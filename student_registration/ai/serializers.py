from rest_framework import serializers


class VannaQuerySerializer(serializers.Serializer):
    """Serializer validating the payload for Vanna questions."""

    question = serializers.CharField(help_text="Natural language question to pass to Vanna")
    run_sql = serializers.BooleanField(
        required=False,
        default=False,
        help_text="Execute the generated SQL and return the resulting dataset.",
    )
