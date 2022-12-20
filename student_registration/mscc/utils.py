
from student_registration.outreach.models import OutreachChild

def to_array(fields, obj):
    data = {}
    for field_name in fields:
        if hasattr(obj, field_name):
            data[field_name] = getattr(obj, field_name)

    return data

def get_outreach_child(initial,outreach_id,center_id):
    instance = OutreachChild.objects.get(id=outreach_id)
    initial['center'] = center_id
    initial['child_first_name'] = instance.first_name
    initial['child_father_name'] = instance.outreach_caregiver.father_name
    initial['child_last_name'] = instance.outreach_caregiver.last_name
    initial['child_mother_fullname'] = instance.outreach_caregiver.mother_full_name
    # # date_of_birth = models.CharField(max_length=200, blank=True, null=True)
    # # initial['child_birthday_year'] = instance.last_name
    # # initial['child_birthday_month'] = instance.last_name
    # # initial['child_birthday_day'] = instance.last_name
    initial['gender'] = instance.gender
    # # initial['child_nationality_id'] = instance.nationality
    initial['child_nationality_other'] = instance.nationality_other
    initial['child_address'] = instance.outreach_caregiver.address
    # # initial['child_disability_id'] = instance.disability
    initial['disability_other'] = instance.disability_other
    # # initial['child_marital_status'] = instance.family_status
    # # initial['main_caregiver_nationality_id'] = instance.outreach_caregiver.caregiver_nationality
    initial['main_caregiver_nationality_other'] = instance.outreach_caregiver.caregiver_nationality_other
    # # initial['child_marital_status'] = instance.family_status
    initial['individual_case_number'] = instance.child_unhcr_number
    # # initial[''] = instance.child_personal_id
    # initial['have_labour'] = instance.working_status
    # initial['labour_type'] = instance.work_type
    initial['labour_type_specify'] = instance.work_type_other
    initial['first_phone_number'] = instance.outreach_caregiver.primary_phone
    initial['first_phone_number_confirm'] = instance.outreach_caregiver.primary_phone
    initial['second_phone_number'] = instance.outreach_caregiver.secondary_phone
    initial['second_phone_number_confirm'] = instance.outreach_caregiver.secondary_phone
    # # initial['main_caregiver'] = instance.outreach_caregiver.main_caregiver
    initial['caregiver_first_name'] = instance.outreach_caregiver.caregiver_first_name
    initial['caregiver_middle_name'] = instance.outreach_caregiver.caregiver_father_name
    initial['caregiver_last_name'] = instance.outreach_caregiver.caregiver_last_name
    initial['caregiver_mother_name'] = instance.outreach_caregiver.caregiver_mother_name
    # # caregiver_dob
    # initial['id_type_id'] = instance.outreach_caregiver.id_type
    initial['case_number'] = instance.outreach_caregiver.unhcr_case_number
    initial['parent_individual_case_number'] = instance.outreach_caregiver.caregiver_unhcr_id
    initial['recorded_number'] = instance.outreach_caregiver.unhcr_barcode
    # # initial['id_type_id'] = instance.outreach_caregiver.caregiver_personal_id
    # initial['father_educational_level_id'] = instance.outreach_caregiver.father_education_level
    # initial['mother_educational_level_id'] = instance.outreach_caregiver.mother_education_level

    return initial
