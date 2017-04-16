# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
from rest_framework_nested import routers
from student_registration.alp.views import (
    OutreachViewSet,
)
from student_registration.registrations.views import (
    RegisteringAdultViewSet,
    RegisteringChildViewSet,
    ClassAssignmentViewSet,
    WaitingListViewSet,
    RegisteringAdultListSearchView,
    RegisteringAdultIDViewSet,
    RegisteringComplaintViewSet,
    RegisteringNotFoundViewSet,
    RegisteringComplaintCategoryViewSet
)
from student_registration.hhvisit.views import (
    HouseholdVisitLoadViewSet,
    HouseholdVisitAttemptViewSet,
    HouseholdVisitChildViewSet,
    HouseholdVisitServiceViewSet,
    HouseholdVisitCommentViewSet,
    HouseholdVisitSaveViewSet
)
from student_registration.attendances.views import (
    AttendanceViewSet,
    AttendanceReportViewSet,
)
from student_registration.students.views import (
    StudentViewSet,
)
from student_registration.schools.views import (
    SchoolViewSet,
    ClassRoomViewSet,
    SectionViewSet,
    GradeViewSet,
)
from student_registration.eav.views import (
    AttributeViewSet,
    ValueViewSet,
)
from student_registration.winterization.views import (
    BeneficiaryViewSet
)
from student_registration.users.views import LoginRedirectView, PasswordChangeView, PasswordChangeDoneView
from student_registration.enrollments.views import EnrollmentViewSet
from student_registration.students.views import StudentAutocomplete
from .views import acme_view

api = routers.SimpleRouter()
api.register(r'outreach', OutreachViewSet, base_name='outreach')
api.register(r'enrollments', EnrollmentViewSet, base_name='enrollments')
api.register(r'registrations-adult', RegisteringAdultViewSet, base_name='registrations_adult')
api.register(r'registrations-adult-id', RegisteringAdultIDViewSet, base_name='registrations_adult_id')
api.register(r'registrations-child', RegisteringChildViewSet, base_name='registrations_child')
api.register(r'registrations-complaint', RegisteringComplaintViewSet, base_name='registrations_complaint')

api.register(r'registrations-complaint-category', RegisteringComplaintCategoryViewSet, base_name='registrations_complaint_category')


api.register(r'registrations-notfound', RegisteringNotFoundViewSet, base_name='registrations_notfound')
api.register(r'attendances', AttendanceViewSet, base_name='attendances')
api.register(r'attendances-report', AttendanceReportViewSet, base_name='attendances_report')
api.register(r'class-assignment', ClassAssignmentViewSet, base_name='class_assignment')
api.register(r'waiting-list', WaitingListViewSet, base_name='waiting_list')
api.register(r'registry-search', RegisteringAdultListSearchView, base_name='registry_search')
api.register(r'beneficiary', BeneficiaryViewSet, base_name='beneficiary')

api.register(r'household-visit', HouseholdVisitLoadViewSet, base_name='household_visit')
api.register(r'household-visit-attempt', HouseholdVisitAttemptViewSet, base_name='household_visit_attempt')
api.register(r'household-team', HouseholdVisitSaveViewSet, base_name='household_team')
api.register(r'household-visit-child', HouseholdVisitChildViewSet, base_name='household_visit_child')
api.register(r'household-visit-service', HouseholdVisitServiceViewSet, base_name='household_visit_service')
api.register(r'household-visit-comment', HouseholdVisitCommentViewSet, base_name='household_visit_comment')

api.register(r'students', StudentViewSet, base_name='students')
api.register(r'schools', SchoolViewSet, base_name='schools')
api.register(r'classrooms', ClassRoomViewSet, base_name='classrooms')
api.register(r'sections', SectionViewSet, base_name='sections')
api.register(r'grades', GradeViewSet, base_name='grades')
api.register(r'eav/attributes', AttributeViewSet, base_name='eav-attributes')
api.register(r'eav/values', ValueViewSet, base_name='eav-values')

urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    url(r'^login-redirect/$', LoginRedirectView.as_view(), name='login-redirect'),
    url(r'^change-password/$', PasswordChangeView.as_view(), name='change_password'),
    url(r'^change-password-done/$', PasswordChangeDoneView.as_view(), name='change_password_done'),
    url(r'^student-autocomplete/$', StudentAutocomplete.as_view(), name='student_autocomplete'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/', include('student_registration.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^students/', include('student_registration.students.urls', namespace='students')),
    url(r'^alp/', include('student_registration.alp.urls', namespace='alp')),
    url(r'^attendances/', include('student_registration.attendances.urls', namespace='attendances')),
    url(r'^registrations/', include('student_registration.registrations.urls', namespace='registrations')),
    url(r'^hhvisit/',include('student_registration.hhvisit.urls', namespace='hhvisit')),
    url(r'^enrollments/', include('student_registration.enrollments.urls', namespace='enrollments')),
    url(r'^schools/', include('student_registration.schools.urls', namespace='schools')),
    url(r'^locations/', include('student_registration.locations.urls', namespace='locations')),
    url(r'^dashboard/', include('student_registration.dashboard.urls', namespace='dashboard')),

    url(r'helpdesk/', include('helpdesk.urls')),
    url(r'^winterization/', include('student_registration.winterization.urls', namespace='winterization')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/docs/', include('rest_framework_swagger.urls')),

    url(r'^api/', include(api.urls)),

    url(r'^.well-known/acme-challenge/(?P<slug>.*)/', acme_view),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    import debug_toolbar
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
