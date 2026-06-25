import codecs
import csv
import io
import threading
import uuid
import zipfile

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.files.base import ContentFile
from django.db import connection
from django.db.models import Count, Exists, IntegerField, OuterRef, Q, Subquery
from django.db.models.functions import Coalesce
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy
from django.utils.encoding import smart_str
from django.views.generic import FormView, TemplateView

from braces.views import GroupRequiredMixin
from django_filters.views import FilterView
from django_tables2 import RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin

from student_registration.attendances.models import MSCCAttendanceChild
from student_registration.backends.models import ExportHistory
from student_registration.backends.utils import ExportStorage
from .education_form import EducationServiceForm
from .filters import FullFilter, MainFilter
from .forms import MainForm
from .models import EducationService, ProvidedServices, Registration, Round
from .serializers import MainSerializer
from .tables import BootstrapTable, FullTable, PartnerTable, TLSMainTable, YouthMainTable
from .utils import DEFAULT_PACKAGE_TYPE, generate_services, to_array
from student_registration.users.templatetags.custom_tags import has_group

TLS_PACKAGE_TYPE = 'TLS'


class TLSProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'tls/profile.html'

    def get_context_data(self, **kwargs):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        generate_services(instance.child.age, instance)
        current_tab = self.request.GET.get('current_tab', 'info')

        rounds_registered = EducationService.objects.filter(
            registration__child_id=instance.child.id,
            registration__deleted=False,
        ).values_list('round_id', flat=True)
        rounds_registered = [r for r in rounds_registered if r is not None]
        available_rounds = Round.objects.filter(current_year=True).exclude(id__in=rounds_registered)
        services = ProvidedServices.objects.filter(registration=instance)
        services_dict = {service.name: service for service in services}
        provide_french_language = getattr(getattr(instance, 'center', None), 'provide_french_language', None) == 'Yes'

        return {
            'instance': instance,
            'new_round': available_rounds.exists(),
            'current_tab': current_tab,
            'provided_services': services_dict,
            'provide_french_language': provide_french_language,
        }


