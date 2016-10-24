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
        regex=r'^registration-view/$',
        view=views.RegistrationStaffView.as_view(),
        name='registration_view'
    ),
    url(
        regex=r'^registering-pilot/$',
        view=views.RegisteringPilotView.as_view(),
        name='registering_pilot'
    ),
    url(
        regex=r'^class-assignment/$',
        view=views.ClassAssignmentView.as_view(),
        name='class_assignment'
    ),
    url(
        regex=r'^waiting-list/$',
        view=views.WaitingListView.as_view(),
        name='waiting_list'
    ),
    url(regex=r'^registration/export/$', view=views.ExportViewSet.as_view(), name='registration_export'),
]
