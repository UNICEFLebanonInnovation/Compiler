from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^registration/$',
        view=views.RegistrationView.as_view(),
        name='registration'
    ),
    url(
        regex=r'^registering-adult/$',
        view=views.RegisteringAdultView.as_view(),
        name='registering_adult'
    ),
    url(
        regex=r'^registering-child/(?P<pk>\d+)/',
        view=views.RegisteringChildView.as_view(),
        name='registering_child'
    ),
    url(
        regex=r'^registering-pilot/$',
        view=views.RegisteringPilotView.as_view(),
        name='registering_pilot'
    ),
    url(regex=r'^registration/export/$', view=views.ExportViewSet.as_view(), name='registration_export'),
]
