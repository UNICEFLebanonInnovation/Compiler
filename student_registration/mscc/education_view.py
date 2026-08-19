# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from braces.views import GroupRequiredMixin, SuperuserRequiredMixin
from django.urls import reverse
from django.http import Http404

from dal import autocomplete
from student_registration.schools.models import School

from .education_form import *
from .models import Registration, TarlAssessment
from .utils import *


class SchoolAutocomplete(autocomplete.Select2QuerySetView):
    def get_queryset(self):
        qs = School.objects.filter(is_bma=True).order_by('name')
        if self.q:
            qs = qs.filter(name__icontains=self.q)
        return qs


class EducationAssessmentFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'mscc/service_education_assessment_form.html'
    form_class = EducationAssessmentForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(EducationAssessmentFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return EducationAssessmentForm(self.request.POST, instance=instance, registry=registry,
                                           request=self.request)
        else:
            if instance:
                data = to_array(EducationAssessmentForm.Meta.fields, EducationAssessment.objects.get(id=instance))
                if data['post_test_done']:
                    return EducationAssessmentForm(data, registry=registry, instance=instance, request=self.request)
            return EducationAssessmentForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(EducationAssessmentFormView, self).form_valid(form)


class DiagnosticAssessmentFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'mscc/service_diagnostic_assessment_form.html'
    form_class = DiagnosticAssessmentForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(DiagnosticAssessmentFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return DiagnosticAssessmentForm(self.request.POST, instance=instance, registry=registry,
                                           request=self.request)
        else:
            if instance:
                data = to_array(DiagnosticAssessmentForm.Meta.fields, EducationAssessment.objects.get(id=instance))
                return DiagnosticAssessmentForm(data, registry=registry, instance=instance, request=self.request)
            return DiagnosticAssessmentForm(registry=registry, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(DiagnosticAssessmentFormView, self).form_valid(form)


class EducationServiceFormView(LoginRequiredMixin,
                                  GroupRequiredMixin,
                                  FormView):
    template_name = 'mscc/service_education_service_form.html'
    form_class = EducationServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def _resolve_package_type(self):
        package_type = self.kwargs.get('package_type')

        if package_type:
            return package_type

        registry_id = self.kwargs.get('registry')
        if registry_id:
            package_type = (
                Registration.objects.filter(id=registry_id)
                .values_list('type', flat=True)
                .first()
            )

        return package_type or DEFAULT_PACKAGE_TYPE

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['package_type'] = self._resolve_package_type()
        return super(EducationServiceFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        package_type = self._resolve_package_type()
        data = {}
        if self.request.method == "POST":
            return EducationServiceForm(self.request.POST, instance=instance, registry=registry,
                                        package_type=package_type, request=self.request)
        else:
            if instance:
                data = to_array(EducationServiceForm.Meta.fields, EducationService.objects.get(id=instance))
                return EducationServiceForm(data, registry=registry, package_type=package_type, instance=instance, request=self.request)
            return EducationServiceForm(registry=registry, package_type=package_type, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        package_type = self._resolve_package_type()
        form.save(request=self.request, registry=registry, package_type=package_type, instance=instance)
        return super(EducationServiceFormView, self).form_valid(form)


class EducationRSServiceFormView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 FormView):
    template_name = 'mscc/service_education_rs_service_form.html'
    form_class = EducationRSServiceForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        return super(EducationRSServiceFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        pk = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return EducationRSServiceForm(self.request.POST, pk=pk, registry=registry, request=self.request)
        else:
            if pk:
                instance = EducationRSService.objects.get(id=pk)
                return EducationRSServiceForm(instance=instance, registry=registry, pk=pk, request=self.request)
            return EducationRSServiceForm(registry=registry, pk=pk, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, instance=instance)
        return super(EducationRSServiceFormView, self).form_valid(form)


class EducationGradingFormView(LoginRequiredMixin,
                               GroupRequiredMixin,
                               FormView):
    template_name = 'mscc/service_education_grading_form.html'
    form_class = EducationGradingForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['programme_type'] = self.kwargs['programme_type']
        kwargs['pre_post'] = self.kwargs.get('pre_post', 'pre')
        return super(EducationGradingFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs.get('pre_post', 'pre')
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return EducationGradingForm(self.request.POST, instance=instance, registry=registry,
                                        programme_type=programme_type,pre_post=pre_post, request=self.request)
        else:
            if instance:
                grade_data = EducationProgrammeAssessment.objects.get(id=instance)
                if pre_post == 'pre':
                    data = grade_data.pre_test
                if pre_post == 'mid':
                    data = grade_data.mid_test
                if pre_post == 'post':
                    data = grade_data.post_test
                return EducationGradingForm(data, registry=registry, programme_type=programme_type,pre_post=pre_post, instance=instance, request=self.request)
            return EducationGradingForm(registry=registry, programme_type=programme_type, pre_post=pre_post, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs.get('pre_post', 'pre')
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry,  programme_type=programme_type, pre_post=pre_post,
                  instance=instance)
        return super(EducationGradingFormView, self).form_valid(form)


class SummerRSAssessmentFormView(LoginRequiredMixin,
                                 GroupRequiredMixin,
                                 FormView):
    template_name = 'mscc/summer_rs_assessment_form.html'
    form_class = SummerRSAssessmentForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def dispatch(self, request, *args, **kwargs):
        programme_type = self.kwargs.get('programme_type')
        if programme_type not in SUMMER_RS_PROGRAMMES:
            raise Http404("Summer RS assessment is only available for Summer RS programmes.")
        return super(SummerRSAssessmentFormView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['programme_type'] = self.kwargs['programme_type']
        kwargs['pre_post'] = self.kwargs.get('pre_post', 'pre')
        return super(SummerRSAssessmentFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs.get('pre_post', 'pre')
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return SummerRSAssessmentForm(
                self.request.POST,
                instance=instance,
                registry=registry,
                programme_type=programme_type,
                pre_post=pre_post,
                request=self.request
            )

        if instance:
            assessment = EducationProgrammeSummerRSAssessment.objects.get(id=instance)
            data = {
                'pre': assessment.pre_test,
                'post': assessment.post_test,
            }[pre_post]
            return SummerRSAssessmentForm(
                data,
                registry=registry,
                programme_type=programme_type,
                pre_post=pre_post,
                instance=instance,
                request=self.request
            )

        return SummerRSAssessmentForm(
            registry=registry,
            programme_type=programme_type,
            pre_post=pre_post,
            instance=instance,
            request=self.request
        )

    def form_valid(self, form):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs.get('pre_post', 'pre')
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, programme_type=programme_type,
                  pre_post=pre_post, instance=instance)
        return super(SummerRSAssessmentFormView, self).form_valid(form)


class WLBLNAssessmentFormView(LoginRequiredMixin,
                             GroupRequiredMixin,
                             FormView):
    template_name = 'mscc/wl_bln_assessment_form.html'
    form_class = WLBLNAssessmentForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def dispatch(self, request, *args, **kwargs):
        programme_type = self.kwargs.get('programme_type')
        if programme_type not in ["BLN Level 1", "BLN Level 2", "BLN Level 3"]:
            raise Http404("WL BLN assessment is only available for BLN levels.")
        return super(WLBLNAssessmentFormView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['programme_type'] = self.kwargs['programme_type']
        kwargs['pre_post'] = self.kwargs.get('pre_post', 'pre')
        return super(WLBLNAssessmentFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs.get('pre_post', 'pre')
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return WLBLNAssessmentForm(
                self.request.POST,
                instance=instance,
                registry=registry,
                programme_type=programme_type,
                pre_post=pre_post,
                request=self.request
            )

        if instance:
            assessment = EducationProgrammeWLAssessment.objects.get(id=instance)
            data = assessment.pre_test if pre_post == 'pre' else assessment.post_test
            return WLBLNAssessmentForm(
                data,
                registry=registry,
                programme_type=programme_type,
                pre_post=pre_post,
                instance=instance,
                request=self.request
            )

        return WLBLNAssessmentForm(
            registry=registry,
            programme_type=programme_type,
            pre_post=pre_post,
            instance=instance,
            request=self.request
        )

    def form_valid(self, form):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs.get('pre_post', 'pre')
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry, programme_type=programme_type,
                  pre_post=pre_post, instance=instance)
        return super(WLBLNAssessmentFormView, self).form_valid(form)


class TarlGradingFormView(LoginRequiredMixin,
                          GroupRequiredMixin,
                          FormView):
    template_name = 'mscc/service_tarl_grading_form.html'
    form_class = TarlGradingForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def dispatch(self, request, *args, **kwargs):
        programme_type = self.kwargs.get('programme_type')
        allowed_programmes = ["BLN Level 1", "BLN Level 2", "BLN Level 3"]
        center = getattr(getattr(request, 'user', None), 'center', None)
        is_tarl_center = getattr(center, 'is_tarl', None) == "Yes"
        pre_post = self.kwargs.get('pre_post', 'pre')

        allowed_periods = ["pre", "mid", "post"]

        if (programme_type not in allowed_programmes or
                not is_tarl_center or
                pre_post not in allowed_periods):
            raise Http404("TARL grading is not available for this request.")

        return super(TarlGradingFormView, self).dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['programme_type'] = self.kwargs['programme_type']
        kwargs['pre_post'] = self.kwargs.get('pre_post', 'pre')
        return super(TarlGradingFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs.get('pre_post', 'pre')
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None

        if self.request.method == "POST":
            return TarlGradingForm(self.request.POST, instance=instance, registry=registry,
                                   programme_type=programme_type, pre_post=pre_post, request=self.request)
        else:
            if instance:
                assessment = TarlAssessment.objects.get(id=instance)
                stage_data = getattr(assessment, f"{pre_post}_test", {}) or {}
                stage_data['programme_type'] = assessment.programme_type
                return TarlGradingForm(stage_data, registry=registry, programme_type=programme_type,
                                       pre_post=pre_post,
                                       instance=instance, request=self.request)
            return TarlGradingForm(registry=registry, programme_type=programme_type, instance=instance,
                                   pre_post=pre_post, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        pre_post = self.kwargs.get('pre_post', 'pre')
        form.save(request=self.request, registry=registry, programme_type=programme_type,
                  instance=instance, pre_post=pre_post)
        return super(TarlGradingFormView, self).form_valid(form)


class YouthScoringFormView(LoginRequiredMixin,
                           GroupRequiredMixin,
                           FormView):
    template_name = 'mscc/service_youth_scoring_form.html'
    form_class = YouthScoringForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['programme_type'] = self.kwargs['programme_type']
        kwargs['pre_post'] = self.kwargs['pre_post'] if 'pre_post' in self.kwargs else 'pre'
        return super(YouthScoringFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs['pre_post'] if 'pre_post' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        data = {}
        if self.request.method == "POST":
            return YouthScoringForm(self.request.POST, instance=instance, registry=registry,
                                    programme_type=programme_type, pre_post=pre_post, request=self.request)
        else:
            if instance:
                grade_data = EducationProgrammeAssessment.objects.get(id=instance)
                if pre_post == 'pre':
                    data = grade_data.youth_pre_test
                if pre_post == 'post':
                    data = grade_data.youth_post_test
                return YouthScoringForm(data, registry=registry, programme_type=programme_type,pre_post=pre_post,
                                        instance=instance, request=self.request)
            return YouthScoringForm(registry=registry, programme_type=programme_type, pre_post=pre_post,
                                    instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        pre_post = self.kwargs['pre_post'] if 'pre_post' in self.kwargs else None
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, registry=registry,  programme_type=programme_type, pre_post=pre_post,
                  instance=instance)
        return super(YouthScoringFormView, self).form_valid(form)


class EducationSchoolGradingFormView(LoginRequiredMixin,
                                     GroupRequiredMixin,
                                     FormView):
    template_name = 'mscc/service_school_grading_form.html'
    form_class = EducationSchoolGradingForm
    success_url = ''
    group_required = [u"MSCC", u"MSCC_CENTER"]

    def get_success_url(self):
        return reverse('mscc:child_profile', kwargs={'pk': self.kwargs['registry']}) + '?current_tab=services'

    def get_context_data(self, **kwargs):
        """Insert the form into the context dict."""
        if 'form' not in kwargs:
            kwargs['form'] = self.get_form()
        kwargs['registry'] = self.kwargs['registry']
        kwargs['programme_type'] = self.kwargs['programme_type']
        return super(EducationSchoolGradingFormView, self).get_context_data(**kwargs)

    def get_form(self, form_class=None):
        registry = self.kwargs['registry']
        programme_type = self.kwargs['programme_type']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        if self.request.method == "POST":
            return EducationSchoolGradingForm(self.request.POST, instance=instance, registry=registry,
                                              programme_type=programme_type, request=self.request)
        else:
            grade_data = EducationProgrammeAssessment.objects.get(id=instance)
            data = grade_data.school_test
            return EducationSchoolGradingForm(data, registry=registry, programme_type=programme_type, instance=instance, request=self.request)

    def form_valid(self, form):
        registry = self.kwargs['registry']
        instance = self.kwargs['pk'] if 'pk' in self.kwargs else None
        form.save(request=self.request, instance=instance)
        return super(EducationSchoolGradingFormView, self).form_valid(form)
