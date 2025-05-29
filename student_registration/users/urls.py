# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.urls import re_path, include

from . import views

urlpatterns = [
    # URL pattern for the UserListView
    # re_path(
    #     regex=r'^$',
    #     view=views.UserListView.as_view(),
    #     name='list'
    # ),

    # URL pattern for the UserRedirectView
    re_path(
        regex=r'^redirect/$',
        view=views.LoginRedirectView.as_view(),
        name='redirect'
    ),

    # URL pattern for the UserDetailView
    re_path(
        regex=r'^(?P<username>[\w.@+-]+)/$',
        view=views.UserDetailView.as_view(),
        name='detail'
    ),

    # URL pattern for the UserUpdateView
    # re_path(
    #     regex=r'^~update/$',
    #     view=views.UserUpdateView.as_view(),
    #     name='update'
    # ),

    re_path(
        r'^set-language/(?P<language>[\w.@+-]+)/$',
        view=views.UserChangeLanguageRedirectView.as_view(),
        name='set_language'
    ),
    re_path(
        regex=r'^partner',
        view=views.user_overview,
        name='profile'
    ),
]
