from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views


urlpatterns = [
    url(
        regex=r'^teacher-list/$',
        view=views.TeacherListView.as_view(),
        name='teacher_list'
    ),
    url(
        regex=r'^teacher-add/$',
        view=views.TeacherAddView.as_view(),
        name='teacher_add'
    ),
    url(
        regex=r'^teacher-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.TeacherEditView.as_view(),
        name='teacher_edit'
    ),
    url(
        regex=r'^teacher-export/$',
        view=views.teacher_export_data,
        name='teacher_export'
    ),
    url(
        regex=r'^teacher-delete/(?P<pk>[\w.@+-]+)/$',
        view=views.TeacherDeleteView.as_view(),
        name='teacher_delete'
    ),
]

