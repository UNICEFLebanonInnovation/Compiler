
import json

from rest_framework import serializers
from .models import Location


class LocationSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False)
    name_en = serializers.CharField(required=True)
    type = serializers.IntegerField(required=True)
    parent = serializers.IntegerField(required=True)

    def create(self, validated_data):

        try:
            instance = Location.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Location instance': ex.message})

        return instance

    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'name_en',
            'type',
            'parent',

        )


