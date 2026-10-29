import json

from braces.views import GroupRequiredMixin
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Q
from django.http import HttpResponse, JsonResponse
from django.urls import reverse, reverse_lazy
from django.views.generic import FormView, TemplateView
from fuzzywuzzy import fuzz

from student_registration.backends.utils import download_file, is_valid_filename
from student_registration.child.models import Child
from student_registration.students.models import Nationality
from student_registration.students.utils import generate_one_unique_id
from student_registration.mscc.models import Registration, Referral
from student_registration.tls.templatetags.simple_tags import education_history_model, get_education_service_history
from student_registration.users.templatetags.custom_tags import has_group
from .forms import ReferralForm
from student_registration.outreach.models import OutreachChild
from .utils import get_outreach_child, get_old_child

def main_mark_delete_view(request, pk):
    if request.user.is_authenticated:
        try:
            registration = Registration.objects.get(id=pk, type='TLS')
            registration.deleted = True
            registration.deleted_by = request.user
            registration.save()
            result = {"isSuccessful": True}
        except Registration.DoesNotExist:
            result = {"isSuccessful": False}
    else:
        result = {"isSuccessful": False}
    return JsonResponse(result)

def outreach_child_search(request):

    birthday_year = request.GET.get('birthday_year')
    birthday_month = request.GET.get('birthday_month')
    birthday_day = request.GET.get('birthday_day')
    first_name = request.GET.get('first_name')
    father_name = request.GET.get('father_name')
    last_name = request.GET.get('last_name')

    form_str = '{} {} {}'.format(first_name, father_name, last_name)
    filtered_results = OutreachChild.objects.filter(
        birthday_year=birthday_year
    )

    if birthday_month:
        filtered_results = filtered_results.filter(
            birthday_month=birthday_month
        )
    if birthday_day:
        filtered_results = filtered_results.filter(
            birthday_day=birthday_day
        )

    filtered_results = filtered_results.values(
        'id',
        'first_name',
        'outreach_caregiver__father_name',
        'outreach_caregiver__last_name',
        'outreach_caregiver__mother_full_name',
        'gender',
        'nationality',
        'date_of_birth',
        'birthday_year',
        'birthday_month',
        'birthday_day',
    ).distinct()

    result_match = []
    for result in filtered_results:
        result_str = '{} {} {}'.format(result['first_name'], result['outreach_caregiver__father_name'],
                                       result['outreach_caregiver__last_name'])
        fuzzy_match = fuzz.ratio(form_str, result_str)
        if fuzzy_match > 80:
            result['score'] = fuzzy_match
            result_match.append(result)

    if filtered_results != '':
        return JsonResponse({'result': result_match})

    return JsonResponse({'result': []})

def outreach_child(request):

    outreach_id = request.GET.get('outreach_id')
    result = get_outreach_child(outreach_id)
    return JsonResponse(result)

