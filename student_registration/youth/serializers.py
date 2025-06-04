from rest_framework import serializers
from .models import (
    Registration
)


def create_instance(validated_data, model):
    from student_registration.adolescent.serializers import AdolescentSerializer
    from student_registration.adolescent.models import Adolescent

    adolescent_data = validated_data.pop('adolescent', None)
    adolescent = None

    if 'id' in adolescent_data and adolescent_data['id']:
        adolescent_serializer = AdolescentSerializer(Adolescent.objects.get(id=adolescent_data['id']), data=adolescent_data)
        adolescent_serializer.is_valid(raise_exception=True)
        adolescent_serializer.instance = adolescent_serializer.save()
        adolescent = adolescent_serializer.instance

    if not adolescent:
        adolescent_serializer = AdolescentSerializer(data=adolescent_data)
        adolescent_serializer.is_valid(raise_exception=True)
        adolescent_serializer.instance = adolescent_serializer.save()
        adolescent = adolescent_serializer.instance

    try:
        instance = model.objects.create(**validated_data)
        instance.adolescent = adolescent
        instance.save()

    except Exception as ex:
        raise serializers.ValidationError({'Registration instance': ex})

    return instance


def update_instance(instance, validated_data):
    from student_registration.adolescent.serializers import AdolescentSerializer
    adolescent_data = validated_data.pop('adolescent', None)

    if adolescent_data:
        adolescent_serializer = AdolescentSerializer(instance.adolescent, data=adolescent_data)
        adolescent_serializer.is_valid(raise_exception=True)
        adolescent_serializer.instance = adolescent_serializer.save()

    try:

        for key in validated_data:
            if hasattr(instance, key):
                setattr(instance, key, validated_data[key])

        instance.save()

    except Exception as ex:
        raise serializers.ValidationError({'Registration instance': ex})

    return instance


