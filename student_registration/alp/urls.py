from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^data-collecting/$',
        view=views.OutreachView.as_view(),
        name='alp_data_collecting'
    ),

    url(
        regex=r'^data-view/$',
        view=views.OutreachStaffView.as_view(),
        name='alp_data_view'
    ),

    url(regex=r'^data-collecting/export/$', view=views.OutreachExportViewSet.as_view(), name='alp_data_export'),
]
