# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse, HttpResponseForbidden
from rest_framework import viewsets, mixins, permissions
from datetime import datetime
import tablib
import json
from rest_framework import status
from django.utils.translation import ugettext as _
from django.db.models import Q
from import_export.formats import base_formats
from braces.views import GroupRequiredMixin

from .models import Outreach, ALPRound
from .serializers import OutreachSerializer, OutreachExamSerializer, OutreachSmallSerializer
from student_registration.students.serializers import StudentSerializer
from student_registration.students.models import (
    Person,
    Student,
    Language,
    Nationality,
    IDType,
)
from student_registration.schools.models import (
    School,
    ClassRoom,
    Grade,
    Section,
    EducationLevel,
    ClassLevel,
    PartnerOrganization
)
from student_registration.locations.models import Location
from student_registration.eav.models import (
    Attribute,
    Value,
)
from student_registration.alp.templatetags.util_tags import has_group


class OutreachViewSet(mixins.RetrieveModelMixin,
                      mixins.ListModelMixin,
                      mixins.CreateModelMixin,
                      mixins.UpdateModelMixin,
                      viewsets.GenericViewSet):

    model = Outreach
    queryset = Outreach.objects.all()
    serializer_class = OutreachSerializer
    permission_classes = (permissions.IsAuthenticated,)

    def get_queryset(self):
        if self.request.method in ["PATCH", "POST", "PUT"]:
            return self.queryset
        terms = self.request.GET.get('term', 0)
        if self.request.user.school_id and terms:
            # todo
            qs = self.queryset.filter(school_id=self.request.user.school_id, alp_round__lt=4)
            for term in terms.split():
                qs = qs.filter(
                    Q(student__first_name__contains=term) |
                    Q(student__father_name__contains=term) |
                    Q(student__last_name__contains=term) |
                    Q(student__id_number__contains=term)
                )
            return qs
        if self.request.GET.get('id', 0):
            return self.queryset.filter(id=self.request.GET.get('id', 0))
        if self.request.user.school_id:
            # todo
            return self.queryset.filter(school_id=self.request.user.school_id, alp_round=4)

    def delete(self, request, *args, **kwargs):
        instance = self.model.objects.get(id=kwargs['pk'])
        instance.delete()
        return JsonResponse({'status': status.HTTP_200_OK})

    def perform_update(self, serializer):
        if has_group(self.request.user, 'CERD') and self.request.method != "PATCH":
            self.serializer_class = OutreachSmallSerializer
        instance = serializer.save()
        instance.save()

    def create(self, request, *args, **kwargs):
        if has_group(self.request.user, 'CERD'):
            self.serializer_class = OutreachSmallSerializer
        return super(OutreachViewSet, self).create(request)

    def update(self, request, *args, **kwargs):
        if has_group(self.request.user, 'CERD') and request.method != "PATCH":
            self.serializer_class = OutreachSmallSerializer
        return super(OutreachViewSet, self).update(request)

    def partial_update(self, request, *args, **kwargs):
        if has_group(self.request.user, 'CERD'):
            self.serializer_class = OutreachExamSerializer
        return super(OutreachViewSet, self).partial_update(request)


class OutreachView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   TemplateView):
    model = Outreach
    template_name = 'alp/index.html'

    group_required = [u"ALP_SCHOOL", u"ALP_DIRECTOR"]

    def handle_no_permission(self, request):
        # return HttpResponseRedirect(reverse("403.html"))
        # return HttpResponseForbidden(reverse("404.html"))
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        data = []
        school = 0
        location = 0
        location_parent = 0
        school_id = int(self.request.GET.get("school", 0))
        alp_round = ALPRound.objects.get(current_round=True)

        if has_group(self.request.user, 'ALP_SCHOOL'):
            school_id = self.request.user.school_id
        if school_id:
            school = School.objects.get(id=school_id)
        if school and school.location:
            location = school.location
        if location and location.parent:
            location_parent = location.parent

        return {
            'data': data,
            'schools': School.objects.all().order_by('name'),
            'languages': Language.objects.all(),
            'locations': Location.objects.filter(type_id=2),
            'partners': PartnerOrganization.objects.all(),
            'distances': (u'<= 2.5km', u'> 2.5km', u'> 10km',),
            'months': Person.MONTHS,
            'genders': Person.GENDER,
            'idtypes': IDType.objects.all(),
            'education_levels': ClassRoom.objects.all(),
            'education_results': Outreach.RESULT,
            'informal_educations': EducationLevel.objects.all(),
            'alp_rounds': ALPRound.objects.all(),
            'education_final_results': ClassLevel.objects.all(),
            'classrooms': ClassRoom.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.exclude(id=5),
            'nationalities2': Nationality.objects.all(),
            'columns': Attribute.objects.filter(type=Outreach.EAV_TYPE),
            'eav_type': Outreach.EAV_TYPE,
            'school_id': school_id,
            'school': school,
            'location': location,
            'location_parent': location_parent,
            'alp_round': alp_round.id,
        }


