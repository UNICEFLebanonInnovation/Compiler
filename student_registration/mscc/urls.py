from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^add-child/$',
        view=views.MainAddView.as_view(),
        name='add_child'
    ),
    url(
        regex=r'^edit-child/(?P<pk>[\w.@+-]+)/$',
        view=views.MainEditView.as_view(),
        name='edit_child'
    ),
    # url(
    #     regex=r'^export/$',
    #     view=views.ExportViewSet.as_view(),
    #     name='export'
    # ),
    url(
        regex=r'^list/$',
        view=views.MainListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^education-situation/(?P<pk>[\w.@+-]+)/$',
        view=views.EducationSituationView.as_view(),
        name='education_situation'
    ),
    url(
        regex=r'^diagnostic-assessment/(?P<pk>[\w.@+-]+)/$',
        view=views.DiagnosticAssessmentView.as_view(),
        name='diagnostic_assessment'
    ),
    url(
        regex=r'^education-assessment/(?P<pk>[\w.@+-]+)/$',
        view=views.EducationAssessmentView.as_view(),
        name='education_assessment'
    ),
    url(
        regex=r'^child-profile/(?P<pk>[\w.@+-]+)/$',
        view=views.ProfileView.as_view(),
        name='view_child'
    ),


]
