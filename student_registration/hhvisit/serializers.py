
from rest_framework import serializers
from .models import  (
    HouseholdVisit ,
    SpecificReason ,
    HouseholdVisitAttempt ,
    ChildVisit ,
    MainReason ,
    ChildService ,
    ServiceType ,
    HouseholdVisitComment,
    HouseholdVisitTeam,
)
from student_registration.registrations.serializers import (
    RegisteringAdultSerializer ,
    StudentSerializer,
)

from student_registration.users.models import User


class MainReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainReason


class SpecificReasonSerializer(serializers.ModelSerializer):
    class Meta:
        model = SpecificReason


class ServiceTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceType

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


class ChildServiceSerializer(serializers.ModelSerializer):

    service_type = serializers.CharField(source='service_type.name')
    def create(self, validated_data):

        service_type_data = validated_data.pop('service_type', None)
        service_type_serializer = ServiceTypeSerializer(data=service_type_data)
        service_type_serializer.is_valid(raise_exception=True)
        service_type_serializer.instance = service_type_serializer.save()

        try:
            instance = ChildService.objects.create(**validated_data)
            instance.student = service_type_serializer.instance
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'ChildService instance': ex.message})

        return instance

    class Meta:
        model = ChildService
        fields = (
            'service_type',
            'service_provider',
        )



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
            'household_found',
            'comment',
            'date',
        )

        UserSerializer

class HouseholdVisitTeamSerializer(serializers.ModelSerializer):

    first_enumerator = serializers.CharField(source='first_enumerator.username')
    second_enumerator = serializers.CharField(source='second_enumerator.username')
    def create(self, validated_data):

        first_enumerator_data = validated_data.pop('first_enumerator', None)
        first_enumerator_serializer = UserSerializer(data=first_enumerator_data)
        first_enumerator_serializer.is_valid(raise_exception=True)
        first_enumerator_serializer.instance = first_enumerator_serializer.save()

        second_enumerator_data = validated_data.pop('second_enumerator', None)
        second_enumerator_serializer = UserSerializer(data=second_enumerator_data)
        second_enumerator_serializer.is_valid(raise_exception=True)
        second_enumerator_serializer.instance = second_enumerator_serializer.save()

        try:
            instance = HouseholdVisitTeam.objects.create(**validated_data)
            instance.first_enumerator = first_enumerator_serializer.instance
            instance.second_enumerator = second_enumerator_serializer.instance
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'HouseholdVisitTeam instance': ex.message})

        return instance

    class Meta:
        model = HouseholdVisitTeam
        fields = (
            'name',
            'first_enumerator',
            'second_enumerator',
        )


class HouseholdVisitCommentSerializer(serializers.ModelSerializer):

    def create(self, validated_data):

        try:
            instance = HouseholdVisitComment.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'HouseholdVisitComment instance': ex.message})

        return instance

    class Meta:
        model = HouseholdVisitComment
        fields = (
            'comment',
            'date',
        )

class ChildVisitSerializer(serializers.ModelSerializer):

    first_name = serializers.CharField(source='student.first_name')
    father_name = serializers.CharField(source='student.father_name')
    last_name = serializers.CharField(source='student.last_name')
    mother_fullname = serializers.CharField(source='student.mother_fullname')
    main_reason =  serializers.CharField(source='main_reason.name')
    specific_reason = serializers.CharField(source='specific_reason.name')
    child_visit_service = ChildServiceSerializer(many=True, read_only=True)
    house_hold_visit_team = HouseholdVisitTeamSerializer(many=True, read_only=True)


    def create(self, validated_data):

        student_data = validated_data.pop('student', None)
        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()

        mainreason_data = validated_data.pop('main_reason', None)
        mainreason_serializer = MainReasonSerializer(data=mainreason_data)
        mainreason_serializer.is_valid(raise_exception=True)
        mainreason_serializer.instance = MainReasonSerializer.save()

        specificreason_data = validated_data.pop('specific_reason', None)
        specificreason_serializer = SpecificReasonSerializer(data=specificreason_data)
        specificreason_serializer.is_valid(raise_exception=True)
        specificreason_serializer.instance = SpecificReasonSerializer.save()

        try:
            instance = ChildVisit.objects.create(**validated_data)
            instance.student = student_serializer.instance
            instance.main_reason = mainreason_serializer.instance
            instance.specific_reason = specificreason_serializer.instance
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'ChildVisit instance': ex.message})

        return instance

    class Meta:
        model = ChildVisit
        fields = (
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'main_reason',
            'specific_reason',
            'child_visit_service',
            'house_hold_visit_team'
        )


class HouseholdVisitSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    registeringadult_id = serializers.IntegerField(source='registering_adult.id', read_only=True)
    first_name = serializers.CharField(source='registering_adult.first_name', read_only=True)
    father_name = serializers.CharField(source='registering_adult.father_name', read_only=True)
    last_name = serializers.CharField(source='registering_adult.last_name', read_only=True)
    address = serializers.CharField(source='registering_adult.address', read_only=True)
    primary_phone = serializers.CharField(source='registering_adult.primary_phone', read_only=True)
    secondary_phone = serializers.CharField(source='registering_adult.secondary_phone', read_only=True)
    visit_attempt = VisitAttemptSerializer(many=True, read_only=True)
    children_visits = ChildVisitSerializer(many=True, read_only=True)
    visit_comment = HouseholdVisitCommentSerializer(many=True, read_only=True)
    household_visit_team = HouseholdVisitCommentSerializer(many=True, read_only=True)

    def create(self, validated_data):

        registeringadult_data = validated_data.pop('registering_adult', None)
        registeringadult_serializer = RegisteringAdultSerializer(data=registeringadult_data)
        registeringadult_serializer.is_valid(raise_exception=True)
        registeringadult_serializer.instance = RegisteringAdultSerializer.save()

        try:
            instance = HouseholdVisit.objects.create(**validated_data)
            instance.registering_adult = RegisteringAdultSerializer.instance
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'HouseholdVisit instance': ex.message})

        return instance

    class Meta:
        model = HouseholdVisit
        fields = (
            'id',
            'visit_status',
            'registeringadult_id',
            'first_name',
            'father_name',
            'last_name',
            'address',
            'primary_phone',
            'secondary_phone',
            'visit_attempt',
            'children_visits',
            'visit_comment',
            'household_visit_team'
        )
