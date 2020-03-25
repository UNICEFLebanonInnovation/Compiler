from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^profile/$',
        view=views.ProfileView.as_view(),
        name='profile'
    ),
    url(
        regex=r'^partner/$',
        view=views.PartnerView.as_view(),
        name='partner'
    ),
    url(
        regex=r'^documents/$',
        view=views.PublicDocumentView.as_view(),
        name='documents'
    ),
    url(
        regex=r'^autocomplete/$',
        view=views.AutocompleteView.as_view(),
        name='autocomplete'
    ),
    url(
        regex=r'^evaluation/$',
        view=views.EvaluationView.as_view(),
        name='evaluation'
    ),
    url(
        regex=r'^evaluation/update_classroom/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class.as_view(),
        name='update_classroom'
    ),
    url(
        regex=r'^evaluation/update_classroom_c1/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class_c1.as_view(),
        name='update_classroom_c1'
    ),
    url(
        regex=r'^evaluation/update_classroom_c3/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class_C3.as_view(),
        name='update_classroom_c3'
    ),
    url(
        regex=r'^evaluation/update_classroom_c4/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class_c4.as_view(),
        name='update_classroom_c4'
    ),
    url(
        regex=r'^evaluation/update_classroom_c5/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class_c5.as_view(),
        name='update_classroom_c5'
    ),
    url(
        regex=r'^evaluation/update_classroom_c6/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class_c6.as_view(),
        name='update_classroom_c6'
    ),
    url(
        regex=r'^evaluation/update_classroom_c7/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class_c7.as_view(),
        name='update_classroom_c7'
    ),
    url(
        regex=r'^evaluation/update_classroom_c8/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class_c8.as_view(),
        name='update_classroom_c8'
    ),
    url(
        regex=r'^evaluation/update_classroom_c9/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class_c9.as_view(),
        name='update_classroom_c9'
    ),
    url(
        regex=r'^evaluation/update_classroom_cprep/(?P<pk>[\w.@+-]+)/$',
        view=views.Update_Class_cprep.as_view(),
        name='update_classroom_cprep'
    ),
]
