# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.urls import re_path, include

from . import views

app_name = 'users'

urlpatterns = [
    # URL pattern for the UserListView
    # re_path(
    #     r'^$',
    #     view=views.UserListView.as_view(),
    #     name='list'
    # ),

    # URL pattern for the UserRedirectView
    re_path(
        r'^redirect/$',
        view=views.LoginRedirectView.as_view(),
        name='redirect'
    ),

    # URL pattern for the UserDetailView
    re_path(
        r'^(?P<username>[\w.@+-]+)/$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the UserUpdateView
    # re_path(
    #     r'^~update/$',
    #     view=views.UserUpdateView.as_view(),
    #     name='update'
    # ),

    re_path(
        r'^set-language/(?P<language>[\w.@+-]+)/$',
        view=views.UserChangeLanguageRedirectView.as_view(),
        name='set_language'
    ),
    re_path(
        r'^partner',
        view=views.user_overview,
        name='profile'
    ),
    re_path(
        r'^two-factor/setup/$',
        view=views.two_factor_setup,
        name='two_factor_setup'
    ),
    re_path(
        r'^two-factor/prompt/$',
        view=views.two_factor_prompt,
        name='two_factor_prompt'
    ),
    re_path(
        r'^two-factor/verify/$',
        view=views.two_factor_verify,
        name='two_factor_verify'
    ),
]
