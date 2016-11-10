from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from student_registration.hhvisit import views

urlpatterns = [

    url(
        regex=r'^household-visit/$',
        view=views.HouseholdVisitView.as_view(),
        name='household_visit'
    )
    ,
    url(
        regex=r'^household-visit-list/$',
        view=views.HouseholdVisitListView.as_view(),
        name='household_visit_list'
    ),
]

