# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.http import Http404
from django.views.generic import ListView, FormView, TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponse, JsonResponse
from rest_framework import viewsets, mixins, permissions
import tablib
import json
from rest_framework import status
from django.utils.translation import ugettext as _
from import_export.formats import base_formats
from django.core.urlresolvers import reverse
from datetime import datetime
from student_registration.alp.templatetags.util_tags import has_group

from student_registration.students.models import (
    Person,
    Student,
    Nationality,
    IDType,
)
from student_registration.schools.models import (
    School,
    ClassRoom,
    Grade,
    Section,
    EducationLevel,
    ClassLevel,
)
from student_registration.students.serializers import StudentSerializer
from student_registration.registrations.forms import (
    RegisteringAdultForm,
    RegisteringChildForm,
    WaitingListForm,
)
from student_registration.students.forms import StudentForm
from student_registration.eav.models import (
    Attribute,
    Value,
)
from student_registration.locations.models import Location

from .models import Registration, RegisteringAdult, WaitingList
from .serializers import (
    RegistrationSerializer,
    RegisteringAdultSerializer,
    RegistrationChildSerializer,
    ClassAssignmentSerializer,
    WaitingListSerializer,
)
from .utils import get_unhcr_principal_applicant


class WaitingListView(LoginRequiredMixin, ListView):
    """
    Provides the registration page with lookup types in the context
    """
    model = WaitingList
    template_name = 'registration-pilot/waitinglist.html'

    def get_context_data(self, **kwargs):

        return {
            'form': WaitingListForm({'location': self.request.user.location_id,
                                     'locations': self.request.user.locations.all()}),
        }

