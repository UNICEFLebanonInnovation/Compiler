
import json

from rest_framework import serializers
from .models import CLM, BLN, RS, CBECE, SelfPerceptionGrades


def create_instance(validated_data, model):
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

    if 'internal' in validated_data and validated_data['internal']:
        if validated_data['internal'] == 'yes':
            if 'internal_number' in validated_data and validated_data['internal_number']:
                internal_number = validated_data['internal_number']
                queryset = model.objects.filter(internal_number=internal_number).first()

                if queryset and queryset.student:
                    student_id = queryset.student.id
                    student_serializer = StudentSerializer(Student.objects.get(id=student_id), data=student_data)
                    student_serializer.is_valid(raise_exception=True)
                    student_serializer.instance = student_serializer.save()
                    # model.student = queryset.student
                else:
                    student_serializer = StudentSerializer(data=student_data)
                    student_serializer.is_valid(raise_exception=True)
                    student_serializer.instance = student_serializer.save()

    try:
        instance = model.objects.create(**validated_data)
        instance.student = student_serializer.instance
        instance.save()

    except Exception as ex:
        raise serializers.ValidationError({'Enrollment instance': ex.message})

    return instance


def update_instance(instance, validated_data):
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


class CLMSerializer(serializers.ModelSerializer):

    original_id = serializers.IntegerField(source='id', read_only=True)
    # round_name = serializers.CharField(source='round.name', read_only=True)
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
    student_birthday = serializers.CharField(source='student.birthday', read_only=True)
    student_nationality = serializers.CharField(source='student.nationality')
    student_nationality_id = serializers.CharField(source='student.nationality.id', read_only=True)
    student_address = serializers.CharField(source='student.address', required=False)
    student_p_code = serializers.CharField(source='student.p_code', required=False)
    student_id_number = serializers.CharField(source='student.id_number', required=False)
    student_family_status = serializers.CharField(source='student.family_status', required=False)
    student_have_children = serializers.CharField(source='student.have_children', required=False)
    comments = serializers.CharField(required=False)
    unsuccessful_posttest_reason = serializers.CharField(required=False)
    unsuccessful_pretest_reason = serializers.CharField(required=False)

    student_outreach_child = serializers.IntegerField(source='student.outreach_child', required=False)
    student_outreach_child_id = serializers.IntegerField(source='student.outreach_child.id', read_only=True)

    csrfmiddlewaretoken = serializers.IntegerField(source='owner.id', read_only=True)
    save = serializers.IntegerField(source='owner.id', read_only=True)
    internal = serializers.CharField(read_only=True)
    enrollment_id = serializers.IntegerField(source='id', read_only=True)
    search_clm_student = serializers.CharField(source='student.full_name', read_only=True)
    search_barcode = serializers.CharField(source='outreach_barcode', read_only=True)

    class Meta:
        model = CLM
        fields = (
            'id',
            'original_id',
            # 'round_name',
            'enrollment_id',
            'student_id',
            'round',
            'partner',
            'language',
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
            'student_birthday',
            'student_nationality',
            'student_nationality_id',
            'student_address',
            'student_p_code',
            'student_id_number',
            'internal_number',
            'owner',
            'modified_by',
            'governorate',
            'district',
            'location',
            'outreach_barcode',
            'disability',
            'student_family_status',
            'student_have_children',
            # 'have_labour',
            # 'labours',
            # 'labour_hours',
            'hh_educational_level',
            'participation',
            'barriers',
            'learning_result',
            'student_outreached',
            'new_registry',
            'have_barcode',
            'search_clm_student',
            'search_barcode',
            'csrfmiddlewaretoken',
            'save',
            'comments',
            'unsuccessful_posttest_reason',
            'unsuccessful_pretest_reason',
            'internal',
        )


class BLNSerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = BLN
        fields = CLMSerializer.Meta.fields + (
            # 'cycle',
            # 'referral',
            'have_labour',
            'labours',
            'labour_hours',
            'student_family_status',
            'student_have_children',
        )


class RSSerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = RS
        fields = CLMSerializer.Meta.fields + (
            'type',
            'site',
            'school',
            'shift',
            'grade',
            'section',
            'referral',
            'have_labour',
            'labours',
            'labour_hours',
            'registered_in_school',
            'student_family_status',
            'student_have_children',
            'pre_test_arabic',
            'pre_test_language',
            'pre_test_math',
            'pre_test_science',
            'post_test_arabic',
            'post_test_language',
            'post_test_math',
            'post_test_science',
        )


class CBECESerializer(CLMSerializer):

    def create(self, validated_data):
        return create_instance(validated_data=validated_data, model=self.Meta.model)

    def update(self, instance, validated_data):
        return update_instance(instance=instance, validated_data=validated_data)

    class Meta:
        model = CBECE
        fields = CLMSerializer.Meta.fields + (
            'cycle',
            'site',
            'school',
            'referral',
            'child_muac',
            'final_grade',
        )


class SelfPerceptionGradesSerializer(serializers.ModelSerializer):

    class Meta:
        model = SelfPerceptionGrades
        fields = '__all__'
