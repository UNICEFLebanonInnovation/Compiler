from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^attendance/$',
        view=views.AttendanceView.as_view(),
        name='attendance'
    ),
    url(
        regex=r'^attendance-alp/$',
        view=views.AttendanceALPView.as_view(),
        name='attendance_alp'
    ),
    url(
        regex=r'^export/$',
        view=views.ExportView.as_view(),
        name='export'
    ),
    url(
        regex=r'^absents/$',
        view=views.AbsenteeView.as_view(),
        name='absents'
    ),
]
