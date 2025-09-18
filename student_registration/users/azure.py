"""Azure Entra ID (Azure Active Directory) integration helpers."""

from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone as dt_timezone
from functools import lru_cache
from typing import Dict, Iterable, Optional, Sequence, Set

import requests
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils import timezone

try:  # pragma: no cover - the dependency is provided via requirements
    import msal
except ImportError:  # pragma: no cover
    msal = None


logger = logging.getLogger(__name__)

RISK_LEVELS = ["hidden", "none", "low", "medium", "high"]


class AzurePolicyViolation(Exception):
    """Raised when a sign-in attempt violates configured Azure AD policies."""


class AzureGraphError(Exception):
    """Raised when the Microsoft Graph API reports an unexpected error."""


@dataclass
class _TokenCache:
    """Simple bearer token cache for Microsoft Graph calls."""

    access_token: str
    expires_on: float

    def is_valid(self) -> bool:
        return time.time() < (self.expires_on - 60)


class AzureEntraIDClient:
    """Small Microsoft Graph API client focused on identity scenarios."""

    graph_base_url = "https://graph.microsoft.com/v1.0"

    def __init__(self, tenant_id: str, client_id: str, client_secret: str, timeout: float = 5.0):
        if not tenant_id or not client_id or not client_secret:
            raise ImproperlyConfigured(
                "AzureEntraIDClient requires tenant ID, client ID and client secret."  # noqa: E501
            )

        if msal is None:
            raise ImproperlyConfigured("msal must be installed to use AzureEntraIDClient.")

        self.tenant_id = tenant_id
        self.client_id = client_id
        self.client_secret = client_secret
        self.timeout = timeout
        self._app: Optional[msal.ConfidentialClientApplication] = None
        self._token_cache: Optional[_TokenCache] = None

    def _application(self) -> "msal.ConfidentialClientApplication":
        if self._app is None:
            authority = f"https://login.microsoftonline.com/{self.tenant_id}"
            self._app = msal.ConfidentialClientApplication(
                client_id=self.client_id,
                client_credential=self.client_secret,
                authority=authority,
            )

        return self._app

    def _acquire_token(self) -> str:
        if self._token_cache and self._token_cache.is_valid():
            return self._token_cache.access_token

        app = self._application()
        scopes = ["https://graph.microsoft.com/.default"]

        result = app.acquire_token_silent(scopes, account=None)
        if not result:
            result = app.acquire_token_for_client(scopes=scopes)

        if "access_token" not in result:
            error = result.get("error_description") or result
            raise AzureGraphError(f"Unable to acquire Microsoft Graph token: {error}")

        self._token_cache = _TokenCache(
            access_token=result["access_token"],
            expires_on=float(result.get("expires_on", time.time() + 300)),
        )

        return self._token_cache.access_token

    def _request(self, method: str, path: str, **kwargs) -> Optional[Dict]:
        url = f"{self.graph_base_url}{path}"
        headers = kwargs.pop("headers", {})
        headers.setdefault("Authorization", f"Bearer {self._acquire_token()}")
        headers.setdefault("Accept", "application/json")

        response = requests.request(method, url, headers=headers, timeout=self.timeout, **kwargs)

        if response.status_code == 404:
            return None

        if response.status_code == 204:
            return {}

        if not response.ok:
            raise AzureGraphError(
                f"Microsoft Graph call to {url} failed: {response.status_code} {response.text}"
            )

        return response.json()

    def get_user_risk(self, object_id: str) -> Optional[Dict]:
        """Return the risky user payload if Microsoft Identity Protection flagged the user."""

        path = f"/identityProtection/riskyUsers/{object_id}"
        return self._request("GET", path)

    def get_active_role_ids(self, object_id: str) -> Set[str]:
        """Return active Azure AD role assignment IDs for the provided principal."""

        params = {
            "$filter": f"principalId eq '{object_id}' and status eq 'Active'",
        }
        payload = self._request(
            "GET",
            "/roleManagement/directory/roleAssignmentScheduleInstances",
            params=params,
        )

        values = payload.get("value", []) if payload else []
        return {item.get("roleDefinitionId") for item in values if item.get("roleDefinitionId")}