class CurrentRoundView(LoginRequiredMixin,
                       GroupRequiredMixin,
                       TemplateView):
    model = Outreach
    template_name = 'alp/current.html'

    group_required = [u"ALP_SCHOOL", u"ALP_DIRECTOR"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        data = []
        school = 0
        location = 0
        location_parent = 0
        total = 0
        school_id = int(self.request.GET.get("school", 0))
        round_id = int(self.request.GET.get("round_id", 0))
        if round_id:
            alp_round = ALPRound.objects.get(id=round_id)
        else:
            alp_round = ALPRound.objects.get(current_pre_test=True)

        if has_group(self.request.user, 'ALP_SCHOOL'):
            school_id = self.request.user.school_id
        if school_id:
            school = School.objects.get(id=school_id)
            total = self.model.objects.filter(school_id=school_id, alp_round=alp_round).count()
        if school and school.location:
            location = school.location
        if location and location.parent:
            location_parent = location.parent

        return {
            'data': data,
            'total': total,
            'schools': School.objects.all().order_by('name'),
            'languages': Language.objects.all(),
            'locations': Location.objects.filter(type_id=2),
            'partners': PartnerOrganization.objects.all(),
            'distances': (u'<= 2.5km', u'> 2.5km', u'> 10km',),
            'months': Person.MONTHS,
            'genders': Person.GENDER,
            'idtypes': IDType.objects.all(),
            'education_levels': ClassRoom.objects.all(),
            'education_results': Outreach.RESULT,
            'informal_educations': EducationLevel.objects.all(),
            'alp_rounds': ALPRound.objects.all(),
            'education_final_results': ClassLevel.objects.all(),
            'classrooms': ClassRoom.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.exclude(id=5),
            'nationalities2': Nationality.objects.all(),
            'columns': Attribute.objects.filter(type=Outreach.EAV_TYPE),
            'eav_type': Outreach.EAV_TYPE,
            'school_id': school_id,
            'school': school,
            'location': location,
            'location_parent': location_parent,
            'alp_round': alp_round.id,
        }


class DataCollectingView(LoginRequiredMixin,
                         GroupRequiredMixin,
                         TemplateView):
    model = Outreach
    template_name = 'alp/outreach.html'

    group_required = [u"PARTNER"]

    def handle_no_permission(self, request):
        # return HttpResponseRedirect(reverse("403.html"))
        # return HttpResponseForbidden(reverse("404.html"))
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        data = []
        school = 0
        location = 0
        location_parent = 0
        alp_round = ALPRound.objects.get(current_pre_test=True)

        return {
            'data': data,
            'schools': School.objects.all().order_by('name'),
            'languages': Language.objects.all(),
            'locations': Location.objects.filter(type_id=2),
            'months': Person.MONTHS,
            'genders': Person.GENDER,
            'idtypes': IDType.objects.all(),
            'education_levels': ClassRoom.objects.all(),
            'education_results': Outreach.RESULT,
            'informal_educations': EducationLevel.objects.all(),
            'alp_rounds': ALPRound.objects.all(),
            'education_final_results': ClassLevel.objects.all(),
            'classrooms': ClassRoom.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.exclude(id=5),
            'nationalities2': Nationality.objects.all(),
            'school': school,
            'location': location,
            'location_parent': location_parent,
            'alp_round': alp_round.id
        }


class PreTestView(LoginRequiredMixin,
                  GroupRequiredMixin,
                  TemplateView):
    model = Outreach
    template_name = 'alp/pre_test.html'

    group_required = [u"CERD"]

    def handle_no_permission(self, request):
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        data = []
        school = 0
        location = 0
        location_parent = 0
        school_id = int(self.request.GET.get("school", 0))
        alp_round = ALPRound.objects.get(current_pre_test=True)

        schools = Outreach.objects.filter(
            alp_round=alp_round,
        ).values_list('school_id').order_by('school__number').distinct('school__number')

        data = Outreach.objects.exclude(owner__partner_id=None)
        data = data.filter(school_id=school_id, alp_round=alp_round)

        if school_id:
            school = School.objects.get(id=school_id)
        if school and school.location:
            location = school.location
        if location and location.parent:
            location_parent = location.parent

        return {
            'data': data,
            'schools': School.objects.filter(id__in=schools),
            'months': Person.MONTHS,
            'genders': Person.GENDER,
            'idtypes': IDType.objects.all(),
            'education_levels': ClassRoom.objects.all(),
            'education_results': Outreach.RESULT,
            'informal_educations': EducationLevel.objects.all(),
            'alp_rounds': ALPRound.objects.all(),
            'education_final_results': ClassLevel.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.exclude(id=5),
            'nationalities2': Nationality.objects.all(),
            'selectedSchool': school_id,
            'school': school,
            'location': location,
            'location_parent': location_parent,
            'alp_phase': 'pre_test',
            'alp_round': alp_round.id,
        }


class PostTestView(LoginRequiredMixin,
                   GroupRequiredMixin,
                   TemplateView):
    model = Outreach
    template_name = 'alp/post_test.html'

    group_required = [u"CERD"]

    def handle_no_permission(self, request):
        # return HttpResponseRedirect(reverse("403.html"))
        # return HttpResponseForbidden(reverse("404.html"))
        return HttpResponseForbidden()

    def get_context_data(self, **kwargs):
        data = []
        school = 0
        location = 0
        location_parent = 0
        school_id = int(self.request.GET.get("school", 0))
        alp_round = ALPRound.objects.get(current_post_test=True)

        schools = Outreach.objects.filter(
            alp_round=alp_round,
            registered_in_level__isnull=False
        ).values_list('school_id').order_by('school__number').distinct('school__number')

        if school_id:
            data = Outreach.objects.filter(
                school_id=school_id,
                alp_round=alp_round,
                registered_in_level__isnull=False
            )
            school = School.objects.get(id=school_id)
        if school and school.location:
            location = school.location
        if location and location.parent:
            location_parent = location.parent

        return {
            'data': data,
            'schools': School.objects.filter(id__in=schools),
            'locations': Location.objects.filter(type_id=2),
            'months': Person.MONTHS,
            'genders': Person.GENDER,
            'idtypes': IDType.objects.all(),
            'education_levels': ClassRoom.objects.all(),
            'education_results': Outreach.RESULT,
            'informal_educations': EducationLevel.objects.all(),
            'alp_rounds': ALPRound.objects.all(),
            'education_final_results': ClassLevel.objects.all(),
            'alp_results': ClassLevel.objects.all(),
            'sections': Section.objects.all(),
            'nationalities': Nationality.objects.exclude(id=5),
            'nationalities2': Nationality.objects.all(),
            'selectedSchool': school_id,
            'school': school,
            'location': location,
            'location_parent': location_parent,
            'alp_phase': 'post_test',
        }


class OutreachStaffView(LoginRequiredMixin, TemplateView):
    model = Outreach
    template_name = 'alp/list.html'

    def get_context_data(self, **kwargs):
        data = []
        schools = School.objects.all()

        try:
            school = int(self.request.GET.get("school", 0))
        except Exception as ex:
            school = 0
        try:
            location = int(self.request.GET.get("location", 0))
        except Exception as ex:
            location = 0
        if school:
            data = self.model.objects.filter(school=school).order_by('id')

        return {
            'outreaches': data,
            'locations': Location.objects.filter(type_id=2),
            'schools': schools,
            'selectedSchool': school,
            'selectedLocation': location,
        }


class OutreachExportViewSet(LoginRequiredMixin, ListView):
    model = Outreach

    def get(self, request, *args, **kwargs):
        queryset = self.model.objects.all()
        school = int(request.GET.get('school', 0))
        location = int(request.GET.get('location', 0))
        alp_round = ALPRound.objects.get(current_round=True)

        if has_group(self.request.user, 'PARTNER'):
            alp_round = ALPRound.objects.get(current_pre_test=True)
            queryset = queryset.filter(owner=self.request.user, alp_round=alp_round)
        if has_group(self.request.user, 'ALP_SCHOOL') and self.request.user.school_id:
            school = self.request.user.school_id
        if school:
            queryset = queryset.filter(school_id=school, alp_round=alp_round).order_by('id')
        if location:
            queryset = queryset.filter(school__location_id=location, alp_round=alp_round).order_by('id')

        data = tablib.Dataset()

        data.headers = [
            _('ALP result'),
            _('ALP round'),
            _('ALP level'),
            _('Is the child participated in an ALP program'),

            _('Education year'),
            _('Last education level'),

            _('Phone prefix'),
            _('Phone number'),
            _('Student living address'),

            _('Student ID Number'),
            _('Student ID Type'),
            _('Registered in UNHCR'),

            _('Mother nationality'),
            _('Mother fullname'),

            _('Current Section'),
            _('Current Level'),

            _('Post-test result'),
            _('Assigned to level'),
            _('Pre-test result'),

            _('Student nationality'),
            _('Student age'),
            _('Student birthday'),
            _('Sex'),
            _('Student fullname'),

            _('School'),
            _('School number'),
            _('District'),
            _('Governorate'),
        ]

        content = []
        for line in queryset:
            if not line.student or not line.school:
                continue
            content = [
                line.last_informal_edu_final_result.name if line.last_informal_edu_final_result else '',
                line.last_informal_edu_round.name if line.last_informal_edu_round else '',
                line.last_informal_edu_level.name if line.last_informal_edu_level else '',
                _(line.participated_in_alp) if line.participated_in_alp else '',

                line.last_education_year,
                line.last_education_level.name if line.last_education_level else '',

                line.student.phone_prefix,
                line.student.phone,
                line.student.address,

                line.student.id_number,
                line.student.id_type.name if line.student.id_type else '',
                _(line.registered_in_unhcr) if line.registered_in_unhcr else '',

                line.student.mother_nationality.name if line.student.mother_nationality else '',
                line.student.mother_fullname,

                line.section.name if line.section else '',
                line.registered_in_level.name if line.registered_in_level else '',

                line.post_exam_total,
                line.assigned_to_level.name if line.assigned_to_level else '',
                line.exam_total,

                line.student.nationality_name(),
                line.student.birthday,
                line.student.calc_age,
                _(line.student.sex),
                line.student.__unicode__(),

                line.school.name,
                line.school.number,
                line.school.location.name,
                line.school.location.parent.name,
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/application/ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=outreach_list.xls'
        return response


class ExportBySchoolView(LoginRequiredMixin, ListView):

    model = Outreach
    queryset = Outreach.objects.all()

    def get(self, request, *args, **kwargs):

        alp_round = ALPRound.objects.get(current_pre_test=True)

        schools = self.queryset.filter(alp_round=alp_round, registered_in_level__isnull=False).values_list(
                        'school', 'school__number', 'school__name', 'school__location__name',
                        'school__location__parent__name').distinct().order_by('school__number')

        data = tablib.Dataset()
        data.headers = [
            _('CERD'),
            _('School name'),
            _('# Students'),
            _('District'),
            _('Governorate'),
        ]

        content = []
        for school in schools:
            nbr = self.model.objects.filter(school=school[0], alp_round=alp_round, registered_in_level__isnull=False).count()
            content = [
                school[1],
                school[2],
                nbr,
                school[3],
                school[4]
            ]
            data.append(content)

        file_format = base_formats.XLS()
        response = HttpResponse(
            file_format.export_data(data),
            content_type='application/vnd.ms-excel',
        )
        response['Content-Disposition'] = 'attachment; filename=student_by_school.xls'
        return response
