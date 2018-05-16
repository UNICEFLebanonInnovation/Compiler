from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^files-list/$',
        view=views.ExporterListView.as_view(),
        name='files_list'
    ),

]
