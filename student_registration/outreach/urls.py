from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [
    url(
        regex=r'^outreach_import_data/$',
        view=views.outreach_import_data,
        name='outreach-import-data'
    ),
]
