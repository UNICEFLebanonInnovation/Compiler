
from rest_framework import serializers
from .models import (
    Student,
    School,
    ClassRoom,
    Section,
    Grade
)


class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School


class ClassRoomSerializer(serializers.ModelSerializer):

    class Meta:
        model = ClassRoom


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section


class GradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grade


class StudentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

    class Meta:
        model = Student
        fields = (
            'id',
            'full_name',
            'mother_fullname',
            'sex',
            'birthday_year',
            'birthday_month',
            'birthday_day',
            'phone',
            'id_number',
            'nationality',
            'address',
        )
