from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^enrollment/$',
        view=views.EnrollmentView.as_view(),
        name='enrollment'
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
        regex=r'^enrollment/enrollment-export-by-school/$',
        view=views.ExportBySchoolView.as_view(),
        name='enrollment_export_by_school'
    ),
]
