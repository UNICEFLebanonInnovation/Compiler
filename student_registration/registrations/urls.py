from __future__ import absolute_import, unicode_literals

from django.conf.urls import url

from . import views

urlpatterns = [

    url(
        regex=r'^registering-pilot/$',
        view=views.RegisteringPilotView.as_view(),
        name='registering_pilot'
    ),
    url(
        regex=r'^class-assignment/$',
        view=views.ClassAssignmentView.as_view(),
        name='class_assignment'
    ),
    url(
        regex=r'^waiting-list/$',
        view=views.WaitingListView.as_view(),
        name='waiting_list'
    ),
    url(
        regex=r'^registry-search/$',
        view=views.RegisteringAdultListSearchView.as_view(),
        name='registry_search'
    ),
    url(
        regex=r'^list-school-modification/$',
        view=views.SchoolApprovalListView.as_view(),
        name='list_school_modification'
    ),
    url(
        regex=r'^complaints-search/$',
        view=views.ComplaintCategoryListSearchView.as_view(),
        name='complaints_search'
    ),
    url(
        regex=r'^complaints-grid/$',
        view=views.ComplaintsGridView.as_view(),
        name='complaints_grid'
    ),
    url(
        regex=r'^changebeneficiary-grid/$',
        view=views.ChangeBeneficiaryGridView.as_view(),
        name='changebeneficiary_grid'
    ),
]
