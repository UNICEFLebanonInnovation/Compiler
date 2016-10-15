
from rest_framework import serializers
from .models import Registration, RegisteringAdult, WaitingList
from student_registration.students.serializers import StudentSerializer


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
    student_age = serializers.CharField(source='student.age')
    student_phone = serializers.CharField(source='student.phone')
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
            'student_age',
            'student_phone',
            'student_id_number',
            'student_id_type',
            'student_id_type_name',
            'student_number',
            'student_nationality',
            'student_mother_nationality',
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
            'last_education_level',
            'last_education_year',
            'last_class_level',
            'owner',
        )


class RegistrationChildSerializer(serializers.ModelSerializer):

    student_id = serializers.IntegerField(source='student.id', read_only=True)
    number = serializers.CharField(source='student.number', read_only=True)
    first_name = serializers.CharField(source='student.first_name')
    father_name = serializers.CharField(source='student.father_name')
    last_name = serializers.CharField(source='student.last_name')
    mother_fullname = serializers.CharField(source='student.mother_fullname')
    sex = serializers.CharField(source='student.sex')
    birthday_year = serializers.CharField(source='student.birthday_year')
    birthday_month = serializers.CharField(source='student.birthday_month')
    birthday_day = serializers.CharField(source='student.birthday_day')
    id_number = serializers.CharField(source='student.id_number')
    age = serializers.CharField(source='student.age')
    school_name = serializers.CharField(source='school.name', read_only=True)

    def create(self, validated_data):

        student_data = validated_data.pop('student', None)
        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()

        try:
            instance = Registration.objects.create(**validated_data)
            instance.student = student_serializer.instance
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
            'school_name',
            'enrolled_last_year_school',
            'relation_to_adult',
            'related_to_family',
            'enrolled_last_year_location',
            'enrolled_last_year',
            'registering_adult',
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
            'owner',
            'number',
        )


class RegisteringAdultSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    number = serializers.CharField(read_only=True)
    children = RegistrationChildSerializer(many=True, read_only=True)

    def create(self, validated_data):

        try:
            instance = RegisteringAdult.objects.create(**validated_data)
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
            'previously_registered_number',
            'signature',
            'address',
            'primary_phone',
            'primary_phone_answered',
            'secondary_phone',
            'secondary_phone_answered',
            'children',
            'number',
            'principal_applicant_living_in_house',
            'individual_id_number',
        )


class ClassAssignmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Registration
        fields = (
            'id',
            'classroom',
            'section',
            'enrolled_in_this_school',
        )


class WaitingListSerializer(serializers.ModelSerializer):

    class Meta:
        model = WaitingList
        fields = (
            'location',
            'school',
            'first_name',
            'last_name',
            'father_name',
            'unhcr_id',
            'number_of_children',
            'phone_number',
            'alternate_phone_number',
            'village',
            'owner',
        )

