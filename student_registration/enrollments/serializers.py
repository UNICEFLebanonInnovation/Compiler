from rest_framework import serializers
from .models import Enrollment, LoggingStudentMove, LoggingProgramMove, EnrollmentGrading


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
    student_age = serializers.CharField(source='student.age', read_only=True)
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
    student_id = serializers.IntegerField(source='student.id', required=False)
    student_first_name = serializers.CharField(source='student.first_name')
    student_father_name = serializers.CharField(source='student.father_name')
    student_last_name = serializers.CharField(source='student.last_name')
    student_full_name = serializers.CharField(source='student.full_name', read_only=True)
    student_mother_fullname = serializers.CharField(source='student.mother_fullname')
    student_sex = serializers.CharField(source='student.sex')
    student_birthday_year = serializers.CharField(source='student.birthday_year')
    student_birthday_month = serializers.CharField(source='student.birthday_month')
    student_birthday_day = serializers.CharField(source='student.birthday_day')
    student_place_of_birth = serializers.CharField(source='student.place_of_birth', required=False)
    student_recordnumber = serializers.CharField(source='student.recordnumber', required=False)
    student_age = serializers.CharField(source='student.age', read_only=True)
    student_phone = serializers.CharField(source='student.phone', required=False)
    student_phone_prefix = serializers.CharField(source='student.phone_prefix', required=False)
    student_id_number = serializers.CharField(source='student.id_number', required=False)
    student_registered_in_unhcr = serializers.CharField(source='student.registered_in_unhcr', required=False)
    student_id_type = serializers.CharField(source='student.id_type', required=False)
    student_id_type_name = serializers.CharField(source='student.id_type.name', read_only=True)
    student_number = serializers.CharField(source='student.number', read_only=True)
    student_nationality = serializers.CharField(source='student.nationality', required=False)
    student_mother_nationality = serializers.CharField(source='student.mother_nationality', required=False)
    student_address = serializers.CharField(source='student.address', required=False)
    school_name = serializers.CharField(source='school.name', read_only=True)
    education_year_name = serializers.CharField(source='education_year.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    governorate_name = serializers.CharField(source='school.location.parent.name', read_only=True)
    location = serializers.CharField(source='school.location.name', read_only=True)
    student_nationality_id = serializers.CharField(source='student.nationality.id', read_only=True)
    student_mother_nationality_id = serializers.CharField(source='student.mother_nationality.id', read_only=True)
    student_id_type_id = serializers.CharField(source='student.id_type.id', read_only=True)

    last_education_level_id = serializers.CharField(source='last_education_level.id', read_only=True)
    last_school_id = serializers.CharField(source='last_school.id', read_only=True)
    # last_informal_edu_level_id = serializers.CharField(source='last_informal_edu_level.id', read_only=True)
    last_informal_edu_round_id = serializers.CharField(source='last_informal_edu_round.id', read_only=True)
    last_informal_edu_final_result_id = serializers.CharField(source='last_informal_edu_final_result.id', read_only=True)

    moved = serializers.CharField(read_only=True)
    dropout_status = serializers.CharField(read_only=True)

    student_outreach_child = serializers.IntegerField(source='student.outreach_child', required=False)
    student_outreach_child_id = serializers.IntegerField(source='student.outreach_child.id', read_only=True)
    csrfmiddlewaretoken = serializers.IntegerField(source='owner.id', read_only=True)
    save = serializers.IntegerField(source='owner.id', read_only=True)
    enrollment_id = serializers.IntegerField(source='id', read_only=True)
    search_student = serializers.CharField(source='student.full_name', read_only=True)
    search_school = serializers.CharField(source='school.id', read_only=True)
    school_type = serializers.CharField(source='school.name', read_only=True)
    search_barcode = serializers.CharField(source='outreach_barcode', read_only=True)
    student_is_justified = serializers.BooleanField(source='student.is_justified', required=False)
    student_is_specialneeds = serializers.BooleanField(source='student.is_specialneeds', required=False)
    student_specialneeds = serializers.CharField(source='student.specialneeds', required=False)
    student_specialneeds_id = serializers.CharField(source='student.specialneeds.id', read_only=True)
    student_specialneedsdt = serializers.CharField(source='student.specialneedsdt', required=False)
    student_specialneedsdt_id = serializers.CharField(source='student.specialneedsdt.id', read_only=True)
    student_is_financialsupport = serializers.BooleanField(source='student.is_financialsupport', required=False)
    student_Financialsupport_number = serializers.CharField(source='student.Financialsupport_number', required=False)
    student_financialsupport = serializers.CharField(source='student.financialsupport', required=False)
    student_financialsupport_id = serializers.CharField(source='student.financialsupport.id', read_only=True)
    student_unhcr_family = serializers.CharField(source='student.unhcr_family', required=False)
    student_unhcr_personal = serializers.CharField(source='student.unhcr_personal', required=False)

    def create(self, validated_data):
        from student_registration.students.serializers import StudentSerializer
        from student_registration.students.models import Student

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
            instance = Enrollment.objects.create(**validated_data)
            instance.student = student_serializer.instance
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Enrollment instance': ex.message})

        return instance

    def update(self, instance, validated_data):

        student_data = validated_data.pop('student', None)

        if student_data:
            from student_registration.students.serializers import StudentSerializer

            student_serializer = StudentSerializer(instance.student, data=student_data)
            student_serializer.is_valid(raise_exception=True)
            student_serializer.instance = student_serializer.save()
        try:

            for key in validated_data:
                if hasattr(instance, key):
                    setattr(instance, key, validated_data[key])

            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Enrollment instance': ex.message})

        return instance

    class Meta:
        model = Enrollment
        fields = (
            'id',
            'original_id',
            'enrollment_id',
            'student_id',
            'student_outreach_child',
            'student_outreach_child_id',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_full_name',
            'student_mother_fullname',
            'student_sex',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'student_place_of_birth',
            'student_recordnumber',
            'student_age',
            'student_phone',
            'student_phone_prefix',
            'student_id_number',
            'student_id_type',
            'student_id_type_name',
            'student_number',
            'student_nationality',
            'student_mother_nationality',
            'student_registered_in_unhcr',
            'participated_in_alp',
            'number_in_previous_school',
            # 'last_informal_edu_level',
            'last_informal_edu_round',
            'last_informal_edu_final_result',
            'student_address',
            'school',
            'school_name',
            'school_number',
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
            # 'last_informal_edu_level_id',
            'last_informal_edu_round_id',
            'last_informal_edu_final_result_id',
            'moved',
            'dropout_status',
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_education',
            'exam_result_geo',
            'exam_result_history',
            'exam_result_math',
            'exam_result_science',
            'exam_result_physic',
            'exam_result_chemistry',
            'exam_result_bio',
            'exam_result_linguistic_ar',
            'exam_result_linguistic_en',
            'exam_result_sociology',
            'exam_result_physical',
            'exam_result_artistic',
            'exam_result_mathematics',
            'exam_result_sciences',
            'exam_total',
            'exam_result',
            'education_year',
            'education_year_name',
            'outreach_barcode',
            'student_outreached',
            'registration_date',
            'new_registry',
            'have_barcode',
            'search_school',
            'search_student',
            'search_barcode',
            'csrfmiddlewaretoken',
            'save',
            'school_type',
            'age_min_restricted',
            'age_max_restricted',
            'student_is_justified',
            'student_is_specialneeds',
            'student_specialneeds',
            'student_specialneedsdt',
            'student_specialneeds_id',
            'student_specialneedsdt_id',
            'student_is_financialsupport',
            'student_Financialsupport_number',
            'student_financialsupport',
            'student_financialsupport_id',
            'student_unhcr_personal',
            'student_unhcr_family',
        )


class GradingSerializer(serializers.ModelSerializer):

    csrfmiddlewaretoken = serializers.IntegerField(source='owner.id', read_only=True)
    save = serializers.IntegerField(source='owner.id', read_only=True)

    def update(self, instance, validated_data):

        try:

            for key in validated_data:
                if hasattr(instance, key):
                    setattr(instance, key, validated_data[key])

            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Enrollment instance': ex.message})

        return instance

    class Meta:
        model = Enrollment
        fields = (
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_education',
            'exam_result_geo',
            'exam_result_history',
            'exam_result_math',
            'exam_result_science',
            'exam_result_physic',
            'exam_result_chemistry',
            'exam_result_bio',
            'exam_result_linguistic_ar',
            'exam_result_linguistic_en',
            'exam_result_sociology',
            'exam_result_physical',
            'exam_result_artistic',
            'exam_result_mathematics',
            'exam_result_sciences',
            'exam_total',
            'exam_result',
            'exam_result_arabic_cmplt',
            'exam_result_language_cmplt',
            'exam_result_math_cmplt',
            'exam_total_cmplt',
            'exam_result_final',
            'csrfmiddlewaretoken',
            'save',
        )


class LoggingProgramMoveSerializer(serializers.ModelSerializer):

    def create(self, validated_data):
        from student_registration.schools.models import EducationYear

        try:
            current_year = EducationYear.objects.get(education_year=True)
            instance = LoggingStudentMove.objects.create(**validated_data)
            instance.education_year = current_year
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'LoggingStudentMove instance': ex.message})

        return instance

    class Meta:
        model = LoggingProgramMove
        fields = (
            'student',
            'registry',
            'school_from',
            'school_to',
            'eligibility',
        )


