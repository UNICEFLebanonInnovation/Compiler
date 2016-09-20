
from rest_framework import serializers
from .models import (
    Student,
)


class StudentSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)

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
