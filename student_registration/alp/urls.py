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
        regex=r'^edit/(?P<pk>[\w.@+-]+)/$',
        view=views.EditView.as_view(),
        name='edit'
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
        regex=r'^pre-test-add/$',
        view=views.PreTestAddView.as_view(),
        name='pre_test_add'
    ),
    url(
        regex=r'^pre-test-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.PreTestEditView.as_view(),
        name='pre_test_edit'
    ),
    url(
        regex=r'^post-test/$',
        view=views.PostTestView.as_view(),
        name='post_test'
    ),
    url(
        regex=r'^pre-test-grading/(?P<pk>[\w.@+-]+)/$',
        view=views.PreTestGradingView.as_view(),
        name='pre_test_grading'
    ),
    url(
        regex=r'^post-test-grading/(?P<pk>[\w.@+-]+)/$',
        view=views.PostTestGradingView.as_view(),
        name='post_test_grading'
    ),
    url(
        regex=r'^outreach/$',
        view=views.OutreachView.as_view(),
        name='outreach'
    ),
    url(
        regex=r'^outreach-add/$',
        view=views.OutreachAddView.as_view(),
        name='outreach_add'
    ),
    url(
        regex=r'^outreach-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.OutreachEditView.as_view(),
        name='outreach_edit'
    ),
    # url(
    #     regex=r'^alp-registrations/$',
    #     view=views.CurrentRoundView.as_view(),
    #     name='alp_registrations'
    # ),
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

    url(regex=r'^data-collecting/export/$', view=views.OutreachExportViewSet.as_view(), name='alp_data_export'),
]
