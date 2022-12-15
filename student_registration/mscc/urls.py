from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views, education_view, services_view

urlpatterns = [

    url(
        regex=r'^Child-Add/$',
        view=views.MainAddView.as_view(),
        name='child_add'
    ),
    url(
        regex=r'^Child-Edit/(?P<pk>[\w.@+-]+)/$',
        view=views.MainEditView.as_view(),
        name='child_edit'
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
        regex=r'^Services/Education-Service-Add/(?P<registry>[\w.@+-]+)/$',
        view=education_view.EducationServiceFormView.as_view(),
        name='service_education_service_add'
    ),
    url(
        regex=r'^Services/Education-Service-Edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.EducationServiceFormView.as_view(),
        name='service_education_service_edit'
    ),
    url(
        regex=r'^Services/Education-RS-Service-Add/(?P<registry>[\w.@+-]+)/$',
        view=education_view.EducationRSServiceFormView.as_view(),
        name='service_education_rs_service_add'
    ),
    url(
        regex=r'^Services/Education-RS-Service-Edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.EducationRSServiceFormView.as_view(),
        name='service_education_rs_service_edit'
    ),
    url(
        regex=r'^Child-Profile/(?P<pk>[\w.@+-]+)/$',
        view=views.ProfileView.as_view(),
        name='child_profile'
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
    url(
        regex=r'^Services/Digital-Add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.DigitalFormView.as_view(),
        name='service_digital_add'
    ),
    url(
        regex=r'^Services/Digital-Edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.DigitalFormView.as_view(),
        name='service_digital_edit'
    ),
    url(
        regex=r'^Services/Health-Nutrition-Add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.HealthNutritionFormView.as_view(),
        name='service_health_nutrition_add'
    ),
    url(
        regex=r'^Services/Health-Nutrition-Edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.HealthNutritionFormView.as_view(),
        name='service_health_nutrition_edit'
    ),
    url(
        regex=r'^Services/PSS-Add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.PSSFormView.as_view(),
        name='service_pss_add'
    ),
    url(
        regex=r'^Services/PSS-Edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.PSSFormView.as_view(),
        name='service_pss_edit'
    ),

]