class MainSerializer(serializers.ModelSerializer):
    original_id = serializers.IntegerField(source='id', read_only=True)
    registration_id = serializers.IntegerField(source='id', read_only=True)
    adolescent_id = serializers.IntegerField(source='adolescent.id', required=False)
    adolescent_first_name = serializers.CharField(source='adolescent.first_name')
    adolescent_father_name = serializers.CharField(source='adolescent.father_name')
    adolescent_last_name = serializers.CharField(source='adolescent.last_name')
    adolescent_full_name = serializers.CharField(source='adolescent.full_name', read_only=True)
    adolescent_mother_fullname = serializers.CharField(source='adolescent.mother_fullname')
    adolescent_gender = serializers.CharField(source='adolescent.gender')
    adolescent_birthday_year = serializers.CharField(source='adolescent.birthday_year')
    adolescent_birthday_month = serializers.CharField(source='adolescent.birthday_month')
    adolescent_birthday_day = serializers.CharField(source='adolescent.birthday_day')
    adolescent_birthday = serializers.CharField(source='adolescent.birthday', read_only=True)
    adolescent_age = serializers.CharField(source='adolescent.age', read_only=True)
    adolescent_nationality = serializers.CharField(source='adolescent.nationality')
    adolescent_nationality_id = serializers.CharField(source='adolescent.nationality.id', read_only=True)
    adolescent_nationality_other = serializers.CharField(source='adolescent.nationality_other', required=False)
    adolescent_governorate = serializers.CharField(source='adolescent.governorate')
    adolescent_governorate_id = serializers.CharField(source='adolescent.governorate.id', read_only=True)
    adolescent_district = serializers.CharField(source='adolescent.district')
    adolescent_district_id = serializers.CharField(source='adolescent.district.id', read_only=True)
    adolescent_cadaster = serializers.CharField(source='adolescent.cadaster')
    adolescent_cadaster_id = serializers.CharField(source='adolescent.cadaster.id', read_only=True)
    adolescent_address = serializers.CharField(source='adolescent.address', required=False)
    adolescent_disability = serializers.CharField(source='adolescent.disability', required=False)
    adolescent_disability_id = serializers.CharField(source='adolescent.disability.id', read_only=True)
    adolescent_id_number = serializers.CharField(source='adolescent.id_number', required=False)
    main_caregiver_nationality = serializers.CharField(source='adolescent.main_caregiver_nationality', required=False)
    main_caregiver_nationality_id = serializers.CharField(source='adolescent.main_caregiver_nationality.id', required=False)
    main_caregiver_nationality_other = serializers.CharField(source='adolescent.main_caregiver_nationality_other',
                                                             required=False)
    id_type = serializers.CharField(source='adolescent.id_type', required=False)
    id_type_id = serializers.CharField(source='adolescent.id_type.id', required=False)
    case_number = serializers.CharField(source='adolescent.case_number', required=False)
    parent_individual_case_number = serializers.CharField(source='adolescent.parent_individual_case_number',
                                                          required=False)
    individual_case_number = serializers.CharField(source='adolescent.individual_case_number', required=False)
    recorded_number = serializers.CharField(source='adolescent.recorded_number', required=False)
    parent_national_number = serializers.CharField(source='adolescent.parent_national_number', required=False)
    national_number = serializers.CharField(source='adolescent.national_number', required=False)


    parent_extract_record = serializers.CharField(source='adolescent.parent_extract_record', required=False)


    parent_syrian_national_number = serializers.CharField(source='adolescent.parent_syrian_national_number',
                                                          required=False)
    syrian_national_number = serializers.CharField(source='adolescent.syrian_national_number', required=False)
    parent_sop_national_number = serializers.CharField(source='adolescent.parent_sop_national_number', required=False)
    sop_national_number = serializers.CharField(source='adolescent.sop_national_number', required=False)
    parent_other_number = serializers.CharField(source='adolescent.parent_other_number', required=False)
    other_number = serializers.CharField(source='adolescent.other_number', required=False)
    unrwa_number = serializers.CharField(source='adolescent.unrwa_number', required=False)
    father_educational_level = serializers.CharField(source='adolescent.father_educational_level', required=False)
    father_educational_level_id = serializers.CharField(source='adolescent.father_educational_level.id', required=False)
    mother_educational_level = serializers.CharField(source='adolescent.mother_educational_level', required=False)
    mother_educational_level_id = serializers.CharField(source='adolescent.mother_educational_level.id', required=False)
    first_phone_number = serializers.CharField(source='adolescent.first_phone_number', required=False)
    second_phone_number = serializers.CharField(source='adolescent.second_phone_number', required=False)
    main_caregiver = serializers.CharField(source='adolescent.main_caregiver', required=False)
    main_caregiver_other = serializers.CharField(source='adolescent.main_caregiver_other', required=False)
    caregiver_first_name = serializers.CharField(source='adolescent.caregiver_first_name', required=False)
    caregiver_middle_name = serializers.CharField(source='adolescent.caregiver_middle_name', required=False)
    caregiver_last_name = serializers.CharField(source='adolescent.caregiver_last_name', required=False)
    caregiver_mother_name = serializers.CharField(source='adolescent.caregiver_mother_name', required=False)
    created = serializers.CharField(read_only=True)
    csrfmiddlewaretoken = serializers.IntegerField(source='owner.id', read_only=True)
    save = serializers.IntegerField(source='owner.id', read_only=True)
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
            'adolescent_id',
            'csrfmiddlewaretoken',
            'save',
            'owner',
            'owner_name',
            'modified_by',
            'modified_by_name',
            'created',
            'modified',
            'adolescent_first_name',
            'adolescent_father_name',
            'adolescent_last_name',
            'adolescent_mother_fullname',
            'adolescent_full_name',
            'adolescent_gender',
            'adolescent_nationality',
            'adolescent_nationality_other',
            'adolescent_nationality_id',
            'adolescent_birthday_year',
            'adolescent_birthday_month',
            'adolescent_birthday_day',
            'adolescent_birthday',
            'adolescent_age',
            'main_caregiver_nationality',
            'main_caregiver_nationality_id',
            'main_caregiver_nationality_other',
            'adolescent_id_number',
            'adolescent_governorate',
            'adolescent_governorate_id',
            'adolescent_district',
            'adolescent_district_id',
            'adolescent_cadaster',
            'adolescent_cadaster_id',
            'adolescent_address',
            'adolescent_disability',
            'adolescent_disability_id',
            'father_educational_level',
            'father_educational_level_id',
            'mother_educational_level',
            'mother_educational_level_id',
            'first_phone_number',
            'second_phone_number',
            'main_caregiver',
            'main_caregiver_other',
            'caregiver_first_name',
            'caregiver_middle_name',
            'caregiver_last_name',
            'caregiver_mother_name',
            'id_type',
            'id_type_id',
            'case_number',
            'parent_individual_case_number',
            'individual_case_number',
            'parent_extract_record',
            'recorded_number',
            'parent_national_number',
            'national_number',
            'parent_syrian_national_number',
            'syrian_national_number',
            'parent_sop_national_number',
            'sop_national_number',
            'parent_other_number',
            'other_number',
            'unrwa_number'
        )
