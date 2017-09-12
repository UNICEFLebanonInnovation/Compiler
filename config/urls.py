# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views
<<<<<<< HEAD
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
    MissingChildViewSet,
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
=======

from rest_framework_nested import routers
from rest_framework_swagger.views import get_swagger_view

from student_registration.alp.views import (
    OutreachViewSet,
)
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
from student_registration.attendances.views import (
    AttendanceViewSet,
    AttendanceReportViewSet,
)
from student_registration.students.views import (
    StudentViewSet,
<<<<<<< HEAD
=======
    StudentAutocomplete,
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
)
from student_registration.schools.views import (
    SchoolViewSet,
    ClassRoomViewSet,
    SectionViewSet,
<<<<<<< HEAD
    GradeViewSet,
)
from student_registration.eav.views import (
    AttributeViewSet,
    ValueViewSet,
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
)
from student_registration.winterization.views import (
    BeneficiaryViewSet
)
from student_registration.users.views import LoginRedirectView, PasswordChangeView, PasswordChangeDoneView
from student_registration.enrollments.views import EnrollmentViewSet, LoggingStudentMoveViewSet
<<<<<<< HEAD
from student_registration.students.views import StudentAutocomplete
from .views import acme_view
=======
from student_registration.outreach.views import HouseHoldViewSet, ChildViewSet
from django.views.generic import RedirectView
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

api = routers.SimpleRouter()
api.register(r'outreach', OutreachViewSet, base_name='outreach')
api.register(r'enrollments', EnrollmentViewSet, base_name='enrollments')
api.register(r'logging-student-move', LoggingStudentMoveViewSet, base_name='logging_student_move')
<<<<<<< HEAD
api.register(r'registrations-adult', RegisteringAdultViewSet, base_name='registrations_adult')
api.register(r'registrations-adult-id', RegisteringAdultIDViewSet, base_name='registrations_adult_id')
api.register(r'registrations-child', RegisteringChildViewSet, base_name='registrations_child')
api.register(r'registrations-complaint', RegisteringComplaintViewSet, base_name='registrations_complaint')

api.register(r'registrations-complaint-category', RegisteringComplaintCategoryViewSet, base_name='registrations_complaint_category')


api.register(r'registrations-notfound', RegisteringNotFoundViewSet, base_name='registrations_notfound')
api.register(r'registrations-missingchild', MissingChildViewSet, base_name='registrations_missingchild')
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
=======
api.register(r'attendances', AttendanceViewSet, base_name='attendances')
api.register(r'attendances-report', AttendanceReportViewSet, base_name='attendances_report')
api.register(r'beneficiary', BeneficiaryViewSet, base_name='beneficiary')

api.register(r'students', StudentViewSet, base_name='students')
api.register(r'household', HouseHoldViewSet, base_name='household')
api.register(r'child', ChildViewSet, base_name='child')
api.register(r'schools', SchoolViewSet, base_name='schools')
api.register(r'classrooms', ClassRoomViewSet, base_name='classrooms')
api.register(r'sections', SectionViewSet, base_name='sections')

schema_view = get_swagger_view(title='Compiler API')


urlpatterns = [
    url(r'^clm/', include('student_registration.clm.urls', namespace='clm')),
    url(r'^$', RedirectView.as_view(url='/clm/index')),
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    url(r'^login-redirect/$', LoginRedirectView.as_view(), name='login-redirect'),
    url(r'^change-password/$', PasswordChangeView.as_view(), name='change_password'),
    url(r'^change-password-done/$', PasswordChangeDoneView.as_view(), name='change_password_done'),
    url(r'^student-autocomplete/$', StudentAutocomplete.as_view(), name='student_autocomplete'),

    # Django Admin, use {% url 'admin:index' %}
<<<<<<< HEAD
    url(settings.ADMIN_URL, include(admin.site.urls)),
=======
    url(settings.ADMIN_URL, admin.site.urls),
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

    # User management
    url(r'^users/', include('student_registration.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^students/', include('student_registration.students.urls', namespace='students')),
    url(r'^alp/', include('student_registration.alp.urls', namespace='alp')),
<<<<<<< HEAD
    url(r'^attendances/', include('student_registration.attendances.urls', namespace='attendances')),
    url(r'^registrations/', include('student_registration.registrations.urls', namespace='registrations')),
    url(r'^hhvisit/',include('student_registration.hhvisit.urls', namespace='hhvisit')),
=======
    url(r'^outreach/', include('student_registration.outreach.urls', namespace='outreach')),
    url(r'^attendances/', include('student_registration.attendances.urls', namespace='attendances')),
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    url(r'^enrollments/', include('student_registration.enrollments.urls', namespace='enrollments')),
    url(r'^schools/', include('student_registration.schools.urls', namespace='schools')),
    url(r'^locations/', include('student_registration.locations.urls', namespace='locations')),
    url(r'^dashboard/', include('student_registration.dashboard.urls', namespace='dashboard')),

    url(r'helpdesk/', include('helpdesk.urls')),
    url(r'^winterization/', include('student_registration.winterization.urls', namespace='winterization')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
<<<<<<< HEAD
    url(r'^api/docs/', include('rest_framework_swagger.urls')),

    url(r'^api/', include(api.urls)),

    url(r'^.well-known/acme-challenge/(?P<slug>.*)/', acme_view),

=======
    url(r'^api/docs/', schema_view),

    url(r'^api/', include(api.urls)),

>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
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
<<<<<<< HEAD
        url(r'^__debug__/', include(debug_toolbar.urls)),
    ]
=======
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
