from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^mscc-add/$',
        view=mscc_views.MSCCAddView.as_view(),
        name='mscc_add'
    ),
    url(
        regex=r'^mscc-edit/(?P<pk>[\w.@+-]+)/$',
        view=mscc_views.MSCCEditView.as_view(),
        name='mscc_edit'
    ),
    # url(
    #     regex=r'^mscc-export/$',
    #     view=mscc_views.MSCCExportViewSet.as_view(),
    #     name='mscc_export'
    # ),
    url(
        regex=r'^mscc-list/$',
        view=mscc_views.MSCCListView.as_view(),
        name='mscc_list'
    ),
    url(
        regex=r'^education-situation/(?P<pk>[\w.@+-]+)/$',
        view=mscc_views.MSCCEducationSituationView.as_view(),
        name='education_situation'
    ),
    url(
        regex=r'^diagnostic-assessment/(?P<pk>[\w.@+-]+)/$',
        view=mscc_views.DiagnosticAssessmentView.as_view(),
        name='diagnostic_assessment'
    ),
    url(
        regex=r'^education-assessment/(?P<pk>[\w.@+-]+)/$',
        view=mscc_views.EducationAssessmentView.as_view(),
        name='education_assessment'
    ),
    url(
        regex=r'^mscc-youth-list/$',
        view=mscc_views.MSCCYouthListView.as_view(),
        name='mscc_youth_list'
    ),
    url(
        regex=r'^mscc-health-list/$',
        view=mscc_views.MSCCHealthListView.as_view(),
        name='mscc_health_list'
    ),
    url(
        regex=r'^mscc-cp-list/$',
        view=mscc_views.MSCCCPListView.as_view(),
        name='mscc_cp_list'
    ),
    url(
        regex=r'^mscc-view/(?P<pk>[\w.@+-]+)/$',
        view=views.ProfileView.as_view(),
        name='mscc_view'
    ),


]
