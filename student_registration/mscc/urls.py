from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views, education_view, services_view

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
        regex=r'^List/$',
        view=views.MainListView.as_view(),
        name='list'
    ),
    url(
        regex=r'^Services/Education-Assessment-Add/(?P<registry>[\w.@+-]+)/$',
        view=education_view.EducationAssessmentFormView.as_view(),
        name='service_education_assessment_add'
    ),
    url(
        regex=r'^Services/Education-Assessment-Edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.EducationAssessmentFormView.as_view(),
        name='service_education_assessment_edit'
    ),
    url(
        regex=r'^Child-Profile/(?P<pk>[\w.@+-]+)/$',
        view=views.ProfileView.as_view(),
        name='view_child'
    ),
    url(
        regex=r'^Services/Inclusion-Add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.InclusionFormView.as_view(),
        name='service_inclusion_add'
    ),
    url(
        regex=r'^Services/Inclusion-Edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.InclusionFormView.as_view(),
        name='service_inclusion_edit'
    ),

]
