from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^files-list/$',
        view=views.ExporterListView.as_view(),
        name='files_list'
    ),
    url(
        regex=r'^generate-child-unique-id/$',
        view=views.generate_child_unique_id,
        name='generate_child_id'
    ),
    url(
        regex=r'^generate-all-child-unique-id/$',
        view=views.generate_all_child_unique_id,
        name='generate_all_child_unique_id'
    ),
    url(
        regex=r'^generate-student-unique-id/$',
        view=views.generate_student_unique_id,
        name='generate_student_id'
    ),

]
