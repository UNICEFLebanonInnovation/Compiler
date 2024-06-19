
from rest_framework import serializers
from .models import (
    Adolescent,
)


class AdolescentSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    number = serializers.CharField(read_only=True)
    birthday = serializers.CharField(read_only=True)

    def create(self, validated_data):

        try:
            instance = Adolescent.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Adolescent instance': ex})

        return instance

    class Meta:
        model = Adolescent
        fields = (
            'id',
            'first_name',
            'last_name',
            'father_name',
            'mother_fullname',
            'gender',
            'nationality',
            'nationality_other',
            'birthday_year',
            'birthday_month',
            'birthday_day',
            'governorate',
            'district',
            'cadaster',
            'address',
            'disability',
            'birthday',
            'number',
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
            'parent_extract_record',
            'parent_extract_record_confirm',
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
            'father_educational_level',
            'mother_educational_level',
            'first_phone_number',
            'first_phone_number_confirm',
            'second_phone_number',
            'second_phone_number_confirm',
            'main_caregiver',
            'main_caregiver_other',
            'caregiver_first_name',
            'caregiver_middle_name',
            'caregiver_last_name',
            'caregiver_mother_name',
            'main_caregiver_nationality',
            'main_caregiver_nationality_other'
        )

