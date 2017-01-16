
from rest_framework import serializers
from .models import Attendance, Absentee


class AttendanceSerializer(serializers.ModelSerializer):
    original_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_full_name = serializers.CharField(source='student.full_name')
    student_sex = serializers.CharField(source='student.sex')
    school_name = serializers.CharField(source='school.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    state = serializers.IntegerField(source='status', read_only=True)

    class Meta:
        model = Attendance
        fields = (
            'id',
            'original_id',
            'student_id',
            'student_full_name',
            'student_sex',
            'school',
            'school_name',
            'classroom',
            'classroom_name',
            'status',
            'state',
            'attendance_date',
            'owner',
            'validation_status',
            'validation_date',
            'validation_owner',
        )


class AbsenteeSerializer(serializers.ModelSerializer):
    school_id = serializers.IntegerField(source='school.id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_full_name = serializers.CharField(source='student.full_name')
    student_number = serializers.CharField(source='student.number')
    student_sex = serializers.CharField(source='student.sex')
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_location = serializers.CharField(source='school.location.name', read_only=True)

    class Meta:
        model = Absentee
        fields = (
            'school_id',
            'school_name',
            'school_location',
            'student_id',
            'student_number',
            'student_full_name',
            'student_sex',
            'last_attendance_date',
            'absent_days',
            'reattend_date',
        )
