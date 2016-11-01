
from rest_framework import serializers
from .models import  HouseholdVisit



class HouseholdVisitSerializer(serializers.ModelSerializer):

    class Meta:
        model = HouseholdVisit
        fields = (
            'registering_adult',
            'owner',
        )

