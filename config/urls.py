# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, re_path
from django.views import defaults as default_views
from django.views.generic import TemplateView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter

from student_registration.attendances.views import AbsenteeViewSet, AttendancesExportViewSet, AttendanceViewSet
from student_registration.backends.views import ExporterViewSet, NotificationViewSet
from student_registration.clm.api_views import (
    AttendanceListViewSet,
    BridgingListViewSet,
    SchoolListViewSet,
    TeacherListViewSet
)
from student_registration.clm.inclusion_views import InclusionViewSet
from student_registration.clm.views import (
    ABLNViewSet,
    BLNViewSet,
    BridgingViewSet,
    CBECEViewSet,
    CLMStudentViewSet,
    GeneralQuestionnaireViewSet,
    OutreachViewSet,
    RSViewSet,
    SelfPerceptionGradesViewSet
)
from student_registration.enrollments.views import (
    EnrollmentGradingImportViewSet,
    EnrollmentImportViewSet,
    EnrollmentUpdateViewSet,
    EnrollmentViewSet,
    LoggingProgramMoveViewSet,
    LoggingStudentMoveViewSet,
    StudentDropoutViewSet,
    StudentJustifyViewSet
)
from student_registration.locations.views import LocationAutocomplete, LocationViewSet, ProgramStaffViewSet
from student_registration.outreach.views import ChildViewSet, HouseHoldViewSet
from student_registration.schools.views import ClassRoomViewSet, SchoolAutocomplete, SchoolViewSet, SectionViewSet
from student_registration.students.views import (
    StudentAutocomplete,
    StudentSearchViewSet,
    StudentViewSet,
    TeacherViewSet,
    serve_file
)
from student_registration.users.views import LandingPage, LoginRedirectView, home, login_success

router = DefaultRouter()
router.register(r"attendances", AttendanceViewSet, basename="attendances")
router.register(r"absentees", AbsenteeViewSet, basename="absentees")
router.register(
    r"export-attendances", AttendancesExportViewSet, basename="export_attendances"
)
router.register(r"dirasa/list", BridgingListViewSet, basename="dirasa-list")
router.register(r"dirasa/schools", SchoolListViewSet, basename="dirasa-schools")
router.register(r"dirasa/teachers", TeacherListViewSet, basename="dirasa-teachers")
router.register(
    r"dirasa/attendances", AttendanceListViewSet, basename="dirasa-attendances"
)
router.register(r"students", StudentViewSet, basename="students")
router.register(r"students-search", StudentSearchViewSet, basename="students-search")
router.register(r"schools", SchoolViewSet, basename="schools")
router.register(r"classrooms", ClassRoomViewSet, basename="classrooms")
router.register(r"sections", SectionViewSet, basename="sections")
router.register(r"clm-bln", BLNViewSet, basename="clm-bln")
router.register(r"clm-abln", ABLNViewSet, basename="clm-abln")
router.register(r"clm-rs", RSViewSet, basename="clm-rs")
router.register(r"clm-cbece", CBECEViewSet, basename="clm-cbece")
router.register(r"clm-bridging", BridgingViewSet, basename="clm-bridging")
router.register(r"teacher", TeacherViewSet, basename="teacher")
router.register(r"clm-inclusion", InclusionViewSet, basename="clm-inclusion")
router.register(r"clm-students", CLMStudentViewSet, basename="clm-students")
router.register(
    r"self-perception-grads",
    SelfPerceptionGradesViewSet,
    basename="self-perception-grads",
)
router.register(r"program-staff", ProgramStaffViewSet, basename="program-staff")
router.register(r"clm-outreach", OutreachViewSet, basename="clm-outreach")
router.register(r"locations", LocationViewSet, basename="locations")
router.register(r"enrollments", EnrollmentViewSet, basename="enrollments")
router.register(
    r"import-enrollment", EnrollmentImportViewSet, basename="import_enrollments"
)
router.register(
    r"import-grading", EnrollmentGradingImportViewSet, basename="import_gradings"
)
router.register(
    r"update-enrollment", EnrollmentUpdateViewSet, basename="update_enrollments"
)
router.register(
    r"logging-student-move", LoggingStudentMoveViewSet, basename="logging_student_move"
)
router.register(
    r"student-dropout-enrollment",
    StudentDropoutViewSet,
    basename="student_dropout_enrollment",
)
router.register(
    r"student-justify-enrollment",
    StudentJustifyViewSet,
    basename="student_justify_enrollment",
)
router.register(
    r"logging-student-program-move",
    LoggingProgramMoveViewSet,
    basename="logging_student_ptogram_move",
)
router.register(r"household", HouseHoldViewSet, basename="household")
router.register(r"child", ChildViewSet, basename="child")
router.register(r"notifications", NotificationViewSet, basename="notifications")
router.register(r"backend-exporter", ExporterViewSet, basename="backend-exporter")


