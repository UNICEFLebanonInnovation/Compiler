from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^add/$',
        view=views.EnrollmentView.as_view(),
        name='add'
    ),
    url(
        regex=r'^edit/(?P<pk>[\w.@+-]+)/$',
        view=views.EnrollmentEditView.as_view(),
        name='edit'
    ),
    url(
        regex=r'^list/$',
        view=views.EnrollmentListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^grading/(?P<pk>[\w.@+-]+)/(?P<term>[\w.@+-]+)/$',
        view=views.GradingView.as_view(),
        name='grading'
    ),

    url(
        regex=r'^enrollment-patch/$',
        view=views.EnrollmentPatchView.as_view(),
        name='enrollment_patch'
    ),
    url(
        regex=r'^enrollment-grading/$',
        view=views.EnrollmentGradingView.as_view(),
        name='enrollment_grading'
    ),
    url(
        regex=r'^enrollment/export/$',
        view=views.ExportViewSet.as_view(),
        name='enrollment_export'
    ),
    url(
        regex=r'^enrollment-export-by-school/$',
        view=views.ExportBySchoolView.as_view(),
        name='enrollment_export_by_school'
    ),

    url(
        regex=r'^enrollment-export-duplicate/$',
        view=views.ExportDuplicatesView.as_view(),
        name='enrollment_export_duplicate'
    ),

]
