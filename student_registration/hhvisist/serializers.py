
from rest_framework import serializers
from .models import  WaitingList



class WaitingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaitingList
        fields = (
            'location',
            'school',
            'first_name',
            'last_name',
            'father_name',
            'unhcr_id',
            'number_of_children',
            'phone_number',
            'alternate_phone_number',
            'village',
            'owner',
        )

