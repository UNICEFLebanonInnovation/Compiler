from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.urls import reverse, reverse_lazy


from student_registration.mscc.education_view import EducationServiceFormView as MSCCEducationServiceFormView
from student_registration.mscc.views import MainAddView as MSCCMainAddView
from student_registration.mscc.views import MainEditView as MSCCMainEditView
from student_registration.mscc.views import MainListView as MSCCMainListView
from student_registration.mscc.views import ProfileView as MSCCProfileView
from student_registration.mscc.tasks import queue_filtered_mscc_export
from student_registration.backends.models import ExportHistory

from .tables import TLSMainTable

TLS_PACKAGE_TYPE = 'TLS'


class TLSAddView(MSCCMainAddView):
    success_url = reverse_lazy('tls:list')

    def get_success_url(self):
        return reverse('tls:child_profile', kwargs={'pk': self.request.session.get('instance_id')})

    def get_initial(self):
        initial = super().get_initial()
        initial['type'] = self.request.GET.get('type') or TLS_PACKAGE_TYPE
        return initial


class TLSEditView(MSCCMainEditView):
    success_url = reverse_lazy('tls:list')

    def get_success_url(self):
        return reverse('tls:child_profile', kwargs={'pk': self.request.session.get('instance_id')})


class TLSListView(MSCCMainListView):
    template_name = 'tls/list.html'
    table_class = TLSMainTable
    package_type_filter = TLS_PACKAGE_TYPE
    exclude_package_type = None


class TLSProfileView(MSCCProfileView):
    template_name = 'tls/profile.html'


class TLSEducationServiceFormView(MSCCEducationServiceFormView):
    success_url = reverse_lazy('tls:list')

    def get_success_url(self):
        return reverse('tls:child_profile', kwargs={'pk': self.kwargs['registry']})

    def _resolve_package_type(self):
        return TLS_PACKAGE_TYPE


@login_required(login_url='/users/login')
def export_list_background(request):
    user = request.user
    nationality = request.GET.get('nationality', '')
    first_name = request.GET.get('first_name', '')
    last_name = request.GET.get('last_name', '')
    father_name = request.GET.get('father_name', '')
    mother_fullname = request.GET.get('mother_fullname', '')
    round = request.GET.get('round', '')
    if not round:
        return JsonResponse({'error': 'Round is not selected. Please select a round before exporting data.'}, status=400)

    export_record = ExportHistory.objects.create(
        export_type='TLS List',
        created_by=user,
        partner_name=user.partner.name if user.partner else ''
    )
    queue_filtered_mscc_export(
        export_record.id,
        nationality,
        first_name,
        last_name,
        father_name,
        mother_fullname,
        round,
    )
    return JsonResponse({'status': 'started', 'export_id': export_record.id})
