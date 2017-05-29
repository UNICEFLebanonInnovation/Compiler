
from rest_framework import serializers
from .models import Outreach
from student_registration.students.serializers import StudentSerializer
from student_registration.students.models import (
    IDType,
    Nationality,
    Student,
)


def update_student(student_data, student):

    if 'first_name' in student_data:
        student.first_name = student_data['first_name']
    if 'father_name' in student_data:
        student.father_name = student_data['father_name']
    if 'last_name' in student_data:
        student.last_name = student_data['last_name']
    if 'mother_fullname' in student_data:
        student.mother_fullname = student_data['mother_fullname']

    if 'birthday_year' in student_data:
        student.birthday_year = student_data['birthday_year']
    if 'birthday_month' in student_data:
        student.birthday_month = student_data['birthday_month']
    if 'birthday_day' in student_data:
        student.birthday_day = student_data['birthday_day']

    if 'sex' in student_data:
        student.sex = student_data['sex']
    if 'phone' in student_data:
        student.phone = student_data['phone']
    if 'phone_prefix' in student_data:
        student.phone_prefix = student_data['phone_prefix']
    if 'address' in student_data:
        student.address = student_data['address']
    if 'nationality' in student_data:
        student.nationality_id = student_data['nationality']
    if 'mother_nationality' in student_data:
        student.mother_nationality_id = student_data['mother_nationality']
    if 'id_type' in student_data:
        student.id_type_id = student_data['id_type']
    if 'id_number' in student_data:
        student.id_number = student_data['id_number']

    student.save()

    return student


