from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

app_name = 'backends'

urlpatterns = [

    re_path(
        r'^files-list/$',
        view=views.ExporterListView.as_view(),
        name='files_list'
    ),
    re_path(
        r'^generate-child-unique-id/$',
        view=views.generate_child_unique_id,
        name='generate_child_id'
    ),
    re_path(
        r'^generate-all-child-unique-id/$',
        view=views.generate_all_child_unique_id,
        name='generate_all_child_unique_id'
    ),
    re_path(
        r'^generate-student-unique-id/$',
        view=views.generate_student_unique_id,
        name='generate_student_id'
    ),
    re_path(
        r'^generate-child-cash-programme/$',
        view=views.generate_child_cash_programme,
        name='generate_cash_programme'
    ),

]
