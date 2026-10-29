from django.urls import re_path

from .child_views import (
    ChildProfilePreview,
    child_duplication_check,
    get_file,
    main_mark_delete_view,
    old_child_data,
    old_child_search,
    outreach_child,
    outreach_child_search,
)
from . import views, child_views, education_view, services_view, profile_views

app_name = 'tls'

urlpatterns = [
    re_path(r'^child-add/$', view=views.TLSAddView.as_view(), name='child_add'),
    re_path(r'^child-edit/(?P<pk>[\w.@+-]+)/$', view=views.TLSEditView.as_view(), name='child_edit'),
    re_path(r'^child-mark-delete/(?P<pk>[\w.@+-]+)/$', view=main_mark_delete_view, name='child_mark_deleted'),
    re_path(r'^child-profile/(?P<pk>[\w.@+-]+)/$', view=views.TLSProfileView.as_view(), name='child_profile'),
    re_path(r'^list/$', view=views.TLSListView.as_view(), name='list'),
    re_path(r'^export-list-background/$', view=views.export_list_background, name='export_list_background'),
    re_path(r'^export-download/(?P<file_name>.+)/$', view=get_file, name='export_download'),
    re_path(r'^new-round/(?P<pk>[\w.@+-]+)/$', view=views.TLSNewRoundView.as_view(), name='new_round'),
    re_path(r'^new-round-redirect/$', view=views.TLSNewRoundRedirectView.as_view(), name='new_round_redirect'),
    re_path(r'^child-registration-cancel/(?P<pk>[\w.@+-]+)/$', view=views.tls_registration_cancel_view, name='child_registration_cancel'),
    re_path('outreach-child-search/$', outreach_child_search, name='outreach_child_search'),
    re_path('outreach-child/$', outreach_child, name='outreach_child'),
    re_path('old-child-search/$', old_child_search, name='old_child_search'),
    re_path('get-old-child-data/$', old_child_data, name='old_child_data'),
    re_path('child-duplication-check/$', child_duplication_check, name='child_duplication_check'),
    re_path('child-profile-preview/$', view=ChildProfilePreview.as_view(), name='child_profile_preview'),
    re_path(r'^services/education-add/(?P<registry>[\w.@+-]+)/$', view=views.TLSEducationServiceFormView.as_view(), name='service_education_add'),
    re_path(r'^services/education-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$', view=views.TLSEducationServiceFormView.as_view(), name='service_education_edit'),
]


