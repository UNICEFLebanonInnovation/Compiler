# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse

from .models import Outreach
from student_registration.students.models import (
    Student,
    School,
    Language,
    EducationLevel,
    ClassLevel,
    Location,
    Nationality,
    PartnerOrganization
)


class OutreachView(LoginRequiredMixin, ListView):
    model = Outreach

    def get_context_data(self, **kwargs):
        return {
            'outreaches': self.model.objects.all(),
            'schools': School.objects.all(),
            'languages': Language.objects.all(),
            'education_levels': EducationLevel.objects.all(),
            'levels': ClassLevel.objects.all(),
            'locations': Location.objects.all(),
            'nationalities': Nationality.objects.all(),
            'partners': PartnerOrganization.objects.all(),
            'distances': (u'<= 2.5km', u'> 2.5km', u'> 10km'),
            'genders': (u'Male', u'Female'),
        }


class OutreachNewLineView(LoginRequiredMixin, ListView):
    model = Outreach
    template_name = 'alp/outreach_new_line.html'

    def get_context_data(self, **kwargs):
        p = Outreach(exam_year="2016", exam_month=6, exam_day=5)
        p.save(force_insert=True)

        return {
            'splitter': '##',
            'outreach': p,
            'schools': School.objects.all(),
            'languages': Language.objects.all(),
            'education_levels': EducationLevel.objects.all(),
            'levels': ClassLevel.objects.all(),
            'locations': Location.objects.all(),
            'nationalities': Nationality.objects.all(),
            'partners': PartnerOrganization.objects.all(),
            'distances': (u'<= 2.5km', u'> 2.5km', u'> 10km'),
            'genders': (u'Male', u'Female'),
        }

    def delete(self, request, *args, **kwargs):
        instance = Outreach.objects.get(id=request.body)
        instance.delete()
        return JsonResponse({'result': 'OK'})

    def post(self, request, *args, **kwargs):
        instance = Outreach.objects.get(id=request.POST.get('id'))

        instance.exam_month = request.POST.get('exam_month')
        instance.exam_day = request.POST.get('exam_day')
        instance.average_distance = request.POST.get('average_distance')
        instance.last_education_year = request.POST.get('last_education_year')

        student, created = Student.objects.update_or_create(
            full_name=request.POST.get('student_full_name'),
            mother_fullname=request.POST.get('student_mother_fullname'),
            phone=request.POST.get('student_phone'),
            id_number=request.POST.get('student_id_number'),
            address=request.POST.get('student_address'),
            sex=request.POST.get('student_sex'),
            birthday_year=request.POST.get('student_birthday_year'),
            birthday_month=request.POST.get('student_birthday_month'),
            birthday_day=request.POST.get('student_birthday_day'),
            nationality=(Nationality.objects.get(id=request.POST.get('student_nationality')) if request.POST.get('student_nationality') else None)
        )
        student.save()
        instance.student = student

        if request.POST.get('school'):
            instance.school = School.objects.get(id=request.POST.get('school'))
        if request.POST.get('preferred_language'):
            instance.preferred_language = Language.objects.get(id=request.POST.get('preferred_language'))
        if request.POST.get('last_class_level'):
            instance.last_class_level = ClassLevel.objects.get(id=request.POST.get('last_class_level'))
        if request.POST.get('last_education_level'):
            instance.last_education_level = EducationLevel.objects.get(id=request.POST.get('last_education_level'))
        if request.POST.get('location'):
            instance.location = Location.objects.get(id=request.POST.get('location'))
        if request.POST.get('partner'):
            instance.partner = PartnerOrganization.objects.get(id=request.POST.get('partner'))

        instance.save()
        return JsonResponse({'result': 'OK'})


class OutreachListJson(LoginRequiredMixin, BaseDatatableView):
    model = Outreach

    columns = ['id', 'school_number', 'school', 'exam_year', 'exam_month', 'exam_day', 'average_distance',
               'preferred_language', 'last_education_level', 'last_education_year', 'last_class_level',
               'student_address', 'location', 'student_phone', 'student_id_number', 'student_sex',
               'student_birth_year', 'student_birth_month', 'student_birth_day', 'student_nationality',
               'student_mother_name', 'student_fullname', 'student_id', 'partner']

    order_columns = columns

    max_display_length = 500

    def render_column(self, row, column):
        if column == 'full_name':
            return '{0} {1} {2}'.format(row.first_name, row.father_name, row.last_name)
        elif column == 'birthday_year':
            return '{0}/{1}/{2}'.format(row.birthday_day, row.birthday_month, row.birthday_year)
        else:
            return super(StudentListJson, self).render_column(row, column)

    def filter_queryset(self, qs):
        # use parameters passed in GET request to filter queryset

        # simple example:
        search = self.request.GET.get(u'search[value]', None)
        if search:
            qs = qs.filter(name__istartswith=search)

        return qs


# def save_row(request):
#     HttpRequest.is_ajax()

# from django.http import JsonResponse
# response = JsonResponse({'foo': 'bar'})
# response.content
