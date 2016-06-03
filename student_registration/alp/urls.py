from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^outreach/$',
        view=views.OutreachView.as_view(),
        name='outreach'
    ),
    url(regex=r'^outreach/list/$', view=views.OutreachListJson.as_view(), name='outreach_list_json'),
    url(regex=r'^outreach/new-line/$', view=views.OutreachNewLineView.as_view(), name='outreach_new_line'),
]
