# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls import include, url
from django.conf.urls.static import static
from django.contrib import admin
from django.views.generic import TemplateView
from django.views import defaults as default_views

from rest_framework_nested import routers
from rest_framework_swagger.views import get_swagger_view

from student_registration.alp.views import (
    OutreachViewSet,
)
from student_registration.attendances.views import (
    AttendanceViewSet,
    AbsenteeViewSet,
    AttendancesExportViewSet,
)
from student_registration.students.views import (
    StudentViewSet,
    StudentSearchViewSet,
    StudentAutocomplete,
)
from student_registration.schools.views import (
    SchoolViewSet,
    ClassRoomViewSet,
    SectionViewSet,
)
from student_registration.clm.views import (
    BLNViewSet,
    RSViewSet,
    CBECEViewSet,
    CLMStudentViewSet,
    SelfPerceptionGradesViewSet
)

from student_registration.users.views import LoginRedirectView
from student_registration.enrollments.views import (
    EnrollmentViewSet,
    EnrollmentImportViewSet,
    EnrollmentGradingImportViewSet,
    LoggingStudentMoveViewSet,
    LoggingProgramMoveViewSet,
    EnrollmentUpdateViewSet,
    StudentDropoutViewSet,
)
from student_registration.outreach.views import HouseHoldViewSet, ChildViewSet
from student_registration.backends.views import NotificationViewSet, ExporterViewSet

api = routers.SimpleRouter()
api.register(r'alp', OutreachViewSet, base_name='alp')
api.register(r'enrollments', EnrollmentViewSet, base_name='enrollments')
api.register(r'import-enrollment', EnrollmentImportViewSet, base_name='import_enrollments')
api.register(r'import-grading', EnrollmentGradingImportViewSet, base_name='import_gradings')
api.register(r'update-enrollment', EnrollmentUpdateViewSet, base_name='update_enrollments')
api.register(r'logging-student-move', LoggingStudentMoveViewSet, base_name='logging_student_move')
api.register(r'student-dropout-enrollment', StudentDropoutViewSet, base_name='student_dropout_enrollment')
api.register(r'logging-student-program-move', LoggingProgramMoveViewSet, base_name='logging_student_ptogram_move')
api.register(r'attendances', AttendanceViewSet, base_name='attendances')
api.register(r'absentees', AbsenteeViewSet, base_name='absentees')
api.register(r'export-attendances', AttendancesExportViewSet, base_name='export_attendances')

api.register(r'students', StudentViewSet, base_name='students')
api.register(r'students-search', StudentSearchViewSet, base_name='students-search')
api.register(r'household', HouseHoldViewSet, base_name='household')
api.register(r'child', ChildViewSet, base_name='child')
api.register(r'schools', SchoolViewSet, base_name='schools')
api.register(r'classrooms', ClassRoomViewSet, base_name='classrooms')
api.register(r'sections', SectionViewSet, base_name='sections')
api.register(r'clm-bln', BLNViewSet, base_name='clm-bln')
api.register(r'clm-rs', RSViewSet, base_name='clm-rs')
api.register(r'clm-cbece', CBECEViewSet, base_name='clm-cbece')
api.register(r'clm-students', CLMStudentViewSet, base_name='clm-students')
api.register(r'self-perception-grads', SelfPerceptionGradesViewSet, base_name='self-perception-grads')
api.register(r'notifications', NotificationViewSet, base_name='notifications')
api.register(r'backend-exporter', ExporterViewSet, base_name='backend-exporter')

schema_view = get_swagger_view(title='Compiler API')


urlpatterns = [
    url(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    url(r'^about/$', TemplateView.as_view(template_name='pages/about.html'), name='about'),
    url(r'^login-redirect/$', LoginRedirectView.as_view(), name='login-redirect'),
    url(r'^student-autocomplete/$', StudentAutocomplete.as_view(), name='student_autocomplete'),

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, admin.site.urls),

    # User management
    url(r'^users/', include('student_registration.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^students/', include('student_registration.students.urls', namespace='students')),
    url(r'^alp/', include('student_registration.alp.urls', namespace='alp')),
    url(r'^clm/', include('student_registration.clm.urls', namespace='clm')),
    url(r'^outreach/', include('student_registration.outreach.urls', namespace='outreach')),
    url(r'^attendances/', include('student_registration.attendances.urls', namespace='attendances')),
    url(r'^enrollments/', include('student_registration.enrollments.urls', namespace='enrollments')),
    url(r'^schools/', include('student_registration.schools.urls', namespace='schools')),
    url(r'^locations/', include('student_registration.locations.urls', namespace='locations')),
    url(r'^dashboard/', include('student_registration.dashboard.urls', namespace='dashboard')),
    url(r'^backends/', include('student_registration.backends.urls', namespace='backends')),

    url(r'helpdesk/', include('helpdesk.urls')),
    url(r'^winterization/', include('student_registration.winterization.urls', namespace='winterization')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/docs/', schema_view),

    url(r'^api/', include(api.urls)),

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
    ]
    if 'debug_toolbar' in settings.INSTALLED_APPS:
        import debug_toolbar
        urlpatterns = [
            url(r'^__debug__/', include(debug_toolbar.urls)),
        ] + urlpatterns
