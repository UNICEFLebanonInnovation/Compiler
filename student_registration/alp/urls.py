from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^outreach/$',
        view=views.OutreachView.as_view(),
        name='outreach'
    ),
    url(
        regex=r'^outreach-aggregated/$',
        view=views.OutreachOnlineView.as_view(),
        name='outreach-aggregated'
    ),
    url(regex=r'^outreach/export/$', view=views.ExportViewSet.as_view(), name='outreach_export'),
]