class TLSAddView(LoginRequiredMixin, GroupRequiredMixin, FormView):
    template_name = 'mscc/main_form.html'
    form_class = MainForm
    success_url = reverse_lazy('tls:list')
    group_required = [u'MSCC', u'MSCC_CENTER']

    def get_success_url(self):
        return reverse('tls:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super().get_context_data(**kwargs)

    def get_initial(self):
        initial = super().get_initial()
        initial['type'] = self.request.GET.get('type') or TLS_PACKAGE_TYPE
        return initial

    def form_valid(self, form):
        form.save(self.request)
        return super().form_valid(form)

    def get_form(self, form_class=None):
        if self.request.method == 'POST':
            return MainForm(self.request.POST, instance=None, request=self.request)
        return MainForm(None, instance=None, request=self.request, initial=self.get_initial())


class TLSEditView(LoginRequiredMixin, GroupRequiredMixin, FormView):
    template_name = 'mscc/main_form.html'
    form_class = MainForm
    success_url = reverse_lazy('tls:list')
    group_required = [u'MSCC', u'MSCC_CENTER']

    def get_success_url(self):
        return reverse('tls:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super().get_context_data(**kwargs)

    def get_form(self, form_class=None):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        if self.request.method == 'POST':
            return MainForm(self.request.POST, instance=instance, request=self.request)

        data = MainSerializer(instance).data
        data['child_nationality'] = data['child_nationality_id'] if 'child_nationality_id' in data else ''
        data['child_disability'] = data['child_disability_id'] if 'child_disability_id' in data else ''
        data['main_caregiver_nationality'] = data['main_caregiver_nationality_id'] if 'main_caregiver_nationality_id' in data else ''
        data['father_educational_level'] = data['father_educational_level_id'] if 'father_educational_level_id' in data else ''
        data['mother_educational_level'] = data['mother_educational_level_id'] if 'mother_educational_level_id' in data else ''
        data['id_type'] = data['id_type_id'] if 'id_type_id' in data else ''
        return MainForm(data, instance=instance, request=self.request)

    def form_valid(self, form):
        instance = Registration.objects.get(id=self.kwargs['pk'])
        form.save(request=self.request, instance=instance)
        return super().form_valid(form)


class TLSListView(LoginRequiredMixin, GroupRequiredMixin, FilterView, ExportMixin, SingleTableView, RequestConfig):
    table_class = TLSMainTable
    model = Registration
    template_name = 'tls/list.html'
    table = BootstrapTable(Registration.objects.all(), order_by='id')
    group_required = [u'MSCC']
    filterset_class = MainFilter

    def get_queryset(self):
        user = self.request.user
        center_id = user.center_id
        partner_id = user.partner_id
        is_world_learning = bool(user.partner and user.partner.is_world_learning)

        qs = (Registration.objects
              .select_related(
                  'child', 'child__nationality', 'partner', 'center', 'center__governorate',
                  'center__caza', 'center__cadaster', 'owner', 'modified_by', 'round',
              )
              .prefetch_related('education_service')
              .filter(deleted=False, type=TLS_PACKAGE_TYPE))

        previous_registration = Registration.objects.filter(
            child_id=OuterRef('child_id'),
            created__lt=OuterRef('created'),
        )
        absent_days = (
            MSCCAttendanceChild.objects
            .filter(registration_id=OuterRef('pk'), attended='No')
            .values('registration')
            .annotate(count=Count('id'))
            .values('count')
        )
        qs = qs.annotate(
            has_previous=Exists(previous_registration),
            _total_absent_days=Coalesce(Subquery(absent_days, output_field=IntegerField()), 0),
        )
        round_filter = Q(round__isnull=True) | Q(round__current_year=True)

        if has_group(user, 'MSCC_UNICEF') or is_world_learning:
            return qs.filter(round_filter).order_by('child__first_name', 'child__father_name', 'child__last_name')
        if has_group(user, 'MSCC_PARTNER') and partner_id:
            return qs.filter(round_filter, partner=partner_id).order_by('child__first_name', 'child__father_name', 'child__last_name')
        if has_group(user, 'MSCC_CENTER') and center_id:
            return qs.filter(round_filter, center=center_id).order_by('child__first_name', 'child__father_name', 'child__last_name')
        return Registration.objects.none()

    def get_table_class(self):
        if has_group(self.request.user, 'MSCC_UNICEF'):
            return FullTable
        if has_group(self.request.user, 'MSCC_PARTNER'):
            return PartnerTable
        if has_group(self.request.user, 'MSCC_CENTER'):
            return self.table_class
        if not has_group(self.request.user, 'MSCC_FULL'):
            return YouthMainTable
        return self.table_class

    def get_filterset_class(self):
        if has_group(self.request.user, 'MSCC_UNICEF'):
            return FullFilter
        return self.filterset_class


class TLSEducationServiceFormView(LoginRequiredMixin, GroupRequiredMixin, FormView):
    template_name = 'mscc/service_education_service_form.html'
    form_class = EducationServiceForm
    success_url = reverse_lazy('tls:list')
    group_required = [u'MSCC', u'MSCC_CENTER']

    def _resolve_package_type(self):
        return TLS_PACKAGE_TYPE or DEFAULT_PACKAGE_TYPE

    def get_success_url(self):
        return reverse('tls:child_profile', kwargs={'pk': self.kwargs['registry']})

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['package_type'] = self._resolve_package_type()
        return super().get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        package_type = self._resolve_package_type()
        if self.request.method == 'POST':
            return EducationServiceForm(
                self.request.POST,
                instance=instance,
                registry=registry,
                package_type=package_type,
                request=self.request,
            )
        if instance:
            data = to_array(EducationServiceForm.Meta.fields, EducationService.objects.get(id=instance))
            return EducationServiceForm(data, registry=registry, package_type=package_type, instance=instance, request=self.request)
        return EducationServiceForm(registry=registry, package_type=package_type, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, package_type=self._resolve_package_type(), instance=instance)
        return super().form_valid(form)


def _generate_filtered_tls_export(export_id, round_id=''):
    export = ExportHistory.objects.get(id=export_id)
    try:
        user = export.created_by
        cursor = connection.cursor()
        center_id = user.center_id
        partner_id = user.partner_id or 0
        is_world_learning = bool(user.partner and user.partner.is_world_learning)
        query_params = []

        if not round_id:
            tls_data_query = 'SELECT * FROM vw_mscc_data WHERE id = 0'
        elif round_id == 'no_round':
            tls_data_query = 'SELECT * FROM vw_mscc_wl_data_no_round WHERE id > 0' if is_world_learning else 'SELECT * FROM vw_mscc_data_no_round WHERE id > 0'
        else:
            tls_data_query = 'SELECT * FROM vw_mscc_wl_data WHERE round_id = %s' if is_world_learning else 'SELECT * FROM vw_mscc_data WHERE round_id = %s'
            query_params.append(round_id)

        tls_data_query += ' AND type = %s'
        query_params.append(TLS_PACKAGE_TYPE)

        if has_group(user, 'MSCC_UNICEF') or is_world_learning:
            tls_data_query += ' AND id > 0'
        elif has_group(user, 'MSCC_PARTNER') and partner_id:
            tls_data_query += ' AND partner_id = %s'
            query_params.append(partner_id)
        elif has_group(user, 'MSCC_CENTER') and center_id:
            tls_data_query += ' AND center_id = %s'
            query_params.append(center_id)
        else:
            tls_data_query += ' AND id = 0'

        cursor.execute(tls_data_query, query_params)
        tls_data = cursor.fetchall()
        headers = [col[0] for col in cursor.description]

        zip_output = io.BytesIO()
        with zipfile.ZipFile(zip_output, 'w') as zf:
            csv_tls_output = io.StringIO()
            csv_writer = csv.writer(csv_tls_output)
            csv_tls_output.write(codecs.BOM_UTF8.decode('utf-8'))
            csv_writer.writerow(headers)
            for row in tls_data:
                csv_writer.writerow([smart_str(cell) for cell in row])
            zf.writestr('tls_data.csv', csv_tls_output.getvalue())

            registration_ids = [row[0] for row in tls_data]
            if registration_ids:
                followup_query = 'SELECT * FROM mscc_followupservice WHERE registration_id IN ({})'.format(
                    ','.join(['%s'] * len(registration_ids))
                )
                cursor.execute(followup_query, registration_ids)
                followup_data = cursor.fetchall()
                followup_headers = [col[0] for col in cursor.description]
                csv_followup_output = io.StringIO()
                csv_writer = csv.writer(csv_followup_output)
                csv_followup_output.write(codecs.BOM_UTF8.decode('utf-8'))
                csv_writer.writerow(followup_headers)
                for row in followup_data:
                    csv_writer.writerow([smart_str(cell) for cell in row])
                zf.writestr('followup_data.csv', csv_followup_output.getvalue())

        file_name = f'tls_out_file_{uuid.uuid4()}.zip'
        storage = ExportStorage()
        storage.save(file_name, ContentFile(zip_output.getvalue()))
        export.file_url = reverse('tls:export_download', args=[file_name])
        export.status = 'done'
        export.save()
    except Exception:
        export.status = 'failed'
        export.save()


def queue_filtered_tls_export(export_id, round_id=''):
    thread = threading.Thread(target=_generate_filtered_tls_export, args=(export_id, round_id), daemon=True)
    thread.start()
    return thread


@login_required(login_url='/users/login')
def export_list_background(request):
    user = request.user
    round_id = request.GET.get('round', '')
    if not round_id:
        return JsonResponse({'error': 'Round is not selected. Please select a round before exporting data.'}, status=400)

    export_record = ExportHistory.objects.create(
        export_type='TLS List',
        created_by=user,
        partner_name=user.partner.name if user.partner else '',
    )
    queue_filtered_tls_export(export_record.id, round_id)
    return JsonResponse({'status': 'started', 'export_id': export_record.id})