class AzureIdentityService:
    """Central orchestrator that enforces Azure AD sign-in policies."""

    def __init__(
        self,
        client: Optional[AzureEntraIDClient],
        *,
        require_mfa: bool = True,
        accepted_mfa_claims: Sequence[str] = ("mfa",),
        conditional_access_claims: Sequence[str] = (),
        required_role_ids: Sequence[str] = (),
        risk_threshold: str = "medium",
        token_max_age: Optional[int] = 3600,
        token_leeway: int = 120,
        identity_protection_enabled: bool = True,
    ) -> None:
        self.client = client
        self.require_mfa = require_mfa
        self.accepted_mfa_claims = set(accepted_mfa_claims or [])
        self.conditional_access_claims = tuple(conditional_access_claims or [])
        self.required_role_ids = {role for role in required_role_ids if role}
        self.token_max_age = token_max_age
        self.token_leeway = token_leeway
        self.identity_protection_enabled = identity_protection_enabled

        risk_threshold_normalized = (risk_threshold or "medium").lower()
        self._risk_threshold_index = self._risk_to_index(risk_threshold_normalized)

        self._tenant_id = settings.AZURE_AD_TENANT_ID

    @property
    def enabled(self) -> bool:
        return any(
            [
                self.require_mfa,
                self.conditional_access_claims,
                self.token_max_age,
                self.identity_protection_enabled and self.client,
            ]
        )

    @staticmethod
    def _risk_to_index(level: str) -> int:
        try:
            return RISK_LEVELS.index(level)
        except ValueError:
            logger.warning("Unknown Azure AD risk level '%s'; defaulting to 'medium'.", level)
            return RISK_LEVELS.index("medium")

    def validate_login(
        self,
        user,
        extra_data: Optional[Dict],
        *,
        request=None,
    ) -> None:
        """Validate the Azure AD token and associated Microsoft Graph state."""

        if extra_data is None:
            extra_data = {}

        self._enforce_tenant(extra_data)
        self._ensure_token_hygiene(extra_data)

        if self.require_mfa:
            self._enforce_mfa(extra_data)

        if self.conditional_access_claims:
            self._enforce_conditional_access(extra_data)

        if self.identity_protection_enabled and self.client:
            self._enforce_identity_protection(extra_data)
            self._enforce_privileged_identity_management(user, extra_data)

        if request is not None:
            request.session["azure_auth_metadata"] = {
                "oid": extra_data.get("oid"),
                "tid": extra_data.get("tid"),
                "amr": extra_data.get("amr", []),
                "risk_checked": bool(self.identity_protection_enabled and self.client),
                "validated_at": timezone.now().isoformat(),
            }

    def _enforce_tenant(self, extra_data: Dict) -> None:
        tenant_id = self._tenant_id
        if not tenant_id:
            return

        token_tenant = extra_data.get("tid")
        if token_tenant and token_tenant.lower() == tenant_id.lower():
            return

        raise AzurePolicyViolation("Sign-in does not originate from the expected Azure AD tenant.")

    def _ensure_token_hygiene(self, extra_data: Dict) -> None:
        now = timezone.now()
        leeway = timedelta(seconds=self.token_leeway)

        issued_at = self._claim_to_datetime(extra_data.get("iat"))
        not_before = self._claim_to_datetime(extra_data.get("nbf"))
        expires_at = self._claim_to_datetime(extra_data.get("exp"))

        if self.token_max_age and issued_at:
            max_age = timedelta(seconds=self.token_max_age)
            if now - issued_at > (max_age + leeway):
                raise AzurePolicyViolation("Azure AD token is older than the permitted maximum age.")

        if not_before and now + leeway < not_before:
            raise AzurePolicyViolation("Azure AD token is not yet valid.")

        if expires_at and now - leeway >= expires_at:
            raise AzurePolicyViolation("Azure AD token has expired.")

    @staticmethod
    def _claim_to_datetime(value) -> Optional[datetime]:
        if value in (None, ""):
            return None

        try:
            timestamp = int(value)
        except (TypeError, ValueError):
            logger.debug("Unable to parse datetime claim from value '%s'", value)
            return None

        return datetime.fromtimestamp(timestamp, tz=dt_timezone.utc)

    def _enforce_mfa(self, extra_data: Dict) -> None:
        amr = extra_data.get("amr")

        if isinstance(amr, str):
            amr_values = {amr}
        elif isinstance(amr, Iterable):
            amr_values = {item for item in amr}
        else:
            amr_values = set()

        if self.accepted_mfa_claims.intersection(amr_values):
            return

        raise AzurePolicyViolation("Multi-factor authentication is required for this application.")

    def _enforce_conditional_access(self, extra_data: Dict) -> None:
        for claim in self.conditional_access_claims:
            if extra_data.get(claim):
                continue

            raise AzurePolicyViolation(
                f"Conditional access requirement '{claim}' was not satisfied by the sign-in token."
            )

    def _enforce_identity_protection(self, extra_data: Dict) -> None:
        object_id = extra_data.get("oid") or extra_data.get("sub")

        if not object_id:
            logger.warning("Azure AD extra_data missing object identifier; skipping risk evaluation.")
            return

        try:
            payload = self.client.get_user_risk(object_id)
        except AzureGraphError as exc:
            logger.error("Unable to verify Azure AD identity protection state: %s", exc)
            raise AzurePolicyViolation("Unable to validate Azure AD sign-in risk.") from exc

        if not payload:
            return

        risk_level = (payload.get("riskLevel") or "none").lower()
        risk_index = self._risk_to_index(risk_level)

        if risk_index >= self._risk_threshold_index:
            raise AzurePolicyViolation(
                "Azure AD sign-in was blocked because the risk level exceeds the configured threshold."
            )

    def _enforce_privileged_identity_management(self, user, extra_data: Dict) -> None:
        if not user or not (getattr(user, "is_staff", False) or getattr(user, "is_superuser", False)):
            return

        if not self.required_role_ids:
            return

        object_id = extra_data.get("oid") or extra_data.get("sub")

        if not object_id:
            raise AzurePolicyViolation("Privileged Azure AD users must expose their directory object ID.")

        try:
            active_roles = self.client.get_active_role_ids(object_id)
        except AzureGraphError as exc:
            logger.error("Unable to evaluate Azure AD privileged role assignments: %s", exc)
            raise AzurePolicyViolation("Unable to validate privileged role activation via PIM.") from exc

        if not active_roles.issuperset(self.required_role_ids):
            raise AzurePolicyViolation(
                "Privileged role activation via Azure AD PIM is required before accessing the application."
            )


