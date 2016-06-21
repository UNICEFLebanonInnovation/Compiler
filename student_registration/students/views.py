# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django_datatables_view.base_datatable_view import BaseDatatableView
from django.http import HttpResponse, JsonResponse

from .models import Student, School


class SchoolDetailJson(LoginRequiredMixin, DetailView):
    model = School

    def get(self, request, *args, **kwargs):
        instance = School.objects.get(id=request.GET.get('id'))
        return JsonResponse({'result': 'OK', 'number': instance.number})

# class StudentListView(LoginRequiredMixin, ListView):
#     model = Student
#     template_name = 'students/list.html'
#
#     def get_context_data(self, **kwargs):
#         return {
#             'students': []
#         }
#
# class StudentList2View(LoginRequiredMixin, ListView):
#     model = Student
#     query_set = Student.objects.all()
#     template_name = 'students/list2.html'
#
#     def get_context_data(self, **kwargs):
#         return {
#             'students': self.query_set
#         }
#
#
# class StudentListJson(LoginRequiredMixin, BaseDatatableView):
#     model = Student
#
#     columns = ['id', 'full_name', 'mother_fullname'] #, 'nationality', 'birthday_year', 'phone', 'id_number', 'address']
#
#     order_columns = ['id', 'full_name', 'mother_fullname']
#
#     max_display_length = 500
#
#     def filter_queryset(self, qs):
#         # use parameters passed in GET request to filter queryset
#
#         # simple example:
#         search = self.request.GET.get(u'search[value]', None)
#         if search:
#             qs = qs.filter(name__istartswith=search)
#
#         return qs
#
#     def prepare_results(self, qs):
#         # prepare list with output column data
#         # queryset is already paginated here
#         json_data = []
#         for item in qs:
#             json_data.append({
#                 "id": item.id,
#                 "full_name": '{0} {1} {2}'.format(item.first_name, item.father_name, item.last_name),
#                 "mother_fullname": item.mother_fullname
#                 })
#         return json_data
#
#
# class StudentList2Json(LoginRequiredMixin, BaseDatatableView):
#     model = Student
#
#     columns = ['id', 'full_name', 'mother_fullname', 'nationality', 'birthday_year', 'phone', 'id_number', 'address']
#
#     order_columns = columns
#
#     max_display_length = 500
#
#     def render_column(self, row, column):
#         if column == 'full_name':
#             return '{0} {1} {2}'.format(row.first_name, row.father_name, row.last_name)
#         elif column == 'birthday_year':
#             return '{0}/{1}/{2}'.format(row.birthday_day, row.birthday_month, row.birthday_year)
#         else:
#             return super(StudentList2Json, self).render_column(row, column)
#
#     def filter_queryset(self, qs):
#         # use parameters passed in GET request to filter queryset
#
#         # simple example:
#         search = self.request.GET.get(u'search[value]', None)
#         if search:
#             qs = qs.filter(name__istartswith=search)
#
#         return qs
#