urlpatterns = [
    re_path(r"^$", home, name="home"),
    # re_path(r'^$', TemplateView.as_view(template_name='pages/home.html'), name='home'),
    re_path(
        r"^about/$",
        TemplateView.as_view(template_name="pages/about.html"),
        name="about",
    ),
    re_path(r"^login-redirect/$", LoginRedirectView.as_view(), name="login-redirect"),
    re_path(r"^login-success/$", login_success, name="login_success"),
    re_path(r"^landing-page/$", LandingPage.as_view(), name="landing_page"),
    re_path(
        r"^student-autocomplete/$",
        StudentAutocomplete.as_view(),
        name="student_autocomplete",
    ),
    re_path(
        r"^school-autocomplete/$",
        SchoolAutocomplete.as_view(),
        name="school_autocomplete",
    ),
    re_path(
        r"^location-autocomplete/$",
        LocationAutocomplete.as_view(),
        name="location_autocomplete",
    ),
    # Django Admin, use {% url 'admin:index' %}
    re_path(settings.ADMIN_URL, admin.site.urls),
    # User management
    re_path(r"^users/", include("student_registration.users.urls", namespace="users")),
    re_path(r"^accounts/", include("allauth.urls")),
    re_path(
        r"^students/",
        include("student_registration.students.urls", namespace="students"),
    ),
    # re_path(r'^alp/', include('student_registration.alp.urls', namespace='alp')),
    re_path(r"^clm/", include("student_registration.clm.urls", namespace="clm")),
    re_path(r"^mscc/", include("student_registration.mscc.urls", namespace="mscc")),
    re_path(r"^youth/", include("student_registration.youth.urls", namespace="youth")),
    re_path(
        r"^outreach/",
        include("student_registration.outreach.urls", namespace="outreach"),
    ),
    re_path(
        r"^attendances/",
        include("student_registration.attendances.urls", namespace="attendances"),
    ),
    # re_path(r'^staffenroll/', include('student_registration.staffenroll.urls', namespace='staffenroll')),
    # re_path(r'^staffs/', include('student_registration.staffs.urls', namespace='staffs')),
    # re_path(r'^enrollments/', include('student_registration.enrollments.urls', namespace='enrollments')),
    re_path(
        r"^schools/", include("student_registration.schools.urls", namespace="schools")
    ),
    re_path(
        r"^locations/",
        include("student_registration.locations.urls", namespace="locations"),
    ),
    re_path(
        r"^dashboard/",
        include("student_registration.dashboard.urls", namespace="dashboard"),
    ),
    re_path(
        r"^backends/",
        include("student_registration.backends.urls", namespace="backends"),
    ),
    # re_path(r'helpdesk/', include('helpdesk.urls')),
    # re_path(r'^winterization/', include('student_registration.winterization.urls', namespace='winterization')),
    re_path(r"^api-auth/", include("rest_framework.urls", namespace="rest_framework")),
    # re_path(r'^api/docs/', schema_view), # Replaced by drf-spectacular
    # drf-spectacular URLs
    re_path(r"^api/schema/$", SpectacularAPIView.as_view(), name="schema"),
    re_path(
        r"^api/schema/swagger-ui/$",
        SpectacularSwaggerView.as_view(url_name="schema"),
        name="swagger-ui",
    ),
    re_path(
        r"^api/schema/redoc/$",
        SpectacularRedocView.as_view(url_name="schema"),
        name="redoc",
    ),
    re_path(r"^api/", include(router.urls)),
    re_path(r"^serve-file/(?P<file_path>.+)/$", serve_file, name="serve_file"),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    import debug_toolbar

    urlpatterns += [
        re_path(
            r"^400/$",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        re_path(
            r"^403/$",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        re_path(
            r"^404/$",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        re_path(r"^500/$", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [
            re_path(r"^__debug__/", include(debug_toolbar.urls)),
        ] + urlpatterns