class OutreachSerializer(serializers.ModelSerializer):

    original_id = serializers.IntegerField(source='id', read_only=True)
    # student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', required=False)
    student_first_name = serializers.CharField(source='student.first_name')
    student_father_name = serializers.CharField(source='student.father_name')
    student_last_name = serializers.CharField(source='student.last_name')
    student_full_name = serializers.CharField(source='student', read_only=True)
    student_mother_fullname = serializers.CharField(source='student.mother_fullname')
    student_sex = serializers.CharField(source='student.sex')
    student_birthday_year = serializers.CharField(source='student.birthday_year')
    student_birthday_month = serializers.CharField(source='student.birthday_month')
    student_birthday_day = serializers.CharField(source='student.birthday_day')
    student_birthday = serializers.CharField(source='student.birthday', read_only=True)
    student_age = serializers.CharField(source='student.calc_age', read_only=True)
    student_phone = serializers.CharField(source='student.phone')
    student_phone_prefix = serializers.CharField(source='student.phone_prefix')
    student_id_number = serializers.CharField(source='student.id_number')
    student_id_type = serializers.CharField(source='student.id_type')
    student_id_type_name = serializers.CharField(source='student.id_type.name', read_only=True)
    student_number = serializers.CharField(source='student.number', read_only=True)
    student_nationality = serializers.CharField(source='student.nationality')
    student_mother_nationality = serializers.CharField(source='student.mother_nationality')
    student_address = serializers.CharField(source='student.address')
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    registered_in_level_name = serializers.CharField(source='registered_in_level.name', read_only=True)
    refer_to_level_name = serializers.CharField(source='refer_to_level.name', read_only=True)
    governorate_name = serializers.CharField(source='school.location.parent.name', read_only=True)
    location = serializers.CharField(source='school.location.name', read_only=True)
    student_nationality_id = serializers.CharField(source='student.nationality.id', read_only=True)
    student_mother_nationality_id = serializers.CharField(source='student.mother_nationality.id', read_only=True)
    student_id_type_id = serializers.CharField(source='student.id_type.id', read_only=True)

    last_education_level_id = serializers.CharField(source='last_education_level.id', read_only=True)
    last_informal_edu_level_id = serializers.CharField(source='last_informal_edu_level.id', read_only=True)
    last_informal_edu_round_id = serializers.CharField(source='last_informal_edu_round.id', read_only=True)
    last_informal_edu_final_result_id = serializers.CharField(source='last_informal_edu_final_result.id', read_only=True)

    pretest_total = serializers.CharField(read_only=True)
    posttest_total = serializers.CharField(read_only=True)
    next_level = serializers.CharField(read_only=True)

    def create(self, validated_data):

        student_data = validated_data.pop('student', None)
        if 'id' in student_data and student_data['id']:
            student = update_student(student_data, Student.objects.get(id=student_data['id']))
        else:
            student_serializer = StudentSerializer(data=student_data)
            student_serializer.is_valid(raise_exception=True)
            student_serializer.instance = student_serializer.save()
            student = student_serializer.instance

        try:
            instance = Outreach.objects.create(**validated_data)
            instance.student = student
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Outreach instance': ex.message})

        return instance

    def update(self, instance, validated_data):

        try:

            student_data = validated_data.pop('student', None)
            student = update_student(student_data, instance.student)

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
            if 'modified_by' in validated_data:
                instance.modified_by_id = validated_data['modified_by']

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
            'student_full_name',
            'student_mother_fullname',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'student_birthday',
            'student_age',
            'student_phone',
            'student_phone_prefix',
            'student_id_number',
            'student_id_type',
            'student_id_type_name',
            'student_number',
            'student_nationality',
            'student_mother_nationality',
            'registered_in_unhcr',
            'participated_in_alp',
            'last_informal_edu_level',
            'last_informal_edu_round',
            'last_informal_edu_final_result',
            'student_address',
            'school',
            'school_name',
            'school_number',
            'section',
            'section_name',
            'level',
            'level_name',
            'last_education_level',
            'last_education_year',
            'owner',
            'modified_by',
            'governorate_name',
            'location',
            'student_nationality_id',
            'student_mother_nationality_id',
            'student_id_type_id',
            'last_education_level_id',
            'last_informal_edu_level_id',
            'last_informal_edu_round_id',
            'last_informal_edu_final_result_id',
            'pretest_total',
            'posttest_total',
            'assigned_to_level',
            'registered_in_level',
            'next_level',
            'alp_round',
            'registered_in_level_name',
            'refer_to_level',
            'refer_to_level_name'
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
            'refer_to_level',
            'modified_by',
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
    student_mother_fullname = serializers.CharField(source='student.mother_fullname', required=False)
    student_sex = serializers.CharField(source='student.sex')

    student_birthday_year = serializers.CharField(source='student.birthday_year', required=False)
    student_birthday_month = serializers.CharField(source='student.birthday_month', required=False)
    student_birthday_day = serializers.CharField(source='student.birthday_day', required=False)
    student_phone = serializers.CharField(source='student.phone', required=False)
    student_phone_prefix = serializers.CharField(source='student.phone_prefix', required=False)
    student_id_number = serializers.CharField(source='student.id_number', required=False)
    student_id_type = serializers.CharField(source='student.id_type', required=False)
    student_nationality = serializers.CharField(source='student.nationality', required=False)
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
            student = update_student(student_data, instance.student)

            if 'level' in validated_data:
                instance.level = validated_data['level']
            if 'assigned_to_level' in validated_data:
                instance.assigned_to_level = validated_data['assigned_to_level']

            if 'exam_result_arabic' in validated_data:
                instance.exam_result_arabic = validated_data['exam_result_arabic']
            if 'exam_result_language' in validated_data:
                instance.exam_result_language = validated_data['exam_result_language']
            if 'exam_result_math' in validated_data:
                instance.exam_result_math = validated_data['exam_result_math']
            if 'exam_result_science' in validated_data:
                instance.exam_result_science = validated_data['exam_result_science']

            if 'exam_corrector_arabic' in validated_data:
                instance.exam_corrector_arabic = validated_data['exam_corrector_arabic']
            if 'exam_corrector_language' in validated_data:
                instance.exam_corrector_language = validated_data['exam_corrector_language']
            if 'exam_corrector_math' in validated_data:
                instance.exam_corrector_math = validated_data['exam_corrector_math']
            if 'exam_corrector_science' in validated_data:
                instance.exam_corrector_science = validated_data['exam_corrector_science']
            if 'modified_by' in validated_data:
                instance.modified_by_id = validated_data['modified_by']

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
            'student_id_type_id',
            'student_nationality',
            'student_mother_nationality',
            'student_nationality_id',
            'student_mother_nationality_id',
            'student_phone',
            'student_phone_prefix',
            'student_id_number',
            'student_id_type',
            'student_address',
            'school',
            'owner',
            'modified_by',
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
            'refer_to_level',
            'alp_round',
        )
