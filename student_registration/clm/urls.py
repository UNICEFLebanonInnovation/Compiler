from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views
# from .views import BLN, CBECE, RS

urlpatterns = [

    url(
        regex=r'^index/$',
        view=views.CLMView.as_view(),
        name='index'
    ),

    url(
        regex=r'^bln-dashboard/$',
        view=views.BLNDashboardView.as_view(),
        name='bln_dashboard'
    ),

    url(
        regex=r'^rs-dashboard/$',
        view=views.RSDashboardView.as_view(),
        name='rs_dashboard'
    ),

    url(
        regex=r'^cbece-dashboard/$',
        view=views.CBECEDashboardView.as_view(),
        name='cbece_dashboard'
    ),

    url(
        regex=r'^bln-add/$',
        view=views.BLNAddView.as_view(),
        name='bln_add'
    ),
    url(
        regex=r'^bln-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.BLNEditView.as_view(),
        name='bln_edit'
    ),
    url(
        regex=r'^bln-export/$',
        view=views.BLNExportViewSet.as_view(),
        name='bln_export'
    ),
    url(
        regex=r'^assessment-submission/$',
        view=views.AssessmentSubmission.as_view(),
        name='assessment_submission'
    ),
    url(
        regex=r'^bln-list/$',
        view=views.BLNListView.as_view(),
        name='bln_list'
    ),

    url(
        regex=r'^rs-add/$',
        view=views.RSAddView.as_view(),
        name='rs_add'
    ),
    url(
        regex=r'^rs-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.RSEditView.as_view(),
        name='rs_edit'
    ),
    url(
        regex=r'^rs-export/$',
        view=views.RSExportViewSet.as_view(),
        name='rs_export'
    ),
    url(
        regex=r'^rs-list/$',
        view=views.RSListView.as_view(),
        name='rs_list'
    ),

    url(
        regex=r'^cbece-add/$',
        view=views.CBECEAddView.as_view(),
        name='cbece_add'
    ),
    url(
        regex=r'^cbece-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.CBECEEditView.as_view(),
        name='cbece_edit'
    ),
    url(
        regex=r'^cbece-export/$',
        view=views.CBECEExportViewSet.as_view(),
        name='cbece_export'
    ),
    url(
        regex=r'^cbece-list/$',
        view=views.CBECEListView.as_view(),
        name='cbece_list'
    ),

    url(
        regex=r'^abln-add/$',
        view=views.ABLNAddView.as_view(),
        name='abln_add'
    ),
    url(
        regex=r'^abln-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.ABLNEditView.as_view(),
        name='abln_edit'
    ),
    url(
        regex=r'^abln-export/$',
        view=views.ABLNExportViewSet.as_view(),
        name='abln_export'
    ),
    url(
        regex=r'^abln-list/$',
        view=views.ABLNListView.as_view(),
        name='abln_list'
    ),

]
