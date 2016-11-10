
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

    service_type_id = serializers.CharField(source='service_type.id')
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
            'id',
            'service_type_id',
            'service_type',
            'service_provider',
        )



class VisitAttemptSerializer(serializers.Serializer):

    id = serializers.IntegerField()

    def create(self, validated_data):

        try:
            instance = HouseholdVisitAttempt.objects.create()



            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'HouseholdVisitAttempt instance': ex.message})

        return instance

    def update(self, instance, validated_data):
        # Update the book instance
        # instance.visit_status = validated_data['visit_status']
        #
        # # Delete any pages not included in the request
        # # page_ids = [item['page_id'] for item in validated_data['pages']]
        # # for page in instance.books:
        # #     if page.id not in page_ids:
        # #         page.delete()
        #
        # # # Create or update page instances that are in the request
        # for item in validated_data['visit_attempt']:
        #     instance.visit_status = ''.join('{}{}'.format(key, val) for key, val in item.items())
        #
        #     # hhva = HouseholdVisitAttempt(id=item['id'], household_found=item['household_found'], comment=item['comment'], date=item['date'], visit_attempt=instance)
        #     # hhva.save()
        #
        # instance.save()

        return instance


    class Meta:
        model = HouseholdVisitAttempt
        fields = (
            'id',
            'household_found',
            'comment',
            'date',
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
            'id',
            'comment',
            'date',
        )

class ChildVisitSerializer(serializers.ModelSerializer):

    student_id = serializers.CharField(source='student.id')
    first_name = serializers.CharField(source='student.first_name')
    father_name = serializers.CharField(source='student.father_name')
    last_name = serializers.CharField(source='student.last_name')
    mother_fullname = serializers.CharField(source='student.mother_fullname')
    main_reason_id = serializers.CharField(source='main_reason.id')
    main_reason =  serializers.CharField(source='main_reason.name')
    specific_reason_id = serializers.CharField(source='specific_reason.id')
    specific_reason = serializers.CharField(source='specific_reason.name')
    child_visit_service = ChildServiceSerializer(many=True, read_only=True)


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
            # instance.household_visit_team = household_visit_team_serializer.instance
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
        )


class HouseholdVisitSerializer(serializers.Serializer):

    id = serializers.IntegerField(read_only=True)
    registeringadult_id = serializers.IntegerField(source='registering_adult.id', read_only=True)
    first_name = serializers.CharField(source='registering_adult.first_name', read_only=True)
    father_name = serializers.CharField(source='registering_adult.father_name', read_only=True)
    last_name = serializers.CharField(source='registering_adult.last_name', read_only=True)
    address = serializers.CharField(source='registering_adult.address', read_only=True)
    primary_phone = serializers.CharField(source='registering_adult.primary_phone', read_only=True)
    secondary_phone = serializers.CharField(source='registering_adult.secondary_phone', read_only=True)
    visit_attempt = VisitAttemptSerializer(many=True)
    children_visits = ChildVisitSerializer(many=True, read_only=True)
    visit_comment = HouseholdVisitCommentSerializer(many=True, read_only=True)
    household_visit_team = HouseholdVisitCommentSerializer(many=True, read_only=True)
    all_visit_attempt_count = serializers.CharField()
    visit_status = serializers.CharField()

    def create(self, validated_data):

        # registeringadult_data = validated_data.pop('registering_adult', None)
        # registeringadult_serializer = RegisteringAdultSerializer(data=registeringadult_data)
        # registeringadult_serializer.is_valid(raise_exception=True)
        # registeringadult_serializer.instance = RegisteringAdultSerializer.save()
        #
        # try:
        #     instance = HouseholdVisit.objects.create(**validated_data)
        #     instance.registering_adult = RegisteringAdultSerializer.instance
        #     instance.save()
        #
        # except Exception as ex:
        #     raise serializers.ValidationError({'HouseholdVisit instance': ex.message})

        # instance = HouseholdVisit.objects.create()
        #
        # instance.visit_status = validated_data['visit_status']
        # instance.save()
        instance = HouseholdVisit.objects.create()
        return instance

    def update(self, instance, validated_data):
        # Update the book instance
        instance.visit_status = validated_data['visit_status']

        # Delete any pages not included in the request
        # page_ids = [item['page_id'] for item in validated_data['pages']]
        # for page in instance.books:
        #     if page.id not in page_ids:
        #         page.delete()

        # # Create or update page instances that are in the request
        for item in validated_data['visit_attempt']:

            instance.visit_status = ''.join('{}{}'.format(key, val) for key, val in item.items())

            #hhva = HouseholdVisitAttempt(id=item['id'], household_found=item['household_found'], comment=item['comment'], date=item['date'], visit_attempt=instance)
            #hhva.save()

        instance.save()

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
            'household_visit_team',
            'all_visit_attempt_count',
        )
