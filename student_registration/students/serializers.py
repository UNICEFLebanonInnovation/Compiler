
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

    school_name = serializers.CharField(source='school.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)

    class Meta:
        model = ClassRoom
        fields = (
            'id',
            'name',
            'school',
            'school_name',
            'school_number',
            'grade',
            'grade_name',
            'section',
            'section_name'
        )


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
