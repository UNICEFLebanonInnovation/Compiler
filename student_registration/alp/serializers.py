
from rest_framework import serializers
from .models import Outreach


class OutreachSerializer(serializers.ModelSerializer):
    original_id = serializers.IntegerField(source='id', read_only=True)
    student_full_name = serializers.CharField(source='student.full_name')
    student_mother_fullname = serializers.CharField(source='student.mother_fullname')
    student_sex = serializers.CharField(source='student.sex')
    student_birthday_year = serializers.CharField(source='student.birthday_year')
    student_birthday_month = serializers.CharField(source='student.birthday_month')
    student_birthday_day = serializers.CharField(source='student.birthday_day')
    student_phone = serializers.CharField(source='student.phone')
    student_id_number = serializers.CharField(source='student.id_number')
    student_nationality = serializers.CharField(source='student.nationality')
    student_address = serializers.CharField(source='student.address')
    partner_name = serializers.CharField(source='partner.name', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    location_name = serializers.CharField(source='location.name', read_only=True)
    preferred_language_name = serializers.CharField(source='preferred_language.name', read_only=True)
    last_education_level_name = serializers.CharField(source='last_education_level.name', read_only=True)
    last_class_level_name = serializers.CharField(source='last_class_level.name', read_only=True)

    class Meta:
        model = Outreach
        fields = (
            'id',
            'original_id',
            'student',
            'student_full_name',
            'student_mother_fullname',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'student_phone',
            'student_id_number',
            'student_nationality',
            'student_address',
            'partner',
            'partner_name',
            'school',
            'school_name',
            'school_number',
            'location',
            'location_name',
            'preferred_language',
            'preferred_language_name',
            'last_education_level',
            'last_education_level_name',
            'last_class_level',
            'last_class_level_name',
            'last_education_year',
            'average_distance',
            'exam_year',
            'exam_month',
            'exam_day',
        )
