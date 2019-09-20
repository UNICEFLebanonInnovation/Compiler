from django.shortcuts import render
from django_tables2 import MultiTableMixin, RequestConfig, SingleTableView
from django_tables2.export.views import ExportMixin
from django.views.generic import FormView
from django.utils.translation import ugettext as _
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from student_registration.staffenroll.filters import StaffEnrollFilter
from student_registration.staffenroll.models import StaffEnroll
from .tables import BootstrapTable, StaffEnrollTable
from student_registration.users.utils import force_default_language
from .models import EducationYear



class ListingView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  StaffEnrollFilter,
                  ExportMixin,
                  SingleTableView,
                  RequestConfig):

    table_class = StaffEnrollTable
    model = StaffEnroll
    template_name = 'staffenroll/list.html'
    table = BootstrapTable(StaffEnroll.objects.all(), order_by='id')
    filterset_class = StaffEnrollFilter
    group_required = [u"SCHOOL"]

    def get_queryset(self):
        force_default_language(self.request)
        education_year = EducationYear.objects.get(current_year=True)
        return StaffEnroll.objects.exclude(deleted=False).filter(
            education_year=education_year,
            school=self.request.user.school_id
        )


class AddView(LoginRequiredMixin,
              GroupRequiredMixin,
              FormView):

    template_name = 'bootstrap4/common_form.html'
    #`form_class = StaffEnrollForm
    success_url = '/staffenroll/list/'
    group_required = [u"ENROL_CREATE"]

    def get_success_url(self):
        if self.request.POST.get('save_add_another', None):
            return '/staffenroll/add/'
        return self.success_url

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        return super(AddView, self).get_context_data(**kwargs)



    # def get_form(self, form_class=None):
    #     if self.request.method == "POST":
    #         return EnrollmentForm(self.request.POST, request=self.request)
    #     else:
    #         return EnrollmentForm(self.get_initial())

    def form_valid(self, form):
        if self.request.FILES and self.request.FILES['student_std_image']:
            self.request.std_image = self.request.FILES['student_std_image']
        form.save(self.request)
        return super(AddView, self).form_valid(form)
