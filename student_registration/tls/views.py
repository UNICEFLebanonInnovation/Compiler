from django.urls import reverse, reverse_lazy

from student_registration.mscc.education_view import EducationServiceFormView as MSCCEducationServiceFormView
from student_registration.mscc.views import MainAddView as MSCCMainAddView
from student_registration.mscc.views import MainEditView as MSCCMainEditView
from student_registration.mscc.views import MainListView as MSCCMainListView
from student_registration.mscc.views import ProfileView as MSCCProfileView

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
