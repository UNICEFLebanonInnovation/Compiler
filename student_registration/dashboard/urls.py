from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views
from student_registration.dashboard.secondshift import views as secondshift

urlpatterns = [
    url(
        regex=r'^exporter/$',
        view=views.ExporterView.as_view(),
        name='exporter'
    ),
    url(
        regex=r'^run-exporter/$',
        view=views.RunExporterViewSet.as_view(),
        name='run-exporter'
    ),
    url(
        regex=r'^run-exporter-attendance/$',
        view=views.run_attendance,# RunExporterAttendanceViewSet.as_view(),
        name='run-exporter-attendance'
    ),
    url(
        regex=r'^registrations-alp/$',
        view=views.RegistrationsALPView.as_view(),
        name='registrations-alp'
    ),
    url(
        regex=r'^alp-overall/$',
        view=views.RegistrationsALPOverallView.as_view(),
        name='alp-overall'
    ),
    url(
        regex=r'^registrations-alp-outreach/$',
        view=views.RegistrationsALPOutreachView.as_view(),
        name='registrations-alp-outreach'
    ),
    url(
        regex=r'^registrations-alp-pre-test/$',
        view=views.RegistrationsALPPreTestView.as_view(),
        name='registrations-alp-pre-test'
    ),
    url(
        regex=r'^registrations-alp-post-test/$',
        view=views.RegistrationsALPPostTestView.as_view(),
        name='registrations-alp-post-test'
    ),

    url(
        regex=r'^2ndshift-governorate-grade/$',
        view=secondshift.GovernorateGradeView.as_view(),
        name='2ndshift_governorate_grade'
    ),
    url(
        regex=r'^2ndshift-governorate-age/$',
        view=secondshift.GovernorateAgeView.as_view(),
        name='2ndshift_governorate_age'
    ),
    url(
        regex=r'^2ndshift-governorate-nationality/$',
        view=secondshift.GovernorateNationalityView.as_view(),
        name='2ndshift_governorate_nationality'
    ),
    url(
        regex=r'^2ndshift-grade-age/$',
        view=secondshift.GradeAgeView.as_view(),
        name='2ndshift_grade_age'
    ),
    url(
        regex=r'^2ndshift-grade-nationality/$',
        view=secondshift.GradeNationalityView.as_view(),
        name='2ndshift_grade_nationality'
    ),
    url(
        regex=r'^2ndshift-nationality-age/$',
        view=secondshift.NationalityAgeView.as_view(),
        name='2ndshift_nationality_age'
    ),
    url(
        regex=r'^2ndshift-school-grade/$',
        view=secondshift.SchoolGradeView.as_view(),
        name='2ndshift_school_grade'
    ),
    url(
        regex=r'^2ndshift-school-nationality/$',
        view=secondshift.SchoolNationalityView.as_view(),
        name='2ndshift_school_nationality'
    ),
]
