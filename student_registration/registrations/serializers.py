
from rest_framework import serializers
from .models import Registration, RegisteringAdult, WaitingList, Complaint, Payment , HouseholdNotFound, ComplaintCategory
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

    def update(self, instance, validated_data):

        student_data = validated_data.pop('student', None)
        student_serializer = StudentSerializer(data=student_data)
        student_serializer.is_valid(raise_exception=True)
        student_serializer.instance = student_serializer.save()

        try:
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
            'last_informal_edu_year',
            'last_informal_edu_result',
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
            'last_education_level',
            'last_education_year',
            'owner'
        )


class ComplaintSerializer(serializers.ModelSerializer):
    complaint_id = serializers.IntegerField(source='id', read_only=True)
    complaint_type = serializers.CharField(source='complaint_category.complaint_type', read_only=True)
    complaint_category_name = serializers.CharField(source='complaint_category.name', read_only=True)
    adult_first_name = serializers.CharField(source='complaint_adult.first_name', read_only=True)
    adult_father_name = serializers.CharField(source='complaint_adult.father_name', read_only=True)
    adult_last_name = serializers.CharField(source='complaint_adult.last_name', read_only=True)
    adult_id_number = serializers.CharField(source='complaint_adult.id_number', read_only=True)
    adult_primary_phone = serializers.CharField(source='complaint_adult.primary_phone', read_only=True)
    student_first_name = serializers.CharField(source='complaint_student_refused_entrance.first_name', read_only=True)
    student_father_name = serializers.CharField(source='complaint_student_refused_entrance.father_name', read_only=True)
    student_last_name = serializers.CharField(source='complaint_student_refused_entrance.last_name', read_only=True)
    not_found_first_name = serializers.CharField(source='household_not_found.first_name', read_only=True)
    not_found_father_name = serializers.CharField(source='household_not_found.father_name', read_only=True)
    not_found_last_name = serializers.CharField(source='household_not_found.last_name', read_only=True)
    not_found_id_number = serializers.CharField(source='household_not_found.id_number', read_only=True)
    not_found_primary_phone = serializers.CharField(source='household_not_found.primary_phone', read_only=True)


    class Meta:
        model = Complaint
        fields = (
            'complaint_id',
            'complaint_adult',
            'complaint_type',
            'complaint_Other_type_specify',
            'complaint_category',
            'complaint_category_name',
            'complaint_note',
            'complaint_solution',
            'created',
            'modified',
            'complaint_status',
            'complaint_resolution_date',
            'complaint_bank_date_of_incident',
            'complaint_bank_phone_used',
            'complaint_bank_service_requested',
            'complaint_student_refused_entrance',
            'student_first_name',
            'student_father_name',
            'student_last_name',
            'complaint_Other_type_specify',
            'household_not_found',
            'adult_first_name',
            'adult_father_name',
            'adult_last_name',
            'adult_id_number',
            'adult_primary_phone',
            'not_found_first_name',
            'not_found_father_name',
            'not_found_last_name',
            'not_found_id_number',
            'not_found_primary_phone',
            'owner'
        )
class HouseholdNotFoundSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)

    def create(self, validated_data):

        try:
            instance = HouseholdNotFound.objects.create(**validated_data)
            instance.save()

        except Exception as ex:
            raise serializers.ValidationError({'Household not found instance': ex.message})

        return instance

    class Meta:
        model = HouseholdNotFound
        fields = (
            'id',
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
            'relation_to_householdhead',
            'address',
            'primary_phone',
            'primary_phone_answered',
            'secondary_phone',
            'secondary_phone_answered',
            'number_children_five_to_nine',
            'number_children_ten_to_seventeen'
        )

