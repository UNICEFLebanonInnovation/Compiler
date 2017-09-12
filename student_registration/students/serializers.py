
from rest_framework import serializers
from .models import (
    Student,
)


class StudentSerializer(serializers.ModelSerializer):
    from student_registration.alp.serializers import OutreachSerializer
    from student_registration.enrollments.serializers import EnrollmentSerializer

    id = serializers.IntegerField(read_only=True)
    number = serializers.CharField(read_only=True)
<<<<<<< HEAD
    registration = OutreachSerializer(source='last_alp_registration', read_only=True)

    alp_registrations = OutreachSerializer(read_only=True, many=True)
    secondshift_registrations = EnrollmentSerializer(read_only=True, many=True)

    current_alp_registration = OutreachSerializer(read_only=True, many=True)
    current_secondshift_registration = EnrollmentSerializer(read_only=True, many=True)
=======
    birthday = serializers.CharField(read_only=True)
    registration = OutreachSerializer(source='last_alp_registration', read_only=True)
    enrollment = EnrollmentSerializer(source='last_enrollment', read_only=True)
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1

    def create(self, validated_data):

        try:
            instance = Student.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Student instance': ex.message})

        return instance

    class Meta:
        model = Student
        fields = (
            'id',
            'first_name',
            'father_name',
            'last_name',
<<<<<<< HEAD
=======
            'full_name',
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
            'mother_fullname',
            'sex',
            'age',
            'birthday_year',
            'birthday_month',
            'birthday_day',
<<<<<<< HEAD
=======
            'birthday',
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
            'phone',
            'phone_prefix',
            'id_number',
            'id_type',
<<<<<<< HEAD
            'nationality',
            'mother_nationality',
            'address',
            'number',
            'hh_barcode',
            'registration',
            'alp_registrations',
            'secondshift_registrations',
            'current_alp_registration',
            'current_secondshift_registration',
=======
            'registered_in_unhcr',
            'nationality',
            'mother_nationality',
            'family_status',
            'address',
            'number',
            'registration',
            'enrollment',
>>>>>>> 3b9073c012bcdfc49afcb1d105deb56123ab5be1
        )
