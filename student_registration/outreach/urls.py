from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

app_name = 'outreach'

urlpatterns = [
    re_path(
        r'^outreach_import_data/$',
        view=views.outreach_import_data,
        name='outreach-import-data'
    ),
    re_path(
        r'^outreach-page/$',
        view=views.OutreachPage.as_view(),
        name='outreach_page'
    ),

    re_path(
        r'^outreach-export/$',
        view=views.outreach_export_data,
        name='outreach_export'
    ),
    re_path(
        r'^outreach-unregistered-export/$',
        view=views.outreach_unregistered_export_data,
        name='outreach_unregistered_export'
    ),
    re_path(r'^outreach-unregistered-export-info/$', views.outreach_unregistered_export_info, name='outreach_unregistered_export_info'),
    re_path(r'^outreach-unregistered-export/(?P<part>\d+)/$', views.outreach_unregistered_export_data, name='outreach_unregistered_export')
]