class ComplaintHouseholdNotFoundSerializer(serializers.ModelSerializer):

    complaint_id = serializers.IntegerField(source='id', read_only=True)
    complaint_type = serializers.CharField(source='complaint_category.complaint_type', read_only=True)
    complaint_category_name = serializers.CharField(source='complaint_category.name', read_only=True)
    hh_id = serializers.IntegerField(source='household_not_found.id', read_only=True)
    id_type = serializers.IntegerField(source='household_not_found.id_type', read_only=True)
    id_number = serializers.IntegerField(source='household_not_found.id_number', read_only=True)
    first_name = serializers.CharField(source='household_not_found.first_name')
    father_name = serializers.CharField(source='household_not_found.father_name')
    last_name = serializers.CharField(source='household_not_found.last_name')
    mother_fullname = serializers.CharField(source='household_not_found.mother_fullname')
    sex = serializers.CharField(source='household_not_found.sex')
    nationality = serializers.CharField(source='household_not_found.nationality', read_only=True)
    birthday_year = serializers.CharField(source='household_not_found.birthday_year')
    birthday_month = serializers.CharField(source='household_not_found.birthday_month')
    birthday_day = serializers.CharField(source='household_not_found.birthday_day')
    relation_to_householdhead = serializers.CharField(source='household_not_found.relation_to_householdhead')
    address = serializers.CharField(source='household_not_found.address')
    primary_phone = serializers.CharField(source='household_not_found.primary_phone')
    primary_phone_answered = serializers.CharField(source='household_not_found.primary_phone_answered')
    secondary_phone = serializers.CharField(source='household_not_found.secondary_phone')
    secondary_phone_answered = serializers.CharField(source='household_not_found.secondary_phone_answered')
    number_children_five_to_nine = serializers.CharField(source='household_not_found.number_children_five_to_nine')
    number_children_ten_to_seventeen = serializers.CharField(source='household_not_found.number_children_ten_to_seventeen')

    class Meta:
        model = Complaint
        fields = (
            'complaint_id',
            'complaint_type',
            'complaint_category',
            'complaint_category_name',
            'complaint_note',
            'complaint_solution',
            'created',
            'modified',
            'complaint_status',
            'complaint_resolution_date',
            'hh_id',
            'id_type',
            'id_number',
            'first_name',
            'father_name',
            'last_name',
            'mother_fullname',
            'sex',
            'nationality',
            'birthday_day',
            'birthday_month',
            'birthday_year',
            'relation_to_householdhead',
            'address',
            'primary_phone',
            'primary_phone_answered',
            'secondary_phone',
            'secondary_phone_answered',
            'number_children_five_to_nine',
            'number_children_ten_to_seventeen'
        )


class PaymentSerializer(serializers.ModelSerializer):
    payment_id = serializers.IntegerField(source='id', read_only=True)

    class Meta:
        model = Payment
        fields = (
            'payment_id',
            'payment_list_number',
            'payment_amount',
            'payment_month',
            'payment_year',
            'payment_date',
        )


class RegistrationChildSerializer(serializers.ModelSerializer):

    student_id = serializers.IntegerField(source='student.id', read_only=True)
    reg_id = serializers.IntegerField(source='id', read_only=True)
    number = serializers.CharField(source='student.number', read_only=True)
    first_name = serializers.CharField(source='student.first_name')
    father_name = serializers.CharField(source='student.father_name')
    last_name = serializers.CharField(source='student.last_name')
    mother_fullname = serializers.CharField(source='student.mother_fullname')
    sex = serializers.CharField(source='student.sex')
    birthday_year = serializers.CharField(source='student.birthday_year')
    birthday_month = serializers.CharField(source='student.birthday_month')
    birthday_day = serializers.CharField(source='student.birthday_day')
    calculate_age = serializers.CharField(source='student.calculate_age', read_only=True)
    id_number = serializers.CharField(source='student.id_number')
    age = serializers.CharField(source='student.age')
    school_name = serializers.CharField(source='school.name', read_only=True)
    location_id = serializers.CharField(source='school.location_id', read_only=True)
    school_changed_to_verify_location_id = serializers.CharField(source='school_changed_to_verify.location_id',
                                                                 read_only=True)
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
            'reg_id',
            'school',
            'school_name',
            'location_id',
            'school_changed_to_verify',
            'school_changed_to_verify_location_id',
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
            'calculate_age',
            'id_number',
            'owner',
            'number'
        )


class RegisteringAdultSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    number = serializers.CharField(read_only=True)
    children = RegistrationChildSerializer(many=True, read_only=True)
    complaints = ComplaintSerializer(many=True, read_only=True)
    payments = PaymentSerializer(many=True, read_only=True)
    no_logner_eligible_reason_name = serializers.CharField(source='no_logner_eligible_reason.name', read_only=True)

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
            'beneficiary_changed_id_type',
            'beneficiary_changed_id_number',
            'beneficiary_changed_verify',
            'beneficiary_changed_first_name',
            'beneficiary_changed_last_name',
            'beneficiary_changed_father_name',
            'beneficiary_changed_mother_full_name',
            'beneficiary_changed_birthday_year',
            'beneficiary_changed_birthday_month',
            'beneficiary_changed_birthday_day',
            'beneficiary_changed_phone',
            'beneficiary_changed_relation_to_householdhead',
            'beneficiary_changed_same_as_caller',
            'beneficiary_changed_reason',
            'beneficiary_specify_reason',
            'beneficiary_changed_gender',
            'beneficiary_changed_comment',
            'beneficiary_changed_status',
            'card_last_four_digits',
            'card_distribution_date',
            'card_status',
            'household_suspended',
            'duplicate_card_first_card_case_number',
            'duplicate_card_first_card_last_four_digits',
            'duplicate_card_second_card_case_number',
            'duplicate_card_secondcard_last_four_digits',
            'no_logner_eligible',
            'no_logner_eligible_reason_name',
            'no_logner_eligible_reason',
            'no_logner_eligible_specify',
            'no_logner_eligible_comment',
            'complaints',
            'payments'
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






class ComplaintCategorySerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(read_only=True)
    complaints = ComplaintSerializer(many=True, read_only=True)
    class Meta:
        model = ComplaintCategory
        fields = (
            'id',
            'name',
            'complaint_type',
            'complaints'
        )
