
from rest_framework import serializers
from .models import Outreach
from student_registration.students.serializers import StudentSerializer
from student_registration.students.models import (
    IDType,
    Nationality
)


class OutreachSerializer(serializers.ModelSerializer):
    original_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_id_type_id = serializers.CharField(source='student.id_type_id', read_only=True)
    student_nationality_id = serializers.CharField(source='student.nationality_id', read_only=True)
    student_mother_nationality_id = serializers.CharField(source='student.mother_nationality_id', read_only=True)
    location = serializers.IntegerField(source='school.location_id', read_only=True)
    governorate_name = serializers.CharField(source='school.location.parent.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    student_age = serializers.CharField(source='student.calc_age')
    student_first_name = serializers.CharField(source='student.first_name')
    student_father_name = serializers.CharField(source='student.father_name')
    student_last_name = serializers.CharField(source='student.last_name')
    student_mother_fullname = serializers.CharField(source='student.mother_fullname', required=False)
    student_sex = serializers.CharField(source='student.sex')
    student_birthday_year = serializers.CharField(source='student.birthday_year')
    student_birthday_month = serializers.CharField(source='student.birthday_month')
    student_birthday_day = serializers.CharField(source='student.birthday_day')
    student_phone = serializers.CharField(source='student.phone', required=False)
    student_phone_prefix = serializers.CharField(source='student.phone_prefix', required=False)
    student_id_number = serializers.CharField(source='student.id_number')
    student_id_type = serializers.CharField(source='student.id_type')
    student_nationality = serializers.CharField(source='student.nationality')
    student_mother_nationality = serializers.CharField(source='student.mother_nationality', required=False)
    student_address = serializers.CharField(source='student.address', required=False)

    def create(self, validated_data):

        student_data = validated_data.pop('student', None)
        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()

        try:
            instance = Outreach.objects.create(**validated_data)
            instance.student = student_serializer.instance
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Outreach instance': ex.message})

        return instance

    def update(self, instance, validated_data):

        try:

            student_data = validated_data.pop('student', None)

            student = instance.student
            student.first_name = student_data['first_name']
            student.father_name = student_data['father_name']
            student.last_name = student_data['last_name']
            student.mother_fullname = student_data['mother_fullname']

            student.birthday_year = student_data['birthday_year']
            student.birthday_month = student_data['birthday_month']
            student.birthday_day = student_data['birthday_day']

            student.sex = student_data['sex']
            student.phone = student_data['phone']
            student.phone_prefix = student_data['phone_prefix']
            student.address = student_data['address']
            student.nationality = Nationality.objects.get(id=student_data['nationality'])
            student.mother_nationality = Nationality.objects.get(id=student_data['mother_nationality'])

            student.id_type = IDType.objects.get(id=student_data['id_type'])
            student.id_number = student_data['id_number']

            student.save()

            if 'registered_in_unhcr' in validated_data:
                instance.registered_in_unhcr = validated_data['registered_in_unhcr']
            if 'participated_in_alp' in validated_data:
                instance.participated_in_alp = validated_data['participated_in_alp']
            if 'last_informal_edu_level' in validated_data:
                instance.last_informal_edu_level = validated_data['last_informal_edu_level']
            if 'last_informal_edu_round' in validated_data:
                instance.last_informal_edu_round = validated_data['last_informal_edu_round']
            if 'last_informal_edu_final_result' in validated_data:
                instance.last_informal_edu_final_result = validated_data['last_informal_edu_final_result']
            if 'section' in validated_data:
                instance.section = validated_data['section']
            if 'registered_in_level' in validated_data:
                instance.registered_in_level = validated_data['registered_in_level']
            if 'assigned_to_level' in validated_data:
                instance.assigned_to_level = validated_data['assigned_to_level']
            if 'last_education_level' in validated_data:
                instance.last_education_level = validated_data['last_education_level']
            if 'last_education_year' in validated_data:
                instance.last_education_year = validated_data['last_education_year']
            if 'level' in validated_data:
                instance.level = validated_data['level']

            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Outreach instance': ex.message})

        return instance

    class Meta:
        model = Outreach
        fields = (
            'id',
            'original_id',
            'student_id',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_mother_fullname',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'student_age',
            'student_phone',
            'student_phone_prefix',
            'student_id_number',
            'student_id_type',
            'student_nationality',
            'student_mother_nationality',
            'student_id_type_id',
            'student_nationality_id',
            'student_mother_nationality_id',
            'student_address',
            'registered_in_unhcr',
            'participated_in_alp',
            'last_informal_edu_level',
            'last_informal_edu_year',
            'last_informal_edu_final_result',
            'registered_in_level',
            'assigned_to_level',
            'last_informal_edu_round',
            'student_address',
            'school',
            'section',
            'classroom',
            'last_education_level',
            'last_education_year',
            'owner',
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_math',
            'exam_result_science',
            'registered_in_school',
            'level',
            'exam_school',
            'alp_round',
            'location',
            'governorate_name',
            'school_number',
        )


class OutreachExamSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outreach
        fields = (
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_math',
            'exam_result_science',
            'level',
            'exam_corrector_arabic',
            'exam_corrector_language',
            'exam_corrector_math',
            'exam_corrector_science',
            'registered_in_level',
            'section',
            'assigned_to_level',
            'not_enrolled_in_this_school',
            'exam_not_exist_in_school',
            'post_exam_result_arabic',
            'post_exam_result_language',
            'post_exam_result_math',
            'post_exam_result_science',
            'post_exam_corrector_arabic',
            'post_exam_corrector_language',
            'post_exam_corrector_math',
            'post_exam_corrector_science',
            'post_exam_level',
        )


class OutreachSmallSerializer(serializers.ModelSerializer):
    original_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_id_type_id = serializers.CharField(source='student.id_type_id', read_only=True)
    student_nationality_id = serializers.CharField(source='student.nationality_id', read_only=True)
    student_mother_nationality_id = serializers.CharField(source='student.mother_nationality_id', read_only=True)
    location = serializers.IntegerField(source='school.location_id', read_only=True)
    governorate_name = serializers.CharField(source='school.location.parent.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)

    student_first_name = serializers.CharField(source='student.first_name')
    student_father_name = serializers.CharField(source='student.father_name')
    student_last_name = serializers.CharField(source='student.last_name')
    student_sex = serializers.CharField(source='student.sex')

    # def create(self, validated_data):
    #
    #     student_data = validated_data.pop('student', None)
    #     student_serializer = StudentSerializer(data=student_data)
    #     student_serializer.is_valid(raise_exception=True)
    #     student_serializer.instance = student_serializer.save()
    #
    #     try:
    #         instance = Outreach.objects.create(**validated_data)
    #         instance.student = student_serializer.instance
    #         instance.save()
    #
    #     except Exception as ex:
    #         raise serializers.ValidationError({'Outreach instance': ex.message})
    #
    #     return instance

    # def update(self, instance, validated_data):
    #
    #     try:
    #         instance.level = validated_data['level']
    #         instance.registered_in_level = validated_data['registered_in_level']
    #         instance.assigned_to_level = validated_data['assigned_to_level']
    #         instance.not_enrolled_in_this_school = validated_data['not_enrolled_in_this_school']
    #         instance.exam_not_exist_in_school = validated_data['exam_not_exist_in_school']
    #
    #         instance.save()
    #
    #     except Exception as ex:
    #         raise serializers.ValidationError({'Outreach instance': ex.message})
    #
    #     return instance

    class Meta:
        model = Outreach
        fields = (
            'id',
            'original_id',
            'student_id',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_sex',
            'student_id_type_id',
            'student_nationality_id',
            'student_mother_nationality_id',
            'school',
            'owner',
            'location',
            'governorate_name',
            'school_number',
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_math',
            'exam_result_science',
            'level',
            'exam_corrector_arabic',
            'exam_corrector_language',
            'exam_corrector_math',
            'exam_corrector_science',
            'registered_in_level',
            'assigned_to_level',
            'not_enrolled_in_this_school',
            'exam_not_exist_in_school',
            'post_exam_result_arabic',
            'post_exam_result_language',
            'post_exam_result_math',
            'post_exam_result_science',
            'post_exam_corrector_arabic',
            'post_exam_corrector_language',
            'post_exam_corrector_math',
            'post_exam_corrector_science',
            'post_exam_level',
        )
