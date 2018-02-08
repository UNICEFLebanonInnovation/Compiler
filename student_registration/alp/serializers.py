
from rest_framework import serializers
from .models import Outreach
# from student_registration.students.serializers import StudentSerializer
from student_registration.students.models import (
    IDType,
    Nationality,
    Student,
)


class OutreachSerializer(serializers.ModelSerializer):

    original_id = serializers.IntegerField(source='id', read_only=True)
    # student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', required=False)
    student_first_name = serializers.CharField(source='student.first_name')
    student_father_name = serializers.CharField(source='student.father_name')
    student_last_name = serializers.CharField(source='student.last_name')
    student_full_name = serializers.CharField(source='student', read_only=True)
    student_mother_fullname = serializers.CharField(source='student.mother_fullname', required=False)
    student_sex = serializers.CharField(source='student.sex')
    student_birthday_year = serializers.CharField(source='student.birthday_year')
    student_birthday_month = serializers.CharField(source='student.birthday_month')
    student_birthday_day = serializers.CharField(source='student.birthday_day')
    student_birthday = serializers.CharField(source='student.birthday', read_only=True)
    student_age = serializers.CharField(source='student.age', read_only=True)
    student_phone = serializers.CharField(source='student.phone', required=False)
    student_phone_prefix = serializers.CharField(source='student.phone_prefix', required=False)
    student_id_number = serializers.CharField(source='student.id_number')
    student_registered_in_unhcr = serializers.CharField(source='student.registered_in_unhcr', required=False)
    student_id_type = serializers.CharField(source='student.id_type')
    student_id_type_name = serializers.CharField(source='student.id_type.name', read_only=True)
    student_number = serializers.CharField(source='student.number', read_only=True)
    student_nationality = serializers.CharField(source='student.nationality')
    student_mother_nationality = serializers.CharField(source='student.mother_nationality', required=False)
    student_address = serializers.CharField(source='student.address', required=False)
    # school = serializers.IntegerField(required=True)
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    level_name = serializers.CharField(source='level.name', read_only=True)
    assigned_to_level_name = serializers.CharField(source='assigned_to_level.name', read_only=True)
    registered_in_level_name = serializers.CharField(source='registered_in_level.name', read_only=True)
    classroom_name = serializers.CharField(source='registered_in_level.name', read_only=True)
    refer_to_level_name = serializers.CharField(source='refer_to_level.name', read_only=True)
    alp_round_name = serializers.CharField(source='alp_round.name', read_only=True)
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

    csrfmiddlewaretoken = serializers.IntegerField(source='owner.id', read_only=True)
    save = serializers.IntegerField(source='owner.id', read_only=True)
    enrollment_id = serializers.IntegerField(source='id', read_only=True)
    search_student = serializers.CharField(source='student.full_name', read_only=True)
    search_school = serializers.CharField(source='school.id', read_only=True)
    search_barcode = serializers.CharField(source='outreach_barcode', read_only=True)

    def create(self, validated_data):
        from student_registration.students.serializers import StudentSerializer
        student_data = validated_data.pop('student', None)

        if 'id' in student_data and student_data['id']:
            student_serializer = StudentSerializer(Student.objects.get(id=student_data['id']), data=student_data)
            student_serializer.is_valid(raise_exception=True)
            student_serializer.instance = student_serializer.save()
        else:
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

            if student_data:
                from student_registration.students.serializers import StudentSerializer

                student_serializer = StudentSerializer(instance.student, data=student_data)
                student_serializer.is_valid(raise_exception=True)
                student_serializer.instance = student_serializer.save()

            for key in validated_data:
                if hasattr(instance, key):
                    setattr(instance, key, validated_data[key])

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
            'enrollment_id',
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
            'student_registered_in_unhcr',
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
            'assigned_to_level_name',
            'registered_in_level',
            'next_level',
            'alp_round',
            'registered_in_level_name',
            'classroom_name',
            'refer_to_level',
            'refer_to_level_name',
            'alp_round_name',
            'new_registry',
            'have_barcode',
            'outreach_barcode',
            'student_outreached',
            'search_barcode',
            'search_school',
            'search_student',
            'save',
            'csrfmiddlewaretoken',
        )


class GeneralSerializer(serializers.ModelSerializer):

    class Meta:
        model = Outreach
        fields = '__all__'


class GradingSerializer(serializers.ModelSerializer):
    pre_comment = serializers.CharField(required=False)
    post_comment = serializers.CharField(required=False)

    class Meta:
        model = Outreach
        fields = (
            'exam_result_arabic',
            'exam_language',
            'exam_result_language',
            'exam_result_math',
            'exam_result_science',
            'pre_test_room',
            'post_test_room',
            'level',
            'registered_in_level',
            'section',
            'assigned_to_level',
            'post_exam_result_arabic',
            'post_exam_language',
            'post_exam_result_language',
            'post_exam_result_math',
            'post_exam_result_science',
            'refer_to_level',
            'pre_comment',
            'post_comment',
        )


class OutreachSmallSerializer(serializers.ModelSerializer):
    student_id_type_id = serializers.CharField(source='student.id_type_id', read_only=True)
    student_nationality_id = serializers.CharField(source='student.nationality_id', read_only=True)
    student_mother_nationality_id = serializers.CharField(source='student.mother_nationality_id', read_only=True)

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
    student_registered_in_unhcr = serializers.CharField(source='student.registered_in_unhcr', required=False)
    student_id_type = serializers.CharField(source='student.id_type', required=False)
    student_nationality = serializers.CharField(source='student.nationality', required=False)
    student_mother_nationality = serializers.CharField(source='student.mother_nationality', required=False)
    student_address = serializers.CharField(source='student.address', required=False)

    pre_comment = serializers.CharField(required=False)
    post_comment = serializers.CharField(required=False)

    def create(self, validated_data):
        from student_registration.students.serializers import StudentSerializer
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

            if student_data:
                from student_registration.students.serializers import StudentSerializer

                student_serializer = StudentSerializer(instance.student, data=student_data)
                student_serializer.is_valid(raise_exception=True)
                student_serializer.instance = student_serializer.save()

            for key in validated_data:
                if hasattr(instance, key):
                    setattr(instance, key, validated_data[key])

            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Outreach instance': ex.message})

        return instance

    class Meta:
        model = Outreach
        fields = (
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
            'student_registered_in_unhcr',
            'student_address',
            'school',
            'exam_result_arabic',
            'exam_language',
            'exam_result_language',
            'exam_result_math',
            'exam_result_science',
            'pre_test_room',
            'level',
            'pre_comment',
            'post_comment',
        )
