from __future__ import absolute_import, unicode_literals

from django.urls import re_path
from . import views

app_name = 'staffenroll'

urlpatterns = [

    re_path(
        r'^add/$',
        view=views.AddView.as_view(),
        name='add'
    ),
    re_path(
        r'^list/$',
        view=views.ListingView.as_view(),
        name='list'
    ),
]
