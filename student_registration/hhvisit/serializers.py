
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
)
from student_registration.registrations.serializers import (
    RegisteringAdultSerializer ,
    StudentSerializer,
    RegistrationChildSerializer
)

from student_registration.users.models import User

from collections import OrderedDict

from rest_framework.fields import (  # NOQA # isort:skip
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty
)

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

    service_type_id = serializers.CharField(source='service_type.id')
    service_type = serializers.CharField(source='service_type.name')

    child_visit_id = serializers.IntegerField()

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
            'id',
            'service_type_id',
            'service_type',
            'service_provider',
            'child_visit_id'
        )



class VisitAttemptSerializer(serializers.ModelSerializer):

    household_visit_id = serializers.IntegerField()

    #id = serializers.IntegerField()
    #
    # household_found = serializers.BooleanField()
    #
    # comment = serializers.CharField()
    #
    # date = serializers.DateTimeField()


    # def create(self, validated_data):
    #
    #     try:
    #
    #         instance = HouseholdVisitAttempt.objects.create(**validated_data)
    #
    #
    #     except Exception as ex:
    #         raise serializers.ValidationError({'HouseholdVisitAttempt instance': ex.message})
    #
    #     return instance
    #
    # def update(self, instance, validated_data):
    #
    #     return instance

    class Meta:
        model = HouseholdVisitAttempt
        fields = (
            'id',
            'household_found',
            'comment',
            'date',
            'household_visit_id'
        )


class HouseholdVisitCommentSerializer(serializers.ModelSerializer):

    household_visit_id = serializers.IntegerField()

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
            'id',
            'comment',
            'date',
            'household_visit_id'
        )

class ChildVisitSerializer(serializers.ModelSerializer):

    student_id = serializers.CharField(source='student.id')
    first_name = serializers.CharField(source='student.first_name')
    father_name = serializers.CharField(source='student.father_name')
    last_name = serializers.CharField(source='student.last_name')
    mother_fullname = serializers.CharField(source='student.mother_fullname')
    # school = serializers.CharField(source='')
    main_reason_id = serializers.CharField(source='main_reason.id')
    main_reason =  serializers.CharField(source='main_reason.name')
    specific_reason_id = serializers.CharField(source='specific_reason.id')
    specific_reason = serializers.CharField(source='specific_reason.name')
    child_visit_service = ChildServiceSerializer(many=True, read_only=True)
    household_visit_id = serializers.IntegerField()

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
            'id',
            'student_id',
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'main_reason_id',
            'main_reason',
            'specific_reason_id',
            'specific_reason',
            'child_visit_service',
            'household_visit_id',
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
    all_visit_attempt_count = serializers.CharField(read_only=True)
    visit_attempt_count = serializers.CharField(read_only=True)
    child_visit_count = serializers.CharField(read_only=True)
    visit_status = serializers.CharField()

    def create(self, validated_data):

        instance = HouseholdVisit.objects.create(**validated_data)

        return instance

    def update(self, instance, validated_data):

        allInitialDataResult = self.get_all_initial()

        attempts_data = allInitialDataResult['visit_attempt']

        for attempt in attempts_data:

            attempt['id'] = (attempt['id'] if attempt['id'] else None)
            attemptRecord = HouseholdVisitAttempt.objects.filter(id=(attempt['id'])).first()
            attemptSerializer = VisitAttemptSerializer(attemptRecord, data=attempt)
            attemptSerializer.is_valid(raise_exception=True)
            attemptSerializer.save()

        # attempts_data = allInitialDataResult['visit_attempt']
        #
        # for attempt in attempts_data:
        #     attempt['id'] = (attempt['id'] if attempt['id'] else None)
        #     attemptRecord = HouseholdVisitAttempt.objects.filter(id=(attempt['id'])).first()
        #     attemptSerializer = VisitAttemptSerializer(attemptRecord, data=attempt)
        #     attemptSerializer.is_valid(raise_exception=True)
        #     attemptSerializer.save()
        #
        #     attempts_data = attempt['visit_attempt']
        #
        #     for attempt in attempts_data:
        #         attempt['id'] = (attempt['id'] if attempt['id'] else None)
        #         attemptRecord = HouseholdVisitAttempt.objects.filter(id=(attempt['id'])).first()
        #         attemptSerializer = VisitAttemptSerializer(attemptRecord, data=attempt)
        #         attemptSerializer.is_valid(raise_exception=True)
        #         attemptSerializer.save()
        #
        # attempts_data = allInitialDataResult['visit_attempt']
        #
        # for attempt in attempts_data:
        #     attempt['id'] = (attempt['id'] if attempt['id'] else None)
        #     attemptRecord = HouseholdVisitAttempt.objects.filter(id=(attempt['id'])).first()
        #     attemptSerializer = VisitAttemptSerializer(attemptRecord, data=attempt)
        #     attemptSerializer.is_valid(raise_exception=True)
        #     attemptSerializer.save()
        #

        return instance

    def get_all_initial(self):
        if hasattr(self, 'initial_data'):
            return OrderedDict([
                                   (field_name, field.get_value(self.initial_data))
                                   for field_name, field in self.fields.items()
                                   if (field.get_value(self.initial_data) is not empty)
                                   ])

        return OrderedDict([
                               (field.field_name, field.get_initial())
                               for field in self.fields.values()
                               ])

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
            'all_visit_attempt_count',
            'visit_attempt_count',
            'child_visit_count'
        )


