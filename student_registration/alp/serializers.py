
from rest_framework import serializers
from .models import Outreach, ExtraColumn, Registration, Attendance
from student_registration.students.serializers import StudentSerializer


class RegistrationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Registration


class AttendanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendance


class ExtraColumnSerializer(serializers.ModelSerializer):
    class Meta:
        model = ExtraColumn


class OutreachSerializer(serializers.ModelSerializer):
    original_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)
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

    def create(self, validated_data):

        student_data = validated_data.pop('student', None)
        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()

        try:
            instance = Outreach.objects.create(**validated_data)
            instance.student = student_serializer.instance
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'instance': ex.message})

        return instance

    class Meta:
        model = Outreach
        fields = (
            'id',
            'original_id',
            'student_id',
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
            'owner',
            # 'extra_fields',
        )
