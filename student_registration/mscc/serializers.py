
import json

from rest_framework import serializers
from .models import (
    Registration
)


def create_instance(validated_data, model):
    from student_registration.child.serializers import ChildSerializer
    from student_registration.child.models import Child

    child_data = validated_data.pop('child', None)
    child = None

    if 'id' in child_data and child_data['id']:
        child_serializer = ChildSerializer(Child.objects.get(id=child_data['id']), data=child_data)
        child_serializer.is_valid(raise_exception=True)
        child_serializer.instance = child_serializer.save()
        child = child_serializer.instance

    if not child:
        child_serializer = ChildSerializer(data=student_data)
        child_serializer.is_valid(raise_exception=True)
        child_serializer.instance = child_serializer.save()
        child = child_serializer.instance

    try:
        instance = model.objects.create(**validated_data)
        instance.child = child
        instance.save()

    except Exception as ex:
        raise serializers.ValidationError({'Registration instance': ex.message})

    return instance


def update_instance(instance, validated_data):
    from student_registration.child.serializers import ChildSerializer
    child_data = validated_data.pop('child', None)

    if child_data:
        child_serializer = ChildSerializer(instance.child, data=child_data)
        child_serializer.is_valid(raise_exception=True)
        child_serializer.instance = child_serializer.save()

    try:

        for key in validated_data:
            if hasattr(instance, key):
                setattr(instance, key, validated_data[key])

        instance.save()

    except Exception as ex:
        raise serializers.ValidationError({'Registration instance': ex.message})

    return instance


class MainSerializer(serializers.ModelSerializer):
    original_id = serializers.IntegerField(source='id', read_only=True)
    registration_id = serializers.IntegerField(source='id', read_only=True)
    child_id = serializers.IntegerField(source='child.id', required=False)
    child_first_name = serializers.CharField(source='child.first_name')
    child_father_name = serializers.CharField(source='child.father_name')
    child_last_name = serializers.CharField(source='child.last_name')
    child_full_name = serializers.CharField(source='child.full_name', read_only=True)
    child_mother_fullname = serializers.CharField(source='child.mother_fullname')
    child_gender = serializers.CharField(source='child.gender')
    child_birthday_year = serializers.CharField(source='child.birthday_year')
    child_birthday_month = serializers.CharField(source='child.birthday_month')
    child_birthday_day = serializers.CharField(source='child.birthday_day')
    child_birthday = serializers.CharField(source='child.birthday', read_only=True)
    child_nationality = serializers.CharField(source='child.nationality')
    child_nationality_id = serializers.CharField(source='child.nationality.id', read_only=True)
    child_address = serializers.CharField(source='child.address', required=False)
    child_p_code = serializers.CharField(source='child.p_code', required=False)
    child_id_number = serializers.CharField(source='child.id_number', required=False)
    child_marital_status = serializers.CharField(source='child.marital_status', required=False)
    child_have_children = serializers.CharField(source='child.have_children', required=False)
    # governorate_name = serializers.CharField(source='governorate.name', read_only=True)
    # district_name = serializers.CharField(source='district.name', read_only=True)
    # cadaster_name = serializers.CharField(source='cadaster.name', read_only=True)
    # partner_name = serializers.CharField(source='partner.name', read_only=True)
    # partner = serializers.CharField(source='partner.id', read_only=True)
    created = serializers.CharField(read_only=True)
    csrfmiddlewaretoken = serializers.IntegerField(source='owner.id', read_only=True)
    save = serializers.IntegerField(source='owner.id', read_only=True)
    search_mscc_student = serializers.CharField(source='student.full_name', read_only=True)
    owner_name = serializers.CharField(source='owner.username', read_only=True)
    modified_by_name = serializers.CharField(source='modified_by.username', read_only=True)

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = Registration
        fields = (
            'id',
            'original_id',
            'registration_id',
            'child_id',
            'search_mscc_student',
            'csrfmiddlewaretoken',
            'save',
            'owner',
            'owner_name',
            'modified_by',
            'modified_by_name',
            'created',
            'modified',
            'center',
            'child_first_name',
            'child_father_name',
            'child_last_name',
            'child_mother_fullname',
            'child_full_name',
            'child_gender',
            'child_nationality',
            'child_nationality_other',
            'child_nationality_id',
            'child_birthday_year',
            'child_birthday_month',
            'child_birthday_day',
            'child_birthday',
            'main_caregiver_nationality',
            'main_caregiver_nationality_other',
            'child_p_code',
            'child_id_number',
            'child_address',
            'child_disability',
            'child_marital_status',
            'child_have_children',
            'child_number_children',
            'source_of_identification',
            'source_of_identification_specify',
            'cash_support_programmes',
            'father_educational_level',
            'mother_educational_level',
            'first_phone_owner',
            'first_phone_number',
            'first_phone_number_confirm',
            'second_phone_owner',
            'second_phone_number',
            'second_phone_number_confirm',
            'main_caregiver',
            'main_caregiver_other',
            'caregiver_first_name',
            'caregiver_middle_name',
            'caregiver_last_name',
            'caregiver_mother_name',
            'have_labour',
            'labour_type',
            'labour_type_specify',
            'labour_hours',
            'labour_weekly_income',
            'id_type',
            'case_number',
            'case_number_confirm',
            'parent_individual_case_number',
            'parent_individual_case_number_confirm',
            'individual_case_number',
            'individual_case_number_confirm',
            'recorded_number',
            'recorded_number_confirm',
            'parent_national_number',
            'parent_national_number_confirm',
            'national_number',
            'national_number_confirm',
            'parent_syrian_national_number',
            'parent_syrian_national_number_confirm',
            'syrian_national_number',
            'syrian_national_number_confirm',
            'parent_sop_national_number',
            'parent_sop_national_number_confirm',
            'sop_national_number',
            'sop_national_number_confirm',
            'parent_other_number',
            'parent_other_number_confirm',
            'other_number',
            'other_number_confirm',
        )

