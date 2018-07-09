from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^export/$',
        view=views.Export4View.as_view(),
        name='export'
    ),

]
