
from rest_framework import serializers
from .models import Enrollment, LoggingStudentMove
from student_registration.students.serializers import StudentSerializer
from student_registration.students.models import (
    IDType,
    Nationality
)


class LoggingStudentMoveSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    enrolment_id = serializers.IntegerField(source='enrolment.id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_first_name = serializers.CharField(source='student.first_name', read_only=True)
    student_father_name = serializers.CharField(source='student.father_name', read_only=True)
    student_last_name = serializers.CharField(source='student.last_name', read_only=True)
    student_full_name = serializers.CharField(source='student', read_only=True)
    student_mother_fullname = serializers.CharField(source='student.mother_fullname', read_only=True)
    student_sex = serializers.CharField(source='student.sex', read_only=True)
    student_age = serializers.CharField(source='student.calc_age', read_only=True)
    school_name = serializers.CharField(source='enrolment.school.name', read_only=True)
    school_number = serializers.CharField(source='enrolment.school.number', read_only=True)
    section_name = serializers.CharField(source='enrolment.section.name', read_only=True)
    classroom_name = serializers.CharField(source='enrolment.classroom.name', read_only=True)

    class Meta:
        model = LoggingStudentMove
        fields = (
            'id',
            'enrolment_id',
            'student_id',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_full_name',
            'student_mother_fullname',
            'student_sex',
            'student_age',
            'school_name',
            'school_number',
            'section_name',
            'classroom_name',
        )


class EnrollmentSerializer(serializers.ModelSerializer):

    original_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_first_name = serializers.CharField(source='student.first_name')
    student_father_name = serializers.CharField(source='student.father_name')
    student_last_name = serializers.CharField(source='student.last_name')
    student_full_name = serializers.CharField(source='student.full_name')
    student_mother_fullname = serializers.CharField(source='student.mother_fullname')
    student_sex = serializers.CharField(source='student.sex')
    student_birthday_year = serializers.CharField(source='student.birthday_year')
    student_birthday_month = serializers.CharField(source='student.birthday_month')
    student_birthday_day = serializers.CharField(source='student.birthday_day')
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
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    governorate_name = serializers.CharField(source='school.location.parent.name', read_only=True)
    location = serializers.CharField(source='school.location.name', read_only=True)
    student_nationality_id = serializers.CharField(source='student.nationality.id', read_only=True)
    student_mother_nationality_id = serializers.CharField(source='student.mother_nationality.id', read_only=True)
    student_id_type_id = serializers.CharField(source='student.id_type.id', read_only=True)

    last_education_level_id = serializers.CharField(source='last_education_level.id', read_only=True)
    last_school_id = serializers.CharField(source='last_school.id', read_only=True)
    last_informal_edu_level_id = serializers.CharField(source='last_informal_edu_level.id', read_only=True)
    last_informal_edu_round_id = serializers.CharField(source='last_informal_edu_round.id', read_only=True)
    last_informal_edu_final_result_id = serializers.CharField(source='last_informal_edu_final_result.id', read_only=True)

    moved = serializers.CharField(read_only=True)

    def create(self, validated_data):

        student_data = validated_data.pop('student', None)
        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()

        try:
            instance = Enrollment.objects.create(**validated_data)
            instance.student = student_serializer.instance
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Enrollment instance': ex.message})

        return instance

    def update(self, instance, validated_data):

        student_data = validated_data.pop('student', None)

        if student_data:
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

        try:
            if 'school' in validated_data:
                instance.school = validated_data['school']
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
            if 'classroom' in validated_data:
                instance.classroom = validated_data['classroom']
            if 'last_year_result' in validated_data:
                instance.last_year_result = validated_data['last_year_result']
            if 'last_school_type' in validated_data:
                instance.last_school_type = validated_data['last_school_type']
            if 'last_school_shift' in validated_data:
                instance.last_school_shift = validated_data['last_school_shift']
            if 'last_school' in validated_data:
                instance.last_school = validated_data['last_school']
            if 'last_education_level' in validated_data:
                instance.last_education_level = validated_data['last_education_level']
            if 'last_education_year' in validated_data:
                instance.last_education_year = validated_data['last_education_year']

            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Enrollment instance': ex.message})

        return instance

    class Meta:
        model = Enrollment
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
            'grade',
            'grade_name',
            'section',
            'section_name',
            'classroom',
            'classroom_name',
            'last_year_result',
            'last_school_type',
            'last_school_shift',
            'last_school',
            'last_school_id',
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
            'moved',
        )

