from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

<<<<<<< HEAD
=======
    url(
        regex=r'^profile/$',
        view=views.ProfileView.as_view(),
        name='profile'
    ),

>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
]
