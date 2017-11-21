# -*- coding: utf-8 -*-
from __future__ import absolute_import, unicode_literals
import functools
import warnings

from django.core.urlresolvers import reverse, reverse_lazy
from django.contrib.auth import (
    REDIRECT_FIELD_NAME, get_user_model, login as auth_login,
    logout as auth_logout, update_session_auth_hash,
)
from django.shortcuts import redirect
from django.views.generic import DetailView, ListView, RedirectView, UpdateView, TemplateView, FormView

from django.http import HttpResponseRedirect, HttpResponse
from django.views.decorators.debug import sensitive_post_parameters
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _
from django.utils.decorators import method_decorator

from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import translation
from student_registration.alp.templatetags.util_tags import has_group
from django.contrib.auth.views import password_change
from django.contrib.auth.forms import PasswordChangeForm

from .models import User


class UserDetailView(LoginRequiredMixin, DetailView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserRedirectView(LoginRequiredMixin, RedirectView):
    permanent = False

    def get_redirect_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})


class UserUpdateView(LoginRequiredMixin, UpdateView):

    fields = ['name', ]

    # we already imported User in the view code above, remember?
    model = User

    # send the user back to their own page after a successful update
    def get_success_url(self):
        return reverse('users:detail',
                       kwargs={'username': self.request.user.username})

    def get_object(self):
        # Only get the User record for the user making the request
        return User.objects.get(username=self.request.user.username)


class UserListView(LoginRequiredMixin, ListView):
    model = User
    # These next two lines tell the view to index lookups by username
    slug_field = 'username'
    slug_url_kwarg = 'username'


class UserChangeLanguageRedirectView(LoginRequiredMixin, RedirectView):

    permanent = False
    query_string = True
    pattern_name = 'set_language'

    def get_redirect_url(self, *args, **kwargs):
        user_language = kwargs['language']
        translation.activate(user_language)
        self.request.session[translation.LANGUAGE_SESSION_KEY] = user_language
        return reverse('home')


class LoginRedirectView(LoginRequiredMixin, RedirectView):
    permanent = True

    def get_redirect_url(self):
        if has_group(self.request.user, 'SCHOOL') or has_group(self.request.user, 'ALP_SCHOOL'):
            return reverse('schools:profile', kwargs={})
        if has_group(self.request.user, 'CLM'):
            return reverse('clm:index', kwargs={})
        if has_group(self.request.user, 'HELPDESK'):
            return reverse('helpdesk_dashboard', kwargs={})
        return reverse('home')
