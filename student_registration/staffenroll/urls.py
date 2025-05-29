from __future__ import absolute_import, unicode_literals

from django.urls import re_path
from . import views

urlpatterns = [

    re_path(
        regex=r'^add/$',
        view=views.AddView.as_view(),
        name='add'
    ),
 #   re_path(
  #      regex=r'^edit/(?P<pk>[\w.@+-]+)/$',
   #     view=views.EditView.as_view(),
    #    name='edit'
#    ),
 #  re_path(
  #      regex=r'^saveimage/(?P<stdid>[\w.@+-]+)/$',
   #     view=views.image_update,
    #    name='saveimage'
   # ),
    re_path(
        regex=r'^list/$',
        view=views.ListingView.as_view(),
        name='list'
    ),
]
