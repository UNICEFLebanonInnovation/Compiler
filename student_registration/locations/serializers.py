
import json

from rest_framework import serializers
from .models import Location, Center


class LocationSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(required=True)
    name = serializers.CharField(required=False)
    name_en = serializers.CharField(required=True)
    type_id = serializers.IntegerField(required=True)
    parent_id = serializers.IntegerField(required=True)

    def create(self, validated_data):

        try:
            instance = Location.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Location instance': ex})

        return instance

    class Meta:
        model = Location
        fields = (
            'id',
            'name',
            'name_en',
            'type_id',
            'parent_id',

        )

class CenterSerializer(serializers.ModelSerializer):

    owner_name = serializers.CharField(source='owner.username', read_only=True)
    modified_by_name = serializers.CharField(source='modified_by.username', read_only=True)

    class Meta:
        model = Center
        fields = (
            'id',
            'name',
            'governorate',
            'caza',
            'cadaster',
            'longitude',
            'latitude',
            'manager_name',
            'phone_number',
            'email',
            'type',
            'provided_packages',
            'education_programs',
            'youth_programs',
            'admin_staff_number',
            'owner',
            'owner_name',
            'modified_by',
            'modified_by_name',
            'created',
            'modified',
        )




