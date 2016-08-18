from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^registration/$',
        view=views.RegistrationView.as_view(),
        name='registration'
    ),
    url(regex=r'^registration/export/$', view=views.ExportViewSet.as_view(), name='registration_export'),
]
