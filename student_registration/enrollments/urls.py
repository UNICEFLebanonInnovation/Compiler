from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
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
        regex=r'^list/$',
        view=views.ListingView.as_view(),
        name='list'
    ),
    url(
        regex=r'^grading/(?P<pk>[\w.@+-]+)/(?P<term>[\w.@+-]+)/$',
        view=views.GradingView.as_view(),
        name='grading'
    ),
    # url(
    #     regex=r'^enrollment-grading/$',
    #     view=views.EnrollmentGradingView.as_view(),
    #     name='enrollment_grading'
    # ),
    url(
        regex=r'^export/$',
        view=views.ExportViewSet.as_view(),
        name='export'
    ),
    url(
        regex=r'^enrollment-export-by-school/$',
        view=views.ExportBySchoolView.as_view(),
        name='enrollment_export_by_school'
    ),

]
