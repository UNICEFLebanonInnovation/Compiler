from __future__ import absolute_import, unicode_literals

from django.urls import re_path
from . import views

app_name = 'staffs'

urlpatterns = [

    re_path(
        r'^add/$',
        view=views.CreateStaffView.as_view(),
        name='add'
    ),
    re_path(
        r'^update/(?P<pk>[\w.@+-]+)/$',
        view=views.EditStaffView.as_view(),
        name='update'
    ),
    re_path(
        r'^stafflist/$',
        view=views.ListStaffView.as_view(),
        name='stafflist'
    ),
]
