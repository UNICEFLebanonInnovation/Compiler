
from rest_framework import serializers
from .models import Registration, RegisteringAdult
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
            raise serializers.ValidationError({'instance': ex.message})

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


class RegisteringAdultSerializer(serializers.ModelSerializer):

    children = StudentSerializer(many=True, read_only=True)

    def create(self, validated_data):
        print validated_data
        children = validated_data.pop('children', [])
        print children
        for child in children:
            student_serializer = StudentSerializer(data=child)
            student_serializer.is_valid(raise_exception=True)
            student_serializer.instance = student_serializer.save()

        try:
            instance = RegisteringAdult.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'instance': ex.message})

        return instance

    class Meta:
        model = RegisteringAdult
        fields = (
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
            'children'
        )

# u'age': u'', u'card_issue_requested': False, u'signature': u'', u'previously_registered_status': True}
