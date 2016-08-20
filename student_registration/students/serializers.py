
from rest_framework import serializers
from .models import (
    Student,
)


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
            'id_type',
            'nationality',
            'address',
        )
