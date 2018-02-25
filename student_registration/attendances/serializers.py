
from rest_framework import serializers
from .models import Attendance, Absentee


class AttendanceSerializer(serializers.ModelSerializer):
    school_type = serializers.CharField(required=False)
    close_reason = serializers.CharField(required=False)
    validation_status = serializers.BooleanField(required=False)
    validation_date = serializers.DateField(required=False)
    validation_owner = serializers.IntegerField(source='validation_owner_id', required=False)
    # students = serializers.JSONField(required=False)

    def create(self, validated_data):
        from student_registration.alp.models import ALPRound
        from student_registration.schools.models import EducationYear

        try:
            instance = Attendance.objects.create(**validated_data)
            if instance.school_type == 'ALP':
                alp_round = ALPRound.objects.get(current_round=True)
                instance.alp_round = alp_round
            if instance.school_type == '2nd-shift':
                education_year = EducationYear.objects.get(current_year=True)
                instance.education_year = education_year
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Enrollment instance': ex.message})

        return instance

    class Meta:
        model = Attendance
        fields = (
            'id',
            'school',
            'school_type',
            'attendance_date',
            'validation_status',
            'validation_date',
            'validation_owner',
            'close_reason',
            'total_enrolled',
            'students',
            'owner',
        )


class AbsenteeSerializer(serializers.ModelSerializer):
    student_id = serializers.IntegerField(source='student.id', read_only=True)

    class Meta:
        model = Absentee
        fields = (
            'student_id',
            'absence_type',
            'absent_days',
            'last_attendance_date',
            'last_absent_date',
            'total_absent_days',
            'total_attended_days',
            'last_modification_date',
        )
