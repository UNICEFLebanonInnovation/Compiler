
from rest_framework import serializers
from .models import Attendance


class AttendanceSerializer(serializers.ModelSerializer):
    original_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_full_name = serializers.CharField(source='student.full_name')
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)

    class Meta:
        model = Attendance
        fields = (
            'id',
            'original_id',
            'student_id',
            'student_full_name',
            'classroom',
            'classroom_name',
            'status',
            'attendance_date',
            'owner',
            'validation_status',
            'validation_date',
            'validation_owner',
        )
