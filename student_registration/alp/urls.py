from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    # url(
    #     regex=r'^data-collecting/$',
    #     view=views.OutreachView.as_view(),
    #     name='alp_data_collecting'
    # ),

    url(
        regex=r'^alp-registrations/$',
        view=views.CurrentRoundView.as_view(),
        name='alp_registrations'
    ),

    url(
        regex=r'^outreach/$',
        view=views.DataCollectingView.as_view(),
        name='alp_outreach'
    ),

    url(
        regex=r'^post-test/$',
        view=views.PostTestView.as_view(),
        name='alp_post_test'
    ),

    url(
        regex=r'^pre-test/$',
        view=views.PreTestView.as_view(),
        name='alp_pre_test'
    ),

    url(
        regex=r'^data-view/$',
        view=views.OutreachStaffView.as_view(),
        name='alp_data_view'
    ),

    url(regex=r'^data-collecting/export/$', view=views.OutreachExportViewSet.as_view(), name='alp_data_export'),
]
