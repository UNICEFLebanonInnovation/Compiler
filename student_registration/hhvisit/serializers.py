
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
    ChildReason
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


    service_type_id = serializers.IntegerField()
    service_type = serializers.CharField(source='service_type.name', read_only=True)

    child_visit_id = serializers.IntegerField()

    # def create(self, validated_data):
    #
    #     service_type_data = validated_data.pop('service_type', None)
    #     service_type_serializer = ServiceTypeSerializer(data=service_type_data)
    #     service_type_serializer.is_valid(raise_exception=True)
    #     service_type_serializer.instance = service_type_serializer.save()
    #
    #     try:
    #         instance = ChildService.objects.create(**validated_data)
    #         instance.student = service_type_serializer.instance
    #         instance.save()
    #
    #     except Exception as ex:
    #         raise serializers.ValidationError({'ChildService instance': ex.message})
    #
    #     return instance

    class Meta:
        model = ChildService
        fields = (
            'id',
            'service_type_id',
            'service_type',
            'service_provider',
            'service_provider_followup',
            'child_visit_id',
            'service_date'
        )


class ChildReasonSerializer(serializers.ModelSerializer):

    main_reason_id = serializers.IntegerField(allow_null=True, required=False)
    main_reason = serializers.CharField(source='main_reason.name', read_only=True)
    specific_reason_id = serializers.IntegerField(allow_null=True, required=False)
    specific_reason = serializers.CharField(source='specific_reason.name', read_only=True)
    child_visit_id = serializers.IntegerField()

    class Meta:
        model = ChildReason
        fields = (
            'id',
            'main_reason_id',
            'main_reason',
            'specific_reason_id',
            'specific_reason',
            'specific_reason_other_specify',
            'child_visit_id',
            'reason_date'
        )


class VisitAttemptSerializer(serializers.ModelSerializer):

    household_visit_id = serializers.IntegerField()

    #id = serializers.IntegerField()
    #
    # household_not_found = serializers.BooleanField()
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
            'household_not_found',
            'comment',
            'date',
            'household_visit_id'
        )


class HouseholdVisitCommentSerializer(serializers.ModelSerializer):

    household_visit_id = serializers.IntegerField()

    # def create(self, validated_data):
    #
    #     try:
    #         instance = HouseholdVisitComment.objects.create(**validated_data)
    #         instance.save()
    #
    #     except Exception as ex:
    #         raise serializers.ValidationError({'HouseholdVisitComment instance': ex.message})
    #
    #     return instance

    class Meta:
        model = HouseholdVisitComment
        fields = (
            'id',
            'comment',
            'date',
            'household_visit_id'
        )

class ChildVisitSerializer(serializers.ModelSerializer):

    student_id = serializers.CharField(source='student.id', read_only=True)
    first_name = serializers.CharField(source='student.first_name', read_only=True)
    father_name = serializers.CharField(source='student.father_name', read_only=True)
    last_name = serializers.CharField(source='student.last_name', read_only=True)
    mother_fullname = serializers.CharField(source='student.mother_fullname', read_only=True)
    calculate_age = serializers.CharField(source='student.calculate_age', read_only=True)
    child_school = serializers.CharField(read_only=True)
    child_classroom = serializers.CharField(read_only=True)
    child_visit_service = ChildServiceSerializer(many=True, read_only=True)
    child_visit_reason = ChildReasonSerializer(many=True, read_only=True)
    household_visit_id = serializers.IntegerField()

    def create(self, validated_data):

        student_data = validated_data.pop('student', None)
        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()

        try:
            instance = ChildVisit.objects.create(**validated_data)
            instance.student = student_serializer.instance
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
            'calculate_age',
            'child_enrolled_in_another_school',
            'child_no_longer_living_in_the_pilot_area',
            'child_visit_service',
            'child_visit_reason',
            'household_visit_id',
            'child_school',
            'child_classroom',
            'child_absence_period'
        )


class HouseholdVisitSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    registeringadult_id = serializers.IntegerField(source='registering_adult.id', read_only=True)
    registeringadult_id_number= serializers.CharField(source='registering_adult.id_number', read_only=True)
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

            if not attempt['id']:
                attempt.pop('id')

            attemptSerializer = VisitAttemptSerializer(attemptRecord, data=attempt)
            attemptSerializer.is_valid(raise_exception=True)
            attemptSerializer.save()

        children_data = allInitialDataResult['children_visits']

        childIdentifiers = [x['id'] for x in children_data]

        childServiceIdentifierLists= [[y['id'] for y in x['child_visit_service']] for x in children_data]
        childServiceIdentifiers = [val for sublist in childServiceIdentifierLists for val in sublist]
        ChildService.objects.filter(child_visit_id__in=childIdentifiers).exclude(id__in=childServiceIdentifiers).delete()

        childReasonIdentifierLists= [[y['id'] for y in x['child_visit_reason']] for x in children_data]
        childReasonIdentifiers = [val for sublist in childReasonIdentifierLists for val in sublist]
        ChildReason.objects.filter(child_visit_id__in=childIdentifiers).exclude(id__in=childReasonIdentifiers).delete()

        for child_data in children_data:
            child_data['id'] = (child_data['id'] if child_data['id'] else None)
            childRecord = ChildVisit.objects.filter(id=(child_data['id'])).first()

            if not child_data['id']:
                child_data.pop('id')

            childSerializer = ChildVisitSerializer(childRecord, data=child_data )
            childSerializer.is_valid(raise_exception=True)
            childSerializer.save()

            services_data = child_data['child_visit_service']

            for service_data in services_data:
                service_data['id'] = (service_data['id'] if service_data['id'] else None)

                serviceRecord = ChildService.objects.filter(id=(service_data['id'])).first()

                if not service_data['id']:
                    service_data.pop('id')

                serviceSerializer = ChildServiceSerializer(serviceRecord, data=service_data)

                serviceSerializer.is_valid(raise_exception=True)
                serviceSerializer.save()

            reasons_data = child_data['child_visit_reason']

            for reason_data in reasons_data:
                reason_data['id'] = (reason_data['id'] if reason_data['id'] else None)

                reasonRecord = ChildReason.objects.filter(id=(reason_data['id'])).first()

                if not reason_data['id']:
                    reason_data.pop('id')

                reasonSerializer = ChildReasonSerializer(reasonRecord, data=reason_data)

                reasonSerializer.is_valid(raise_exception=True)
                reasonSerializer.save()

        comments_data = allInitialDataResult['visit_comment']

        for comment_data in comments_data:
            comment_data['id'] = (comment_data['id'] if comment_data['id'] else None)
            commentRecord = HouseholdVisitComment.objects.filter(id=(comment_data['id'])).first()

            if not comment_data['id']:
                comment_data.pop('id')

            commentSerializer = HouseholdVisitCommentSerializer(commentRecord, data=comment_data)
            commentSerializer.is_valid(raise_exception=True)
            commentSerializer.save()

        instance.visit_status = allInitialDataResult['visit_status']

        instance.save()

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
            'registeringadult_id_number',
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
            'child_visit_count',
            # 'visit_attempt_status'
        )



class HouseholdVisitRecordSerializer(serializers.ModelSerializer):

    household_visit_team_id = serializers.IntegerField()

    class Meta:
        model = HouseholdVisit
        fields = (
            'id',
            'household_visit_team_id'
        )

