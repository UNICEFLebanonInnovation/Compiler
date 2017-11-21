
from rest_framework import serializers
from .models import (
    School,
    ClassRoom,
    Section,
)


class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School
        fields = '__all__'


class ClassRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassRoom
        fields = (
            'id',
            'name',
        )


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
