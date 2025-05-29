from __future__ import absolute_import, unicode_literals

from django.urls import re_path

from . import views

urlpatterns = [

    re_path(
        regex=r'^add/$',
        view=views.AddView.as_view(),
        name='add'
    ),
    re_path(
        regex=r'^edit/(?P<pk>[\w.@+-]+)/$',
        view=views.EditView.as_view(),
        name='edit'
    ),
    re_path(
        regex=r'^list/$',
        view=views.SchoolView.as_view(),
        name='list'
    ),
    re_path(
        regex=r'^pre-test/$',
        view=views.PreTestView.as_view(),
        name='pre_test'
    ),
    re_path(
        regex=r'^pre-test-all/$',
        view=views.PreTest_allView.as_view(),
        name='pre_test_all'
    ),
    re_path(
        regex=r'^pre-test-add/$',
        view=views.PreTestAddView.as_view(),
        name='pre_test_add'
    ),
    re_path(
        regex=r'^pre-test-add-all/$',
        view=views.PreTestAdd_allView.as_view(),
        name='pre_test_add_all'
    ),
    re_path(
        regex=r'^pre-test-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.PreTestEditView.as_view(),
        name='pre_test_edit'
    ),
    re_path(
        regex=r'^post-test/$',
        view=views.PostTestView.as_view(),
        name='post_test'
    ),
    re_path(
        regex=r'^pre-test-grading/(?P<pk>[\w.@+-]+)/$',
        view=views.PreTestGradingView.as_view(),
        name='pre_test_grading'
    ),
    re_path(
        regex=r'^post-test-grading/(?P<pk>[\w.@+-]+)/$',
        view=views.PostTestGradingView.as_view(),
        name='post_test_grading'
    ),
    re_path(
        regex=r'^outreach/$',
        view=views.OutreachView.as_view(),
        name='outreach'
    ),
    re_path(
        regex=r'^outreach-add/$',
        view=views.OutreachAddView.as_view(),
        name='outreach_add'
    ),
    re_path(
        regex=r'^outreach-edit/(?P<pk>[\w.@+-]+)/$',
        view=views.OutreachEditView.as_view(),
        name='outreach_edit'
    ),
    # re_path(
    #     regex=r'^alp-registrations/$',
    #     view=views.CurrentRoundView.as_view(),
    #     name='alp_registrations'
    # ),
    #
    # re_path(
    #     regex=r'^outreach/$',
    #     view=views.DataCollectingView.as_view(),
    #     name='alp_outreach'
    # ),
    #
    # re_path(
    #     regex=r'^post-test/$',
    #     view=views.PostTestView.as_view(),
    #     name='alp_post_test'
    # ),
    #
    # re_path(
    #     regex=r'^pre-test/$',
    #     view=views.PreTestView.as_view(),
    #     name='alp_pre_test'
    # ),
    re_path(
        regex=r'^number-by-school/$',
        view=views.ExportBySchoolView.as_view(),
        name='alp_export_by_school'
    ),

    re_path(
        regex=r'^export/$',
        view=views.ExportViewSet.as_view(),
        name='export'
    ),
]