class ReferralFormView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       FormView):
    template_name = 'tls/referral_form.html'
    form_class = ReferralForm
    success_url = reverse_lazy('tls:list')
    group_required = [u"TLS", u"TLS_CENTER"]

    def get_success_url(self):
        return reverse('tls:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(ReferralFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return ReferralForm(self.request.POST, pk=pk, registry=registry, request=self.request)
        else:
            if pk:
                instance = Referral.objects.get(id=pk)

                return ReferralForm(instance=instance, registry=registry, pk=pk, request=self.request)
            return ReferralForm(registry=registry, pk=pk, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(ReferralFormView, self).form_valid(form)

def public_school_lookup(request):
    from student_registration.schools.models import PublicSchool

    if not request.user.is_authenticated:
        return JsonResponse({'name': ''}, status=403)
    cerd = request.GET.get('cerd', '')
    if not cerd.isdigit() or len(cerd) > 6:
        return JsonResponse({'name': ''})
    school = PublicSchool.objects.filter(cerd=int(cerd)).only('name').first()
    return JsonResponse({'name': school.name if school else ''})

def old_child_search(request):
    birthday_year = request.GET.get('birthday_year')
    birthday_month = request.GET.get('birthday_month')
    birthday_day = request.GET.get('birthday_day')
    first_name = request.GET.get('first_name')
    father_name = request.GET.get('father_name')
    last_name = request.GET.get('last_name')

    if not birthday_year or not first_name or not father_name or not last_name:
        return JsonResponse({'result': []})

    form_str = '{} {} {}'.format(first_name, father_name, last_name)

    active_child_ids = Registration.objects.filter(
        deleted=False, type='TLS',
        child_id__isnull=False,
    ).values_list('child_id', flat=True)

    filtered_results = Child.objects.filter(
        birthday_year=birthday_year
    ).filter(
        id__in=active_child_ids
    )

    if birthday_month:
        filtered_results = filtered_results.filter(
            birthday_month=birthday_month
        )

    if birthday_day:
        filtered_results = filtered_results.filter(
            birthday_day=birthday_day
        )

    filtered_results = filtered_results.values(
        'id',
        'first_name',
        'father_name',
        'last_name',
        'mother_fullname',
        'gender',
        'nationality__name',
        'birthday_year',
        'birthday_month',
        'birthday_day',
    ).distinct()

    result_match = []
    for result in filtered_results:
        result_str = '{} {} {}'.format(result['first_name'], result['father_name'], result['last_name'])
        fuzzy_match = fuzz.ratio(form_str, result_str)
        if fuzzy_match <= 80:
            continue

        result['score'] = fuzzy_match
        education_services = get_education_service_history(result['id'])
        education_service_history = []
        if education_services:
            education_service_history = list(
                education_services.select_related('registration__center', 'round')
                    .order_by('-id')
                    .values(
                    'id',
                    'education_program',
                    'registration__type',
                    'registration_date',
                    'class_section',
                    'registration__center__name',
                    'round__name',
                )
            )

        latest_registration_id = (
            Registration.objects.filter(child_id=result['id'], deleted=False, type='TLS')
            .order_by('-registration_date', '-id')
            .values_list('id', flat=True)
            .first()
        )

        result_match.append({
            'child': result,
            'education_service_history': education_service_history,
            'latest_registration_id': latest_registration_id,
        })

    return JsonResponse({'result': result_match})

def old_child_data(request):

    student_id = request.GET.get('student_id')
    result = get_old_child(student_id)
    return JsonResponse(result)

def child_duplication_check(request):
    body_unicode = request.body.decode('utf-8')
    if body_unicode:
        body = json.loads(body_unicode)

        birthday_year = body.get('birthday_year')
        birthday_month = body.get('birthday_month')
        birthday_day = body.get('birthday_day')
        first_name = body.get('first_name')
        father_name = body.get('father_name')
        last_name = body.get('last_name')
        mother_fullname = body.get('mother_fullname')
        sex = body.get('sex')
        nationality_id = body.get('nationality')
        registration_id = body.get('registration_id')

        try:
            nationality = Nationality.objects.get(id=nationality_id).name_en
        except Nationality.DoesNotExist:
            nationality = ''

        birthdate = '{0}-{1}-{2}'.format(birthday_year, birthday_month, birthday_day)
        unicef_id = generate_one_unique_id(
            '0',
            first_name,
            father_name,
            last_name,
            mother_fullname,
            birthdate,
            nationality,
            sex
        )

        if unicef_id:
            qs = Registration.objects.filter(
                child__unicef_id=unicef_id,
                deleted=False, type='TLS'
            )
            if registration_id:
                qs = qs.exclude(pk=registration_id)
            qs = qs.values('id', 'center__name')
            return JsonResponse({'result': list(qs)})

    return JsonResponse({'result': []})

def quick_search(request):
    from django.db.models.functions import Concat
    from django.db.models import Value

    term = request.GET.get('term', 0).strip()
    terms = request.GET.get('term', 0).strip()
    qs = {}

    if terms:
        user = request.user
        if user.is_authenticated:
            center_id = user.center_id
            partner_id = user.partner_id

            if has_group(user, 'TLS_UNICEF'):
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False, type='TLS'
                ).order_by('-id')
            elif has_group(user, 'TLS_PARTNER') and partner_id:
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False, type='TLS', partner=partner_id
                ).order_by('-id')
            elif has_group(user, 'TLS_CENTER') and center_id:
                qs= Registration.objects.filter(
                    Q(round__isnull=True) | Q(round__current_year=True),
                    deleted=False, type='TLS', center=center_id
                ).order_by('-id')
            else:
                qs = Registration.objects.none()

            if len(terms.split()) > 1:
                qs = qs.annotate(fullname=Concat('child__first_name', Value(' '), 'child__father_name',
                                                 Value(' '), 'child__last_name')) \
                    .filter(fullname__icontains=terms) \
                    .values('id', 'child__first_name', 'child__last_name',
                            'child__father_name', 'child__mother_fullname').distinct()

            else:
                # for term in terms:
                qs = qs.filter(
                    Q(child__first_name__icontains=term) |
                    Q(child__last_name__icontains=term))\
                    .values('id', 'child__first_name', 'child__last_name',
                            'child__father_name', 'child__mother_fullname').distinct()
        else:
            return JsonResponse({'error': 'User not authenticated'}, status=401)

    return JsonResponse({'result': json.dumps(list(qs))})

class ProgrammeDetails(LoginRequiredMixin,
                       TemplateView):

    template_name = 'tls/programme_details.html'

    def get_context_data(self, **kwargs):

        programme_id = self.request.GET.get('programme_id')
        programme_type = self.request.GET.get('programme_type')

        instance = education_history_model(programme_id, programme_type)

        return {
            'instance': instance,
            'programme_type': programme_type
        }

class ChildProfilePreview(LoginRequiredMixin, TemplateView):
    template_name = 'tls/child_profile_preview.html'

    def get_context_data(self, **kwargs):
        context = super(ChildProfilePreview, self).get_context_data(**kwargs)

        registry_id = self.request.GET.get('registry_id')

        if not registry_id:
            context['error'] = 'No id provided.'
            return context

        try:
            instance = Registration.objects.get(id=registry_id, type='TLS')
        except Registration.DoesNotExist:
            context['error'] = 'Registration with id' + str(registry_id) + ' not found.'
            return context
        except ValueError:
            context['error'] = 'Invalid registry_id ' + str(registry_id)
            return context

        context['instance'] = instance
        return context

@login_required(login_url='/users/login')
def get_file(request, file_name):
    if is_valid_filename(file_name, 'zip'):
        return download_file(file_name, 'output_file.zip')
    return HttpResponse("Invalid file.")

@login_required(login_url='/users/login')
def get_file_csv(request, file_name):
    if is_valid_filename(file_name, 'csv'):
        return download_file(file_name, 'exported_data.csv', content_type='text/csv')
    return HttpResponse("Invalid file.", status=400)
