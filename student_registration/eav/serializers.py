
from rest_framework import serializers
from .models import Attribute, Value


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attribute


class ValueSerializer(serializers.ModelSerializer):
    class Meta:
        model = Value
