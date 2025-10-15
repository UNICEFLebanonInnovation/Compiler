"""Views for the BMA chatbot."""
from __future__ import annotations

from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView
from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response

from .agent import BMAMetricsAgent
from .serializers import BMAAgentRequestSerializer, BMAChatRequestSerializer
from .services import BMAChatService


class BMAChatbotPageView(LoginRequiredMixin, TemplateView):
    """Render the HTML page that hosts the chatbot interface."""

    template_name = "mscc/bma_chatbot.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("page_title", "BMA Chatbot")
        return context


class BMAMetricsAgentPageView(LoginRequiredMixin, TemplateView):
    """Render the HTML page used to interact with the metrics agent."""

    template_name = "mscc/bma_metrics_agent.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.setdefault("page_title", "BMA Metrics Assistant")
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
                status=exc.status_code or status.HTTP_502_BAD_GATEWAY,
            )

        payload = {"answer": result["answer"]}
        if serializer.validated_data.get("include_snapshot"):
            payload["snapshot"] = result["snapshot"]
        if result.get("usage"):
            payload["usage"] = result["usage"]
        return Response(payload, status=status.HTTP_200_OK)

    @action(detail=False, methods=["post"], url_path="metrics-agent")
    def metrics_agent(self, request):
        serializer = BMAAgentRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        agent = BMAMetricsAgent(request.user)
        try:
            result = agent.answer(
                serializer.validated_data["question"],
                top_k=serializer.validated_data.get("top_k", 3),
                include_suggestions=serializer.validated_data.get("include_suggestions", True),
            )
        except BMAMetricsAgent.AgentError as exc:
            return Response({"detail": str(exc)}, status=exc.status_code)

        return Response(result, status=status.HTTP_200_OK)
