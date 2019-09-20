from rest_framework import serializers


class EnrollmentSerializer(serializers.ModelSerializer):

    original_id = serializers.IntegerField(source='id', read_only=True)
    staff_id = serializers.IntegerField(source='student.id', required=False)
    staff_first_name = serializers.CharField(source='student.first_name')
    staff_father_name = serializers.CharField(source='student.father_name')
    staff_last_name = serializers.CharField(source='student.last_name')
    staff_full_name = serializers.CharField(source='student.full_name', read_only=True)
    staff_mother_fullname = serializers.CharField(source='student.mother_fullname')
    staff_sex = serializers.CharField(source='student.sex')
    staff_birthday_year = serializers.CharField(source='student.birthday_year')
    staff_birthday_month = serializers.CharField(source='student.birthday_month')
    staff_birthday_day = serializers.CharField(source='student.birthday_day')
    staff_place_of_birth = serializers.CharField(source='student.place_of_birth', required=False)
    staff_age = serializers.CharField(source='student.age', read_only=True)
    staff_phone = serializers.CharField(source='student.phone', required=False)
    staff_phone_prefix = serializers.CharField(source='student.phone_prefix', required=False)
    staff_id_number = serializers.CharField(source='student.id_number', required=False)
    staff_registered_in_unhcr = serializers.CharField(source='student.registered_in_unhcr', required=False)
    staff_id_type = serializers.CharField(source='student.id_type', required=False)
    staff_id_type_name = serializers.CharField(source='student.id_type.name', read_only=True)
    staff_number = serializers.CharField(source='student.number', read_only=True)
    staff_nationality = serializers.CharField(source='student.nationality', required=False)
    staff_mother_nationality = serializers.CharField(source='student.mother_nationality', required=False)
    staff_address = serializers.CharField(source='student.address', required=False)
    school_name = serializers.CharField(source='school.name', read_only=True)
    education_year_name = serializers.CharField(source='education_year.name', read_only=True)
    school_number = serializers.CharField(source='school.number', read_only=True)
    section_name = serializers.CharField(source='section.name', read_only=True)
    classroom_name = serializers.CharField(source='classroom.name', read_only=True)
    governorate_name = serializers.CharField(source='school.location.parent.name', read_only=True)
    location = serializers.CharField(source='school.location.name', read_only=True)
    staff_nationality_id = serializers.CharField(source='student.nationality.id', read_only=True)
    staff_mother_nationality_id = serializers.CharField(source='student.mother_nationality.id', read_only=True)

    staff_image = serializers.ImageField(source='staff.image', read_only=True)
    csrfmiddlewaretoken = serializers.IntegerField(source='owner.id', read_only=True)
    save = serializers.IntegerField(source='owner.id', read_only=True)
    staffenroll_id = serializers.IntegerField(source='id', read_only=True)


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
            'std_image',
        )
