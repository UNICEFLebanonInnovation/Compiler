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
]
