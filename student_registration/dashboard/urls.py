from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views
from student_registration.dashboard.secondshift import views as secondshift

urlpatterns = [
    url(
        regex=r'^run-filling_data/$',
        view=views.fill_data,
        name='run-filling_data'
    ),
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
        regex=r'^run-to-excel-per-day/$',
        view=views.run_to_excel_per_day,
        name='run-to-excel-per-day'
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
    url(
        regex=r'^update_duplicatestd/$',
        view=views.update_duplicatestd,
        name='update_duplicatestd'
    ),
    url(
        regex=r'^fix_dupstd/$',
        view=views.fix_dupstd,
        name='fix_dupstd'
    ),
    url(
        regex=r'^dup_id_enr/$',
        view=views.dup_id_enr,
        name='dup_id_enr'
    ),
    url(
        regex=r'^dup_nb_enr/$',
        view=views.dup_nb_enr,
        name='dup_nb_enr'
    ),
    url(
        regex=r'^generate_pretest_result/$',
        view=views.generate_pretest_result,
        name='generate_pretest_result'
    ),
    url(
        regex=r'^utilities/$',
        view=views.View_Utilities.as_view(),
        name='utilities'
    ),
    url(
        regex=r'^run-list-justification/$',
        view=views.List_Justification.as_view(),
        name='run-list-justification'
    ),
    url(
        regex=r'^run-generate-justification/$',
        view=views.Generate_Justification_number,
        name='run-generate-justification'
    ),
]
