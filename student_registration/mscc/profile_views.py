import mimetypes

from braces.views import GroupRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import FileResponse, Http404, HttpResponseForbidden
from django.urls import reverse_lazy
from django.views.generic import DetailView, UpdateView

from student_registration.users.templatetags.custom_tags import has_group
from .models import Registration
from .profile_forms import ProfilePictureForm


class ProfileRegistrationMixin(LoginRequiredMixin, GroupRequiredMixin):
    model = Registration
    group_required = [u"MSCC"]

    def get_queryset(self):
        user = self.request.user
        qs = Registration.objects.filter(deleted=False).select_related(
            'child', 'child__nationality', 'child__disability',
            'round', 'partner', 'center', 'center__governorate',
        )
        if has_group(user, 'MSCC_UNICEF') or (
                user.partner and user.partner.is_world_learning):
            return qs
        if has_group(user, 'MSCC_PARTNER') and user.partner_id:
            return qs.filter(partner_id=user.partner_id)
        if has_group(user, 'MSCC_CENTER') and user.center_id:
            return qs.filter(center_id=user.center_id)
        return qs.none()


class ProfilePictureView(ProfileRegistrationMixin, UpdateView):
    form_class = ProfilePictureForm
    template_name = 'mscc/profile_picture.html'
    success_url = reverse_lazy('mscc:list')

    def dispatch(self, request, *args, **kwargs):
        if (request.method == 'POST' and request.user.is_authenticated
                and request.user.partner and request.user.partner.is_world_learning):
            return HttpResponseForbidden()
        return super().dispatch(request, *args, **kwargs)

    def form_valid(self, form):
        form.instance.modified_by = self.request.user
        return super().form_valid(form)


class ProfilePictureFileView(ProfileRegistrationMixin, DetailView):
    def get(self, request, *args, **kwargs):
        registration = self.get_object()
        if not registration.profile_picture:
            raise Http404("Profile picture not found")
        return FileResponse(
            registration.profile_picture.open('rb'),
            content_type=mimetypes.guess_type(registration.profile_picture.name)[0]
            or 'application/octet-stream',
        )


def registration_profile_id_card(registration):
    child = registration.child
    birthday = ''
    if child:
        parts = [str(getattr(child, 'birthday_' + part) or '').strip()
                 for part in ('day', 'month', 'year')]
        if all(part and part != '0' for part in parts):
            birthday = '{}/{}/{}'.format(parts[0], parts[1], parts[2][-2:])
    nationality = child.nationality if child else None
    disability = child.disability if child else None
    governorate = registration.center.governorate if registration.center else None
    return {
        'round': registration.round.name if registration.round else '',
        'id': registration.pk,
        'ngo': registration.partner.name if registration.partner else '',
        'full_name': registration.child_fullname,
        'birthday': birthday,
        'place_of_birth': getattr(child, 'place_of_birth', '') or '',
        'nationality': (nationality.name_en or nationality.name) if nationality else '',
        'governorate': (governorate.name_en or governorate.name) if governorate else '',
        'physical_difficulties': (disability.name_en or disability.name) if disability else 'No',
        'has_picture': bool(registration.profile_picture),
    }


class ProfileIdView(ProfileRegistrationMixin, DetailView):
    template_name = 'mscc/profile_id.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['card'] = registration_profile_id_card(self.object)
        return context
