from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
<<<<<<< HEAD
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
        regex=r'^enrollment-grading/$',
        view=views.EnrollmentGradingView.as_view(),
        name='enrollment_grading'
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
=======
        regex=r'^add/$',
        view=views.AddView.as_view(),
        name='add'
    ),
    url(
        regex=r'^edit/(?P<pk>[\w.@+-]+)/$',
        view=views.EditView.as_view(),
        name='edit'
    ),
    url(
        regex=r'^moved/(?P<pk>[\w.@+-]+)/(?P<moved>[\w.@+-]+)/$',
        view=views.MovedView.as_view(),
        name='moved'
    ),
    url(
        regex=r'^list/$',
        view=views.ListingView.as_view(),
        name='list'
    ),
    url(
        regex=r'^grading/(?P<pk>[\w.@+-]+)/(?P<term>[\w.@+-]+)/$',
        view=views.GradingView.as_view(),
        name='grading'
    ),
    url(
        regex=r'^export/$',
        view=views.ExportViewSet.as_view(),
        name='export'
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    ),
    url(
        regex=r'^enrollment-export-by-school/$',
        view=views.ExportBySchoolView.as_view(),
        name='enrollment_export_by_school'
    ),
<<<<<<< HEAD

    url(
        regex=r'^enrollment-export-duplicate/$',
        view=views.ExportDuplicatesView.as_view(),
        name='enrollment_export_duplicate'
    ),
=======
    url(
        regex=r'^enrollment-export-by-cycle/$',
        view=views.ExportByCycleView.as_view(),
        name='enrollment_export_by_cycle'
    ),

>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
]
