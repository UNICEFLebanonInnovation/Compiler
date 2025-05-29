from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

urlpatterns = [
    re_path(
        regex=r'^attendance/$',
        view=views.AttendanceView.as_view(),
        name='attendance'
    ),
    re_path(
        regex=r'^attendance-alp/$',
        view=views.AttendanceALPView.as_view(),
        name='attendance_alp'
    ),
    re_path(
        regex=r'^export/$',
        view=views.ExportView.as_view(),
        name='export'
    ),
    re_path(
        regex=r'^absents/$',
        view=views.AbsenteeView.as_view(),
        name='absents'
    ),
    re_path(
        regex=r'^main-attendance/$',
        view=views.MainAttendanceCreateView.as_view(),
        name='main_attendance'
    ),
    re_path(
        regex=r'^main-attendance-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.MainAttendanceUpdateView.as_view(),
        name='main_attendance_edit'
    ),
    re_path(
        regex=r'^attendance-absence/$',
        view=views.AttendanceAbsenceView.as_view(),
        name='attendance_absence'
    ),

    re_path(
        regex=r'^absence-export/(?P<number_of_absences>[\w.@+-]+)/(?P<total_days>[\w.@+-]+)/$',
        view=views.absence_export,
        name='absence_export'
    ),

    re_path(
        regex=r'^attendance-export/(?P<month>[\w.@+-]+)/(?P<year>[\w.@+-]+)/$',
        view=views.attendance_export,
        name='attendance_export'
    ),
    re_path(
        regex=r'^total-attendance-export/(?P<round>[\w.@+-]+)/$',
        view=views.total_attendance_export,
        name='total_attendance_export'
    ),
    re_path(
        regex=r'^consecutive-attendance-export/(?P<round>[\w.@+-]+)/$',
        view=views.consecutive_absence_export,
        name='consecutive_attendance_export'
    ),
    re_path(
        regex=r'^mscc-attendance-export/(?P<month>[\w.@+-]+)/(?P<year>[\w.@+-]+)/(?P<education_program>[\w\s.@+-]*)/(?P<class_section>[\w\s.@+-]*)/(?P<partner>[\w\s.@+-]*)/(?P<center>[\w\s.@+-]*)/?$',
        view=views.mscc_attendance_export,
        name='mscc_attendance_export'
    ),
    re_path(
        regex=r'^mscc-total-attendance-export/(?P<month>[\w.@+-]+)/(?P<year>[\w.@+-]+)/(?P<education_program>[\w\s.@+-]*)/(?P<class_section>[\w\s.@+-]*)/(?P<partner>[\w\s.@+-]*)/(?P<center>[\w\s.@+-]*)/?$',
        view=views.mscc_total_attendance_export,
        name='mscc_total_attendance_export'
    ),

]
