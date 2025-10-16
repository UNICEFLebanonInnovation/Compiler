"""Serializers for the BMA chatbot API."""
from __future__ import annotations

from rest_framework import serializers


class ChatHistoryMessageSerializer(serializers.Serializer):
    role = serializers.ChoiceField(choices=("user", "assistant"))
    content = serializers.CharField()


class BMAChatRequestSerializer(serializers.Serializer):
    question = serializers.CharField()
    history = ChatHistoryMessageSerializer(many=True, required=False)
    include_snapshot = serializers.BooleanField(required=False, default=False)

    def validate_question(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("Question cannot be empty.")
        return value.strip()


class BMAAgentRequestSerializer(serializers.Serializer):
    """Validate requests sent to the metrics-focused conversational agent."""

    question = serializers.CharField()
    top_k = serializers.IntegerField(min_value=1, max_value=10, required=False, default=3)
    include_suggestions = serializers.BooleanField(required=False, default=True)

    def validate_question(self, value: str) -> str:
        if not value or not value.strip():
            raise serializers.ValidationError("Question cannot be empty.")
        return value.strip()