class EnrollmentImportSerializer(serializers.ModelSerializer):

    student_id = serializers.IntegerField(source='student.id', required=False)
    student_first_name = serializers.CharField(source='student.first_name', required=False)
    student_father_name = serializers.CharField(source='student.father_name', required=False)
    student_last_name = serializers.CharField(source='student.last_name', required=False)
    student_full_name = serializers.CharField(source='student.full_name', read_only=True)
    student_mother_fullname = serializers.CharField(source='student.mother_fullname')
    student_sex = serializers.CharField(source='student.sex')
    student_birthday_year = serializers.CharField(source='student.birthday_year')
    student_birthday_month = serializers.CharField(source='student.birthday_month')
    student_birthday_day = serializers.CharField(source='student.birthday_day')
    student_place_of_birth = serializers.CharField(source='student.place_of_birth', required=False)
    student_age = serializers.CharField(source='student.age', read_only=True)
    student_phone = serializers.CharField(source='student.phone', required=False)
    student_phone_prefix = serializers.CharField(source='student.phone_prefix', required=False)
    student_id_number = serializers.CharField(source='student.id_number', required=False)
    student_registered_in_unhcr = serializers.CharField(source='student.registered_in_unhcr', required=False)
    student_id_type = serializers.CharField(source='student.id_type.name', required=False)
    student_number = serializers.CharField(source='student.number', read_only=True)
    student_nationality = serializers.CharField(source='student.nationality.name', required=False)
    student_mother_nationality = serializers.CharField(source='student.mother_nationality.name', required=False)
    student_address = serializers.CharField(source='student.address', required=False)
    school_name = serializers.CharField(source='school.name', read_only=True)
    education_year = serializers.CharField(source='education_year.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    governorate = serializers.CharField(source='school.location.parent.name', read_only=True)
    district = serializers.CharField(source='school.location.name', read_only=True)
    last_school_name = serializers.CharField(source='last_school.name', read_only=True)
    last_school_number = serializers.CharField(source='last_school.number', read_only=True)
    last_informal_edu_round_name = serializers.CharField(source='last_informal_edu_round.name', read_only=True)
    last_informal_edu_final_result_name = serializers.CharField(source='last_informal_edu_final_result.name', read_only=True)
    last_education_level_name = serializers.CharField(source='last_education_level.name', read_only=True)

    class Meta:
        model = Enrollment
        fields = (
            'id',
            'new_registry',
            'student_outreached',
            'have_barcode',
            'outreach_barcode',
            'registration_date',
            'student_id',
            'student_registered_in_unhcr',
            'student_id_type',
            'student_id_number',
            'student_number',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'student_full_name',
            'student_mother_fullname',
            'student_birthday_year',
            'student_birthday_month',
            'student_birthday_day',
            'student_place_of_birth',
            'student_age',
            'student_sex',
            'student_nationality',
            'student_mother_nationality',
            'student_phone_prefix',
            'student_phone',
            'student_address',
            'governorate',
            'district',
            'school_number',
            'school_name',
            'education_year',
            'section_name',
            'classroom_name',
            'cycle',
            'number_in_previous_school',
            'last_education_level_name',
            'last_education_year',
            'last_school_type',
            'last_school_shift',
            'last_school_name',
            'last_school_number',
            'last_year_result',
            'participated_in_alp',
            'last_informal_edu_round_name',
            'last_informal_edu_final_result_name',
            'age_min_restricted',
            'age_max_restricted',
            'last_attendance_date',
            'last_absent_date',
            'created',
            'modified',
            'moved',
            'dropout_status',
            'disabled',
        )


class GradingImportSerializer(serializers.ModelSerializer):

    student_id = serializers.IntegerField(source='enrollment.student.id', required=False)

    class Meta:
        model = EnrollmentGrading
        fields = (
            'id',
            'enrollment_id',
            'student_id',
            'exam_term',
            'exam_result_arabic',
            'exam_result_language',
            'exam_result_education',
            'exam_result_geo',
            'exam_result_history',
            'exam_result_math',
            'exam_result_science',
            'exam_result_physic',
            'exam_result_chemistry',
            'exam_result_bio',
            'exam_result_linguistic_ar',
            'exam_result_linguistic_en',
            'exam_result_sociology',
            'exam_result_physical',
            'exam_result_artistic',
            'exam_result_mathematics',
            'exam_result_sciences',
            'exam_total',
            'exam_result',
        )
