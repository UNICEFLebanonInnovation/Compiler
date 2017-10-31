
from rest_framework import serializers
from .models import Beneficiary


class BeneficiarySerializer(serializers.ModelSerializer):

    class Meta:
        model = Beneficiary
        fields = '__all__'
