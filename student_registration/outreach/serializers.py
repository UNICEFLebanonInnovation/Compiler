
from rest_framework import serializers
from .models import (
    HouseHold,
    Child
)


class HouseHoldSerializer(serializers.ModelSerializer):

    class Meta:
        model = HouseHold
        fields = (
            'name',
            'barcode_number',
            'children',
        )


class ChildSerializer(serializers.ModelSerializer):

    class Meta:
        model = Child
        fields = '__all__'
