# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals

from django.views.generic import DetailView, ListView, RedirectView, UpdateView

from django.contrib.auth.mixins import LoginRequiredMixin

from .models import Student


class StudentListView(LoginRequiredMixin, ListView):
    model = Student

    def get_queryset(self):
        return Student.objects.all()
