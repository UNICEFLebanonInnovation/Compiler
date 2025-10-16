from django.conf import settings
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import ImproperlyConfigured
from django.urls import reverse_lazy
from django.views.generic import TemplateView
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .serializers import VannaQuerySerializer
from .services import get_vanna_service


class VannaQueryViewSet(viewsets.ViewSet):
    """Expose a simple API endpoint to query Vanna."""

    permission_classes = [permissions.IsAuthenticated]
    serializer_class = VannaQuerySerializer

    def create(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        configuration = getattr(settings, "VANNA", {})
        if not configuration.get("ENABLED"):
            return Response(
                {"detail": "Vanna integration is currently disabled."},
                status=status.HTTP_503_SERVICE_UNAVAILABLE,
            )

        try:
            service = get_vanna_service()
            payload = service.ask(**serializer.validated_data)
        except ImproperlyConfigured as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response(payload, status=status.HTTP_200_OK)


class VannaConsoleView(LoginRequiredMixin, TemplateView):
    """Render the conversational console for the Vanna assistant."""

    template_name = "ai/vanna_console.html"
    login_url = reverse_lazy("account_login")

    def get_context_data(self, **kwargs):  # type: ignore[override]
        context = super().get_context_data(**kwargs)
        configuration = getattr(settings, "VANNA", {})
        context.update(
            {
                "vanna_enabled": configuration.get("ENABLED", False),
                "api_endpoint": reverse_lazy("vanna-list"),
            }
        )
        return context
