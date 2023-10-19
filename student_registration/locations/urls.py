from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^Center-Add/$',
        view=views.CenterFormView.as_view(),
        name='center_add'
    ),
    url(
        regex=r'^Center-Edit/(?P<pk>[\w.@+-]+)/$',
        view=views.CenterFormView.as_view(),
        name='center_edit'
    ),
    url(
        regex=r'^Center-List/$',
        view=views.CenterListView.as_view(),
        name='center_list'
    ),
    url(
        regex=r'^Center-Profile/(?P<pk>[\w.@+-]+)/$',
        view=views.ProfileView.as_view(),
        name='center_profile'
    ),
    url(
        regex=r'^Program-Staff-Add/(?P<center_id>[\w.@+-]+)/$',
        view=views.ProgramStaffFormView.as_view(),
        name='program_staff_add'
    ),
    url(
        regex=r'^Program-Staff-Edit/(?P<center_id>[\w.@+-]+)/(?P<pk>[\w.@+-]+)/$',
        view=views.ProgramStaffFormView.as_view(),
        name='program_staff_edit'
    ),
    url(
        regex=r'^Program-Staff-Delete/(?P<pk>[\w.@+-]+)/$',
        view=views.program_staff_delete,
        name='program_staff_delete'
    ),
]
