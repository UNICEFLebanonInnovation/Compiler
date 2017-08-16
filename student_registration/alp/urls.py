from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^add/$',
        view=views.AddView.as_view(),
        name='add'
    ),
    url(
        regex=r'^list/$',
        view=views.SchoolView.as_view(),
        name='list'
    ),
    url(
        regex=r'^pre-test/$',
        view=views.PreTestView.as_view(),
        name='pre_test'
    ),
    url(
        regex=r'^post-test/$',
        view=views.PreTestView.as_view(),
        name='post_test'
    ),
    url(
        regex=r'^pre-test-grading/$',
        view=views.PreTestGradingView.as_view(),
        name='pre_test_grading'
    ),
    url(
        regex=r'^post-test-grading/$',
        view=views.PostTestGradingView.as_view(),
        name='post_test_grading'
    ),
    url(
        regex=r'^alp-registrations/$',
        view=views.CurrentRoundView.as_view(),
        name='alp_registrations'
    ),
    #
    # url(
    #     regex=r'^outreach/$',
    #     view=views.DataCollectingView.as_view(),
    #     name='alp_outreach'
    # ),
    #
    # url(
    #     regex=r'^post-test/$',
    #     view=views.PostTestView.as_view(),
    #     name='alp_post_test'
    # ),
    #
    # url(
    #     regex=r'^pre-test/$',
    #     view=views.PreTestView.as_view(),
    #     name='alp_pre_test'
    # ),
    url(
        regex=r'^alp-export-by-school/$',
        view=views.ExportBySchoolView.as_view(),
        name='alp_export_by_school'
    ),
    url(
        regex=r'^data-view/$',
        view=views.OutreachStaffView.as_view(),
        name='alp_data_view'
    ),

    url(regex=r'^data-collecting/export/$', view=views.OutreachExportViewSet.as_view(), name='alp_data_export'),
]
