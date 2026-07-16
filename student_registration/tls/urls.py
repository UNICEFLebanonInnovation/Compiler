from django.urls import re_path

from student_registration.mscc.views import (
    ChildProfilePreview,
    child_duplication_check,
    get_file,
    main_mark_delete_view,
    old_child_data,
    old_child_search,
    outreach_child,
    outreach_child_search,
)
from . import views

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
    re_path('outreach-child-search/$', outreach_child_search, name='outreach_child_search'),
    re_path('outreach-child/$', outreach_child, name='outreach_child'),
    re_path('old-child-search/$', old_child_search, name='old_child_search'),
    re_path('get-old-child-data/$', old_child_data, name='old_child_data'),
    re_path('child-duplication-check/$', child_duplication_check, name='child_duplication_check'),
    re_path('child-profile-preview/$', view=ChildProfilePreview.as_view(), name='child_profile_preview'),
    re_path(r'^services/education-add/(?P<registry>[\w.@+-]+)/$', view=views.TLSEducationServiceFormView.as_view(), name='service_education_add'),
    re_path(r'^services/education-edit/(?P<registry>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$', view=views.TLSEducationServiceFormView.as_view(), name='service_education_edit'),
]
