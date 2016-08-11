from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^outreach/$',
        view=views.OutreachView.as_view(),
        name='outreach'
    ),
    url(
        regex=r'^registration/$',
        view=views.RegistrationView.as_view(),
        name='registration'
    ),
    url(regex=r'^outreach/export/$', view=views.OutreachExportViewSet.as_view(), name='outreach_export'),
    url(regex=r'^registration/export/$', view=views.RegistrationExportViewSet.as_view(), name='registration_export'),
]
