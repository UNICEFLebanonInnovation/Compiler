
from rest_framework import serializers
from .models import (
    HouseHold,
)


class HouseHoldSerializer(serializers.ModelSerializer):

    class Meta:
        model = HouseHold
        fields = (
            'name',
            'barcode_number',
            'children',
        )
