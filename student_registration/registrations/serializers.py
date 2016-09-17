
from rest_framework import serializers
from .models import Registration, RegisteringAdult
from student_registration.students.serializers import StudentSerializer
from student_registration.students.utils import *


class RegistrationSerializer(serializers.ModelSerializer):

    original_id = serializers.IntegerField(source='id', read_only=True)
    student_id = serializers.IntegerField(source='student.id', read_only=True)
    student_first_name = serializers.CharField(source='student.first_name')
    student_father_name = serializers.CharField(source='student.father_name')
    student_last_name = serializers.CharField(source='student.last_name')
    student_mother_fullname = serializers.CharField(source='student.mother_fullname')
    student_sex = serializers.CharField(source='student.sex')
    student_birthday_year = serializers.CharField(source='student.birthday_year')
    student_birthday_month = serializers.CharField(source='student.birthday_month')
    student_birthday_day = serializers.CharField(source='student.birthday_day')
    student_phone = serializers.CharField(source='student.phone')
    student_id_number = serializers.CharField(source='student.id_number')
    student_id_type = serializers.CharField(source='student.id_type')
    student_id_type_name = serializers.CharField(source='student.id_type.name', read_only=True)
    student_number = serializers.CharField(source='student.number', read_only=True)
    student_nationality = serializers.CharField(source='student.nationality')
    student_address = serializers.CharField(source='student.address')
    school_name = serializers.CharField(source='school.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    grade_name = serializers.CharField(source='grade.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)

    def create(self, validated_data):

        student_data = validated_data.pop('student', None)
        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()

        try:
            instance = Registration.objects.create(**validated_data)
            instance.student = student_serializer.instance
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Registration instance': ex.message})

        return instance

    class Meta:
        model = Registration
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
            'student_phone',
            'student_id_number',
            'student_id_type',
            'student_id_type_name',
            'student_number',
            'student_nationality',
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
            'owner',
        )


class RegistrationChildSerializer(serializers.ModelSerializer):

    student_id = serializers.IntegerField(source='student.id', read_only=True)
    first_name = serializers.CharField(source='student.first_name', read_only=True)
    father_name = serializers.CharField(source='student.father_name', read_only=True)
    last_name = serializers.CharField(source='student.last_name', read_only=True)
    mother_fullname = serializers.CharField(source='student.mother_fullname', read_only=True)
    sex = serializers.CharField(source='student.sex', read_only=True)
    birthday_year = serializers.CharField(source='student.birthday_year', read_only=True)
    birthday_month = serializers.CharField(source='student.birthday_month', read_only=True)
    birthday_day = serializers.CharField(source='student.birthday_day', read_only=True)
    id_number = serializers.CharField(source='student.id_number', read_only=True)
    age = serializers.CharField(source='student.age', read_only=True)
    relation_to_adult = serializers.CharField(source='student.relation_to_adult', read_only=True)
    out_of_school_two_years = serializers.CharField(source='student.out_of_school_two_years', read_only=True)
    related_to_family = serializers.CharField(source='student.related_to_family', read_only=True)
    enrolled_last_year = serializers.CharField(source='student.enrolled_last_year', read_only=True)
    enrolled_last_year_location = serializers.CharField(source='student.enrolled_last_year_location.id', read_only=True)
    enrolled_last_year_school = serializers.CharField(source='student.enrolled_last_year_school.id', read_only=True)

    def create(self, validated_data):

        try:
            instance = Registration.objects.create(**validated_data)
            if not instance.related_to_family:
                instance.status = False
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'RegistrationChild instance': ex.message})

        return instance

    class Meta:
        model = Registration
        fields = (
            'school',
            'enrolled_last_year_school',
            'relation_to_adult',
            'related_to_family',
            'enrolled_last_year_location',
            'enrolled_last_year',
            'student_id',
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'sex',
            'age',
            'birthday_year',
            'birthday_month',
            'birthday_day',
            'id_number',
            'relation_to_adult',
            'out_of_school_two_years',
            'related_to_family',
            'enrolled_last_year',
            'enrolled_last_year_location',
            'enrolled_last_year_school',
        )


class RegisteringAdultSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    children = RegistrationChildSerializer(many=True, read_only=True)

    def get_children(self):
        pass

    def create(self, validated_data):

        try:
            instance = RegisteringAdult.objects.create(**validated_data)
            instance.number = generate_id(instance.first_name, instance.father_name, instance.last_name, instance.mother_fullname, instance.sex)
            if instance.age < 18 or instance.id_type == 6:
                instance.status = False
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'RegisteringAdult instance': ex.message})

        return instance

    class Meta:
        model = RegisteringAdult
        fields = (
            'id',
            'school',
            'id_type',
            'id_number',
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'sex',
            'age',
            'nationality',
            'birthday_day',
            'birthday_month',
            'birthday_year',
            'wfp_case_number',
            'csc_case_number',
            'relation_to_householdhead',
            'child_enrolled_in_other_schools',
            'previously_registered',
            'previously_registered_status',
            'signature',
            'address',
            'primary_phone',
            'primary_phone_answered',
            'secondary_phone',
            'secondary_phone_answered',
            'children',
        )
