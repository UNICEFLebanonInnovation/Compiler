
from rest_framework import serializers
from .models import Attendance, Absentee, CLMAttendanceStudent


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
            raise serializers.ValidationError({'Enrollment instance': ex})

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


class AttendanceExportSerializer(serializers.ModelSerializer):

    governorate = serializers.CharField(source='school.location.parent.name', read_only=True)
    district = serializers.CharField(source='school.location.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    education_year = serializers.CharField(source='education_year.name', read_only=True)
    alp_round = serializers.CharField(source='alp_round.name', read_only=True)

    class Meta:
        model = Attendance
        fields = (
            'id',
            'school_id',
            'school_name',
            'school_number',
            'school_type',
            'education_year_id',
            'education_year',
            'alp_round',
            'alp_round_id',
            'governorate',
            'district',
            'attendance_date',
            'validation_status',
            'validation_date',
            'validation_owner',
            'close_reason',
            'students',
        )


class CLMAttendanceStudentSerializer(serializers.ModelSerializer):

    governorate = serializers.CharField(source='attendance_day.school.location.parent.name', read_only=True)
    district = serializers.CharField(source='attendance_day.school.location.name', read_only=True)
    school_number = serializers.CharField(source='attendance_day.school.number', read_only=True)
    school_name = serializers.CharField(source='attendance_day.school.name', read_only=True)
    school_type = serializers.CharField(source='attendance_day.school.type', read_only=True)
    education_year = serializers.CharField(source='attendance_day.education_year.name', read_only=True)
    alp_round = serializers.CharField(source='attendance_day.alp_round.name', read_only=True)
    attendance_date = serializers.CharField(source='attendance_day.attendance_date', read_only=True)
    close_reason = serializers.CharField(source='attendance_day.close_reason', read_only=True)
    registration_level = serializers.CharField(source='attendance_day.registration_level', read_only=True)
    day_off = serializers.CharField(source='attendance_day.day_off', read_only=True)

    student_number = serializers.CharField(source='student.number', read_only=True)
    student_first_name = serializers.CharField(source='student.first_name', read_only=True)
    student_last_name = serializers.CharField(source='student.last_name', read_only=True)
    student_father_name = serializers.CharField(source='student.father_name', read_only=True)

    class Meta:
        model = CLMAttendanceStudent
        fields = (
            'school_name',
            'school_number',
            'school_type',
            'education_year',
            'alp_round',
            'governorate',
            'district',
            'attendance_date',
            'close_reason',
            'registration_level',
            'day_off',
            'student_number',
            'student_first_name',
            'student_last_name',
            'student_father_name',
            'attended',
            'absence_reason',
            'absence_reason_other',
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
