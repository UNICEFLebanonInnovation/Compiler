from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [

    url(
        regex=r'^add/$',
        view=views.CreateStaffView.as_view(),
        name='add'
    ),
    url(
        regex=r'^update/(?P<pk>[\w.@+-]+)/$',
        view=views.EditStaffView.as_view(),
        name='update'
    ),
    url(
        regex=r'^stafflist/$',
        view=views.ListStaffView.as_view(),
        name='stafflist'
    ),
]
