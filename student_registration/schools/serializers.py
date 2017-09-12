
from rest_framework import serializers
from .models import (
    School,
    ClassRoom,
    Section,
<<<<<<< HEAD
    Grade
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
)


class SchoolSerializer(serializers.ModelSerializer):

    class Meta:
        model = School


class ClassRoomSerializer(serializers.ModelSerializer):

<<<<<<< HEAD
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)

=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
    class Meta:
        model = ClassRoom
        fields = (
            'id',
            'name',
<<<<<<< HEAD
            'school',
            'school_name',
            'school_number',
            'grade',
            'grade_name',
            'section',
            'section_name'
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
        )


class SectionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Section
<<<<<<< HEAD


class GradeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Grade
=======
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
