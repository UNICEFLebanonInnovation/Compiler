from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^outreach_import_data/$',
        view=views.outreach_import_data,
        name='outreach-import-data'
    ),
    url(
        regex=r'^outreach-page/$',
        view=views.OutreachPage.as_view(),
        name='outreach_page'
    ),

    url(
        regex=r'^outreach-export/$',
        view=views.outreach_export_data,
        name='outreach_export'
    ),
    url(
        regex=r'^outreach-unregistered-export/$',
        view=views.outreach_unregistered_export_data,
        name='outreach_unregistered_export'
    ),
    url(r'^outreach-unregistered-export-info/$', views.outreach_unregistered_export_info, name='outreach_unregistered_export_info'),
    url(r'^outreach-unregistered-export/(?P<part>\d+)/$', views.outreach_unregistered_export_data, name='outreach_unregistered_export')
]
