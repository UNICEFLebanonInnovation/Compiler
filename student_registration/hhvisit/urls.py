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
    url(
        regex=r'^household-visit-list-supervisor/$',
        view=views.HouseholdVisitListSupervisorView.as_view(),
        name='household_visit_list_supervisor'
    ),
    # url(
    #     regex=r'^test/$',
    #     view=views.test,
    #     name='household_visit_test'
    # ),
    url(
        regex=r'^load-absences/$',
        view=views.LoadAbsences,
        name='household_visit_load_absences'
    ),
    url(
        regex=r'^save-absences/$',
        view=views.SaveAbsences,
        name='household_visit_save_absences'
    ),
     url(
         regex=r'^student-absence/$',
         view=views.StudentAbsenceView.as_view(),
         name='student_absence'
     )
    # ,
    # url(
    #     regex=r'^student-search/$',
    #     view=views.StudentSearch.as_view(),
    #     name='student_search'
    # )

]

