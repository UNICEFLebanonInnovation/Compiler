# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

import json

from django.views.generic import ListView, FormView, TemplateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin

from braces.views import GroupRequiredMixin, SuperuserRequiredMixin

from student_registration.users.utils import force_default_language


class DashboardView(LoginRequiredMixin,
                    GroupRequiredMixin,
                    TemplateView):

    template_name = 'clm/bln_dashboard.html'

    group_required = [u"CLM"]

    def get_context_data(self, **kwargs):
        force_default_language(self.request)
        return {

        }
