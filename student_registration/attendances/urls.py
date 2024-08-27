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
    url(
        regex=r'^main-attendance/$',
        view=views.MainAttendanceCreateView.as_view(),
        name='main_attendance'
    ),
    url(
        regex=r'^main-attendance-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.MainAttendanceUpdateView.as_view(),
        name='main_attendance_edit'
    ),
    url(
        regex=r'^attendance-absence/$',
        view=views.AttendanceAbsenceView.as_view(),
        name='attendance_absence'
    ),

    url(
        regex=r'^absence-export/(?P<number_of_absences>[\w.@+-]+)/(?P<total_days>[\w.@+-]+)/$',
        view=views.absence_export,
        name='absence_export'
    ),

    url(
        regex=r'^attendance-export/(?P<month>[\w.@+-]+)/(?P<year>[\w.@+-]+)/$',
        view=views.attendance_export,
        name='attendance_export'
    ),
    url(
        regex=r'^total-attendance-export/$',
        view=views.total_attendance_export,
        name='total_attendance_export'
    ),
    url(
        regex=r'^consecutive-attendance-export/$',
        view=views.consecutive_absence_export,
        name='consecutive_attendance_export'
    ),
]
