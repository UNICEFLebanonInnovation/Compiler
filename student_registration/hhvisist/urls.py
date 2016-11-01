from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^registering-pilot/$',
        view=views.RegisteringPilotView.as_view(),
        name='registering_pilot'
    ),
]
