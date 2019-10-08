from __future__ import absolute_import, unicode_literals

from django.conf.urls import url
from . import views

urlpatterns = [

    url(
        regex=r'^add/$',
        view=views.AddView.as_view(),
        name='add'
    ),
 #   url(
  #      regex=r'^edit/(?P<pk>[\w.@+-]+)/$',
   #     view=views.EditView.as_view(),
    #    name='edit'
#    ),
 #  url(
  #      regex=r'^saveimage/(?P<stdid>[\w.@+-]+)/$',
   #     view=views.image_update,
    #    name='saveimage'
   # ),
    url(
        regex=r'^list/$',
        view=views.ListingView.as_view(),
        name='list'
    ),
]