@lru_cache(maxsize=1)
def get_identity_service() -> Optional[AzureIdentityService]:
    """Return a cached AzureIdentityService instance configured from settings."""

    tenant_id = settings.AZURE_AD_TENANT_ID
    client_id = settings.AZURE_AD_CLIENT_ID
    client_secret = settings.AZURE_AD_CLIENT_SECRET

    client = None
    if tenant_id and client_id and client_secret:
        try:
            client = AzureEntraIDClient(
                tenant_id=tenant_id,
                client_id=client_id,
                client_secret=client_secret,
                timeout=settings.AZURE_GRAPH_TIMEOUT,
            )
        except ImproperlyConfigured as exc:
            logger.warning("Azure Entra ID client could not be initialised: %s", exc)
            client = None

    service = AzureIdentityService(
        client,
        require_mfa=settings.AZURE_REQUIRE_MFA,
        accepted_mfa_claims=settings.AZURE_ACCEPTED_MFA_CLAIMS,
        conditional_access_claims=settings.AZURE_CONDITIONAL_ACCESS_CLAIMS,
        required_role_ids=settings.AZURE_PIM_REQUIRED_ROLE_IDS,
        risk_threshold=settings.AZURE_RISK_THRESHOLD,
        token_max_age=settings.AZURE_TOKEN_MAX_AGE,
        token_leeway=settings.AZURE_TOKEN_LEEWAY,
        identity_protection_enabled=settings.AZURE_IDENTITY_PROTECTION_ENABLED,
    )

    return service
