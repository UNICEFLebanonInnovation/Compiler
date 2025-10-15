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
