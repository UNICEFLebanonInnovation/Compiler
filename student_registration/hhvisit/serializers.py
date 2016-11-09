
from rest_framework import serializers
from .models import  HouseholdVisit , SpecificReason , HouseholdVisitAttempt
from student_registration.registrations.serializers import RegisteringAdultSerializer


class HouseholdVisitSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    #visitattempts = serializers.CharField(source='test', read_only=True)

    #testx = serializers.CharField(source='test', read_only=True)
    #visit_attempt = VisitAttemptSerializer(many=True, read_only=True)


    # visitattempts = VisitAttemptSerializer(many=True, read_only=True)
    # registeringadult_id = serializers.IntegerField(source='registeringadult.id', read_only=True)
    # first_name = serializers.CharField(source='registeringadult.first_name')
    # father_name = serializers.CharField(source='registeringadult.father_name')
    # last_name = serializers.CharField(source='registeringadult.last_name')
    # address = serializers.CharField(source='registeringadult.address')
    # primary_phone = serializers.CharField(source='registeringadult.primary_phone')
    # secondary_phone = serializers.CharField(source='registeringadult.secondary_phone')

    def create(self, validated_data):

        registeringadult_data = validated_data.pop('registeringadult', None)
        registeringadult_serializer = RegisteringAdultSerializer(data=registeringadult_data)
        registeringadult_serializer.is_valid(raise_exception=True)
        registeringadult_serializer.instance = registeringadult_serializer.save()

        try:
            instance = HouseholdVisit.objects.create(**validated_data)
            instance.registeringadult = registeringadult_serializer.instance
            instance.test = 'test'
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'HouseholdVisit instance': ex.message})

        return instance

    class Meta:
        model = HouseholdVisit
        fields = (
            'id',
            #'visit_attempt'
        )
        # fields = (
        #     'registeringadult_id',
        #     'first_name',
        #     'father_name',
        #     'last_name',
        #     'address',
        #     'primary_phone',
        #     'secondary_phone',
        # )

class SpecificReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificReason

class VisitAttemptSerializer(serializers.ModelSerializer):

    def create(self, validated_data):

        try:
            instance = HouseholdVisitAttempt.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'HouseholdVisitAttempt instance': ex.message})

        return instance

    class Meta:
        model = HouseholdVisitAttempt
        fields = (
            # 'household_found',
            # 'comment',
            # 'date',
        )