urlpatterns += [
    re_path(r'^profile-ids/$', profile_views.BulkProfileIdView.as_view(), name='profile_id_bulk'),
    re_path(r'^profile-picture/(?P<pk>\d+)/$', profile_views.ProfilePictureView.as_view(), name='profile_picture'),
    re_path(r'^profile-picture/(?P<pk>\d+)/file/$', profile_views.ProfilePictureFileView.as_view(), name='profile_picture_file'),
    re_path(r'^profile-id/(?P<pk>\d+)/$', profile_views.ProfileIdView.as_view(), name='profile_id'),
    re_path(
        r'^public-school-lookup/$',
        view=child_views.public_school_lookup,
        name='public_school_lookup'
    ),
    re_path(
        r'^school-autocomplete/$',
        view=education_view.SchoolAutocomplete.as_view(),
        name='school_autocomplete'
    ),
    re_path(
        r'^services/education-assessment-add/(?P<registry>[\w.@+-]+)/$',
        view=education_view.EducationAssessmentFormView.as_view(),
        name='service_education_assessment_add'
    ),
    re_path(
        r'^services/education-assessment-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.EducationAssessmentFormView.as_view(),
        name='service_education_assessment_edit'
    ),
    re_path(
        r'^services/diagnostic-assessment-add/(?P<registry>[\w.@+-]+)/$',
        view=education_view.DiagnosticAssessmentFormView.as_view(),
        name='service_diagnostic_assessment_add'
    ),
    re_path(
        r'^services/diagnostic-assessment-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.DiagnosticAssessmentFormView.as_view(),
        name='service_diagnostic_assessment_edit'
    ),
    re_path(
        r'^services/rs-add/(?P<registry>[\w.@+-]+)/$',
        view=education_view.EducationRSServiceFormView.as_view(),
        name='service_education_rs_add'
    ),
    re_path(
        r'^services/rs-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.EducationRSServiceFormView.as_view(),
        name='service_education_rs_edit'
    ),
    re_path(
        r'^services/inclusion-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.InclusionFormView.as_view(),
        name='service_inclusion_add'
    ),
    re_path(
        r'^services/inclusion-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.InclusionFormView.as_view(),
        name='service_inclusion_edit'
    ),
    re_path(
        r'^services/digital-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.DigitalFormView.as_view(),
        name='service_digital_add'
    ),
    re_path(
        r'^services/digital-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.DigitalFormView.as_view(),
        name='service_digital_edit'
    ),
    re_path(
        r'^services/health-nutrition-add/(?P<registry>[\w.@+-]+)/(?P<age>[\w.@+-]+)/$',
        view=services_view.HealthNutritionFormView.as_view(),
        name='service_health_nutrition_add'
    ),
    re_path(
        r'^services/health-nutrition-edit/(?P<registry>[\w.@+-]+)/(?P<age>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.HealthNutritionFormView.as_view(),
        name='service_health_nutrition_edit'
    ),
    re_path(
        r'^services/health-nutrition-referral-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.HealthNutritionReferralFormView.as_view(),
        name='service_health_nutrition_referral_add'
    ),
    re_path(
        r'^services/health-nutrition-referral-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.HealthNutritionReferralFormView.as_view(),
        name='service_health_nutrition_referral_edit'
    ),
    re_path(
        r'^services/pss-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.PSSFormView.as_view(),
        name='service_pss_add'
    ),
    re_path(
        r'^services/pss-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.PSSFormView.as_view(),
        name='service_pss_edit'
    ),
    re_path(
        r'^services/youth-kit-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.YouthKitServiceFormView.as_view(),
        name='service_youth_kit_add'
    ),
    re_path(
        r'^services/youth-kit-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.YouthKitServiceFormView.as_view(),
        name='service_youth_kit_edit'
    ),
    re_path(
        r'^services/youth-maharati-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.YouthServiceMaharatiFormView.as_view(),
        name='service_youth_maharati_add'
    ),
    re_path(
        r'^services/youth-maharati-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.YouthServiceMaharatiFormView.as_view(),
        name='service_youth_maharati_edit'
    ),
    re_path(
        r'^services/youth-gil-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.YouthServiceGilFormView.as_view(),
        name='service_youth_gil_add'
    ),
    re_path(
        r'^services/youth-gil-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.YouthServiceGilFormView.as_view(),
        name='service_youth_gil_edit'
    ),
    re_path(
        r'^services/follow-up-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.FollowUpFormView.as_view(),
        name='service_follow_up_add'
    ),
    re_path(
        r'^services/follow-up-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.FollowUpFormView.as_view(),
        name='service_follow_up_edit'
    ),
    re_path(
        r'^services/youth-assessment-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.YouthAssessmentFormView.as_view(),
        name='service_youth_assessment_add'
    ),
    re_path(
        r'^services/youth-assessment-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.YouthAssessmentFormView.as_view(),
        name='service_youth_assessment_edit'
    ),
    re_path(
        r'^services/youth-referral-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.YouthReferralFormView.as_view(),
        name='service_youth_referral_add'
    ),
    re_path(
        r'^services/youth-referral-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.YouthReferralFormView.as_view(),
        name='service_youth_referral_edit'
    ),
    re_path(
        r'^referral-add/(?P<registry>[\w.@+-]+)/$',
        view=child_views.ReferralFormView.as_view(),
        name='referral_add'
    ),
    re_path(
        r'^referral-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=child_views.ReferralFormView.as_view(),
        name='referral_edit'
    ),
    re_path(
        'quick-search/$',
        child_views.quick_search,
        name='quick_search'
    ),
    re_path(
        'find-programme-details/$',
        view=child_views.ProgrammeDetails.as_view(),
        name='find_programme_details'
    ),
    re_path(
        r'^services/follow-up-view-all/(?P<registry>[\w.@+-]+)/$',
        view=services_view.FollowUpViewAll.as_view(),
        name='service_follow_up_view_all'
    ),
    re_path(
        r'^services/education-grading-add/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/$',
        view=education_view.EducationGradingFormView.as_view(),
        name='service_education_grading_add'
    ),
    re_path(
        r'^services/education-grading-edit/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/(?P<pre_post>[\w\s.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.EducationGradingFormView.as_view(),
        name='service_education_grading_edit'
    ),
    re_path(
        r'^services/summer-rs-assessment-add/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/$',
        view=education_view.SummerRSAssessmentFormView.as_view(),
        name='summer_rs_assessment_add'
    ),
    re_path(
        r'^services/summer-rs-assessment-edit/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/(?P<pre_post>pre|post|mid)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.SummerRSAssessmentFormView.as_view(),
        name='summer_rs_assessment_edit'
    ),
    re_path(
        r'^services/wl-bln-assessment-add/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/$',
        view=education_view.WLBLNAssessmentFormView.as_view(),
        name='wl_bln_assessment_add'
    ),
    re_path(
        r'^services/wl-bln-assessment-edit/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/(?P<pre_post>pre|post)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.WLBLNAssessmentFormView.as_view(),
        name='wl_bln_assessment_edit'
    ),
    re_path(
        r'^services/tarl-grading-add/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/(?P<pre_post>pre|post|mid)/$',
        view=education_view.TarlGradingFormView.as_view(),
        name='service_tarl_grading_add'
    ),
    re_path(
        r'^services/tarl-grading-edit/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/(?P<pre_post>pre|post|mid)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.TarlGradingFormView.as_view(),
        name='service_tarl_grading_edit'
    ),
    re_path(
        r'^services/youth-scoring-add/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/$',
        view=education_view.YouthScoringFormView.as_view(),
        name='service_youth_scoring_add'
    ),
    re_path(
        r'^services/youth-scoring-edit/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/(?P<pre_post>[\w\s.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.YouthScoringFormView.as_view(),
        name='service_youth_scoring_edit'
    ),
    re_path(
        r'^services/education-school-grading/(?P<registry>[\w.@+-]+)/(?P<programme_type>[\w\s.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=education_view.EducationSchoolGradingFormView.as_view(),
        name='service_school_grading'
    ),
    re_path(
        r'^services/recreational-add/(?P<registry>[\w.@+-]+)/$',
        view=services_view.RecreationalFormView.as_view(),
        name='service_recreational_add'
    ),
    re_path(
        r'^services/recreational-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.RecreationalFormView.as_view(),
        name='service_recreational_edit'
    ),
    re_path(
        r'^services/lego-add/(?P<registry>[\w.@+-]+)/(?P<age>[\w.@+-]+)/$',
        view=services_view.LegoServiceFormView.as_view(),
        name='service_lego_add'
    ),
    re_path(
        r'^services/lego-edit/(?P<registry>[\w.@+-]+)/(?P<age>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=services_view.LegoServiceFormView.as_view(),
        name='service_lego_edit'
    ),
]
