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
    RegistrationViewSet,
)
from student_registration.attendances.views import (
    AttendanceViewSet,
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

api = routers.SimpleRouter()
api.register(r'outreach', OutreachViewSet, base_name='outreach')
api.register(r'registrations', RegistrationViewSet, base_name='registrations')
api.register(r'attendances', AttendanceViewSet, base_name='attendances')

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

    # Django Admin, use {% url 'admin:index' %}
    url(settings.ADMIN_URL, include(admin.site.urls)),

    # User management
    url(r'^users/', include('student_registration.users.urls', namespace='users')),
    url(r'^accounts/', include('allauth.urls')),

    url(r'^students/', include('student_registration.students.urls', namespace='students')),
    url(r'^alp/', include('student_registration.alp.urls', namespace='alp')),
    url(r'^attendances/', include('student_registration.attendances.urls', namespace='attendances')),
    url(r'^registrations/', include('student_registration.registrations.urls', namespace='registrations')),
    url(r'^schools/', include('student_registration.schools.urls', namespace='schools')),
    url(r'^locations/', include('student_registration.locations.urls', namespace='locations')),

    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
    url(r'^api/docs/', include('rest_framework_swagger.urls')),

    url(r'^api/', include(api.urls)),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        url(r'^400/$', default_views.bad_request, kwargs={'exception': Exception('Bad Request!')}),
        url(r'^403/$', default_views.permission_denied, kwargs={'exception': Exception('Permission Denied')}),
        url(r'^404/$', default_views.page_not_found, kwargs={'exception': Exception('Page not Found')}),
        url(r'^500/$', default_views.server_error),
    ]
