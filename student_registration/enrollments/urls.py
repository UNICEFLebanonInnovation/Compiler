from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^enrollment/$',
        view=views.EnrollmentView.as_view(),
        name='enrollment'
    ),
    # url(
    #     regex=r'^enrollment-edit/$',
    #     view=views.EnrollmentEditView.as_view(),
    #     name='enrollment_edit'
    # ),
    url(
        regex=r'^enrollment-patch/$',
        view=views.EnrollmentPatchView.as_view(),
        name='enrollment_patch'
    ),
    url(
        regex=r'^enrollment-view/$',
        view=views.EnrollmentStaffView.as_view(),
        name='enrollment_view'
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
