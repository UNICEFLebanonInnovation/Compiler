# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView

from .models import Outreach


class OutreachView(LoginRequiredMixin, ListView):
    model = Outreach

    def get_context_data(self, **kwargs):
        return {
            'outreaches': []
        }


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
