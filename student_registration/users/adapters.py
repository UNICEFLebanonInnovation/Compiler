# -*- coding: utf-8 -*-
from django.conf import settings
from django.core.exceptions import PermissionDenied
from allauth.account.adapter import DefaultAccountAdapter
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter

from .azure import AzurePolicyViolation, get_identity_service


class AccountAdapter(DefaultAccountAdapter):
    def is_open_for_signup(self, request):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)


class SocialAccountAdapter(DefaultSocialAccountAdapter):
    def is_open_for_signup(self, request, sociallogin):
        return getattr(settings, 'ACCOUNT_ALLOW_REGISTRATION', True)

    def pre_social_login(self, request, sociallogin):
        service = get_identity_service()

        if service and service.enabled:
            extra_data = sociallogin.account.extra_data or {}

            try:
                service.validate_login(
                    sociallogin.user,
                    extra_data,
                    request=request,
                )
            except AzurePolicyViolation as exc:
                raise PermissionDenied(str(exc))

        return super().pre_social_login(request, sociallogin)
