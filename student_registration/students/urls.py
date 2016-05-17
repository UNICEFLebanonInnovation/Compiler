from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    # URL pattern for the StudentListView
    url(
        regex=r'^$',
        view=views.StudentListView.as_view(),
        name='list'
    ),
]
