from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from student_registration.hhvisit import views

urlpatterns = [

    url(
        regex=r'^household_visit/$',
        view=views.HouseholdVisitView.as_view(),
        name='household_visit'
    ),
]
