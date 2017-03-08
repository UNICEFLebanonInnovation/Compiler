from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^registrations-pilot/$',
        view=views.RegistrationsPilotView.as_view(),
        name='registrations-pilot'
    ),
    url(
        regex=r'^registrations-2ndshift/$',
        view=views.Registrations2ndShiftView.as_view(),
        name='registrations-2ndshift'
    ),
    url(
        regex=r'^registrations-alp/$',
        view=views.RegistrationsALPView.as_view(),
        name='registrations-alp'
    ),
    url(
        regex=r'^registrations-alp-outreach/$',
        view=views.RegistrationsALPOutreachView.as_view(),
        name='registrations-alp-outreach'
    ),
    url(
        regex=r'^registrations-alp-pre-test/$',
        view=views.RegistrationsALPPreTestView.as_view(),
        name='registrations-alp-pre-test'
    ),
    url(
        regex=r'^registrations-alp-post-test/$',
        view=views.RegistrationsALPPostTestView.as_view(),
        name='registrations-alp-post-test'
    ),
    url(
        regex=r'^attendances/$',
        view=views.AttendanceView.as_view(),
        name='attendances'
    ),
]
