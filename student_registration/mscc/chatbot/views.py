"""Views for the BMA chatbot."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework import permissions, status, viewsets
from rest_framework.response import Response

from .serializers import BMAChatRequestSerializer
from .services import BMAChatService


class BMAChatbotPageView(LoginRequiredMixin, TemplateView):
    """Render the HTML page that hosts the chatbot interface."""

    template_name = "mscc/bma_chatbot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("page_title", "BMA Chatbot")
        return context


class BMAChatViewSet(viewsets.ViewSet):
    """Expose the ChatGPT-powered BMA assistant as a REST endpoint."""

    permission_classes = (permissions.IsAuthenticated,)

    def create(self, request):
        serializer = BMAChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        service = BMAChatService(request.user)
        try:
            result = service.chat(
                question=serializer.validated_data["question"],
                history=serializer.validated_data.get("history"),
            )
        except BMAChatService.ChatError as exc:
            return Response(
                {"detail": str(exc)},
                status=status.HTTP_502_BAD_GATEWAY,
            )

        payload = {"answer": result["answer"]}
        if serializer.validated_data.get("include_snapshot"):
            payload["snapshot"] = result["snapshot"]
        if result.get("usage"):
            payload["usage"] = result["usage"]
        return Response(payload, status=status.HTTP_200_OK)
