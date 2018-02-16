
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

    # student_full_name = serializers.CharField(source='student.full_name', read_only=True)
    # student_first_name = serializers.CharField(source='student.first_name', read_only=True)
    # student_father_name = serializers.CharField(source='student.father_name', read_only=True)
    # student_last_name = serializers.CharField(source='student.last_name', read_only=True)
    # student_number = serializers.CharField(source='student.number', read_only=True)
    # student_sex = serializers.CharField(source='student.sex', read_only=True)
    # student_birthday_day = serializers.CharField(source='student.birthday_day', read_only=True)
    # student_birthday_month = serializers.CharField(source='student.birthday_month', read_only=True)
    # student_birthday_year = serializers.CharField(source='student.birthday_year', read_only=True)
    # school_name = serializers.CharField(source='school.name', read_only=True)
    # school_id = serializers.IntegerField(source='school.id', read_only=True)
    # school_location = serializers.CharField(source='school.location.name', read_only=True)
    # school_location_id = serializers.CharField(source='school.location.id', read_only=True)

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

            # 'school_id',
            # 'school_name',
            # 'school_location',
            # 'school_location_id',
            # 'student_number',
            # 'student_full_name',
            # 'student_first_name',
            # 'student_father_name',
            # 'student_last_name',
            # 'student_sex',
            # 'reattend_date',
            # 'student_birthday_day',
            # 'student_birthday_month',
            # 'student_birthday_year',
        )
