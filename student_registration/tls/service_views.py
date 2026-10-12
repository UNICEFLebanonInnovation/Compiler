"""TLS endpoints for the shared child service forms."""
from django.urls import reverse

from student_registration.mscc import education_view, services_view
from student_registration.mscc import views as shared_views


class TLSServiceMixin:
    group_required = ['TLS', 'TLS_CENTER', 'TLS_PARTNER', 'TLS_UNICEF']

    def get_success_url(self):
        return reverse('tls:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service_namespace'] = 'tls'
        context['service_base_template'] = 'tls/base.html'
        return context

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        if hasattr(form, 'helper'):
            form.helper.form_action = self.request.path
        for field in form.fields.values():
            widget = field.widget
            if isinstance(getattr(widget, 'url', None), str) and widget.url.startswith('mscc:'):
                widget.url = widget.url.replace('mscc:', 'tls:', 1)
        return form


class TLSDiagnosticAssessmentFormView(TLSServiceMixin, education_view.DiagnosticAssessmentFormView):
    pass


class TLSDigitalFormView(TLSServiceMixin, services_view.DigitalFormView):
    pass


class TLSEducationAssessmentFormView(TLSServiceMixin, education_view.EducationAssessmentFormView):
    pass


class TLSEducationGradingFormView(TLSServiceMixin, education_view.EducationGradingFormView):
    pass


class TLSEducationRSServiceFormView(TLSServiceMixin, education_view.EducationRSServiceFormView):
    pass


class TLSEducationSchoolGradingFormView(TLSServiceMixin, education_view.EducationSchoolGradingFormView):
    pass


class TLSFollowUpFormView(TLSServiceMixin, services_view.FollowUpFormView):
    pass


class TLSFollowUpViewAll(TLSServiceMixin, services_view.FollowUpViewAll):
    pass


class TLSHealthNutritionFormView(TLSServiceMixin, services_view.HealthNutritionFormView):
    pass


class TLSHealthNutritionReferralFormView(TLSServiceMixin, services_view.HealthNutritionReferralFormView):
    pass


class TLSInclusionFormView(TLSServiceMixin, services_view.InclusionFormView):
    pass


class TLSLegoServiceFormView(TLSServiceMixin, services_view.LegoServiceFormView):
    pass


class TLSPSSFormView(TLSServiceMixin, services_view.PSSFormView):
    pass


class TLSRecreationalFormView(TLSServiceMixin, services_view.RecreationalFormView):
    pass


class TLSReferralFormView(TLSServiceMixin, shared_views.ReferralFormView):
    pass


class TLSSummerRSAssessmentFormView(TLSServiceMixin, education_view.SummerRSAssessmentFormView):
    pass


class TLSTarlGradingFormView(TLSServiceMixin, education_view.TarlGradingFormView):
    pass


class TLSWLBLNAssessmentFormView(TLSServiceMixin, education_view.WLBLNAssessmentFormView):
    pass


class TLSYouthAssessmentFormView(TLSServiceMixin, services_view.YouthAssessmentFormView):
    pass


class TLSYouthKitServiceFormView(TLSServiceMixin, services_view.YouthKitServiceFormView):
    pass


class TLSYouthReferralFormView(TLSServiceMixin, services_view.YouthReferralFormView):
    pass


class TLSYouthScoringFormView(TLSServiceMixin, education_view.YouthScoringFormView):
    pass


class TLSYouthServiceGilFormView(TLSServiceMixin, services_view.YouthServiceGilFormView):
    pass


class TLSYouthServiceMaharatiFormView(TLSServiceMixin, services_view.YouthServiceMaharatiFormView):
    pass
