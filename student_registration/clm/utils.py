import io
import xlwt
import csv
from datetime import date
from django.http import HttpResponse, FileResponse

from .models import ABLN_FC, BLN_FC, CBECE_FC, RS_FC

import copy

import logging

logger = logging.getLogger(__name__)

def is_allowed_create(programme):

    from student_registration.schools.models import CLMRound

    try:
        current = date.today()
        current_round = CLMRound.objects.all()

        if programme == 'BLN':
            current_round = current_round.get(current_round_bln=True)
            if current_round.start_date_bln < current < current_round.end_date_bln:
                return True
            return False

        if programme == 'ABLN':
            current_round = current_round.get(current_round_abln=True)
            if current_round.start_date_abln < current < current_round.end_date_abln:
                return True
            return False

        if programme == 'CBECE':
            current_round = current_round.get(current_round_cbece=True)
            if current_round.start_date_cbece < current < current_round.end_date_cbece:
                return True
            return False

        if programme == 'Inclusion':
            current_round = current_round.get(current_round_inclusion=True)
            if current_round.start_date_inclusion < current < current_round.end_date_inclusion:
                return True
            return False

        if programme == 'RS':
            current_round = current_round.get(current_round_rs=True)
            if current_round.start_date_rs < current < current_round.end_date_rs:
                return True
            return False

        if programme == 'GeneralQuestionnaire':
            return True

    except Exception as ex:
        print(ex.message)
        return False


def is_allowed_edit(programme):

    from student_registration.schools.models import CLMRound

    try:
        current = date.today()
        current_round = CLMRound.objects.all()

        if programme == 'BLN':
            current_round = current_round.get(current_round_bln=True)
            if current_round.start_date_bln_edit < current < current_round.end_date_bln_edit:
                return True
            return False

        if programme == 'ABLN':
            current_round = current_round.get(current_round_abln=True)
            if current_round.start_date_abln_edit < current < current_round.end_date_abln_edit:
                return True
            return False

        if programme == 'CBECE':
            current_round = current_round.get(current_round_cbece=True)
            if current_round.start_date_cbece_edit < current < current_round.end_date_cbece_edit:
                return True
            return False

        if programme == 'Inclusion':
            current_round = current_round.get(current_round_inclusion=True)
            if current_round.start_date_inclusion_edit < current < current_round.end_date_inclusion_edit:
                return True
            return False

        if programme == 'RS':
            current_round = current_round.get(current_round_rs=True)
            if current_round.start_date_rs_edit < current < current_round.end_date_rs_edit:
                return True
            return False
        if programme == 'GeneralQuestionnaire':
            return True

    except Exception as ex:
        print(ex.message)
        return False



def build_xls_extraction(queryset_students, queryset_fc ):
    buffer = io.BytesIO()

    # Personnel
    wbStudent = xlwt.Workbook(encoding='utf-8')
    ws = wbStudent.add_sheet('Student')

    # Sheet header, first row
    row_num_student = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns = [
        'enrollment_id',
        'First time registered?',
        'Partner',
        'CLM Round',
        'Governorate',
        'District',
        'Cadaster',
        'Location',
        'Center',
        'The language supported in the program',
        'Student Address',
        'Registration level',
        'first attendance date',
        'ID number',
        'unique number',
        'First name',
        'Father name',
        'Last name',
        'Mother fullname',
        'Sex',
        'Student Nationality',
        'Student Nationality Specify',
        'Birthday - day',
        'Birthday - month',
        'Birthday - year',
        'P-Code If a child lives in a tent / Brax in a random camp',
        'Does the child have any disability or special need?',
        'Education status',
        'Miss school date',
        'Internal number',
        'RIMS  case number',
        'Source of Identification',
        'Source of Identification Specify',
        'Source of Transportation',
        'What is the educational level of the mother?',
        'What is the educational level of the father?',
        'Phone number',
        'Phone number confirm',
        'phone owner',
        'Second Phone number',
        'Second Phone number confirm',
        'Second phone owner',
        'Main Caregiver',
        'main caregiver nationality',
        'other caregiver relationship',
        'main caregiver nationality Other ',
        'Caretaker first name',
        'Caretaker middle name',
        'Caretaker last name',
        'Caretaker mother name',
        'ID Type',
        'UNHCR case number',
        'UNHCR case number confirm',
        'Parent individual ID',
        'Parent individual ID confirm',
        'Child individual ID',
        'Child individual ID confirm',
        'UNHCR recorded barcode',
        'UNHCR recorded barcode confirm',
        'Parent Lebanese ID number',
        'Parent Lebanese ID number confirm',
        'Child Lebanese ID number',
        'Child Lebanese ID number confirm',
        'Parent Syrian ID number',
        'Parent Syrian ID number confirm',
        'Child Syrian ID number',
        'Child Syrian ID number confirm',
        'Parent Palestinian ID number',
        'Parent Palestinian ID number confirm',
        'Child Palestinian ID number',
        'Child Palestinian ID number confirm',
        'ID number of the Caretaker',
        'ID number of the Caretaker confirm',
        'ID number of the child',
        'ID number of the child confirm',
        'What is the family status of the child?',
        'Does the child have children?',
        'Child number of children',
        'Does the child participate in work?',
        'What is the type of work?',
        'Please specify',
        'How many hours does this child work in a day?',
        'Child weekly income',
        'Level of participation / Absence',
        'The main barriers affecting the daily attendance and performance of the child or drop out of',
        'Please specify',
        'test_done',
        'round_complete',
        'Did the child receive basic stationery?',
        'Did the child benefit from the PSS kit?',
        'Based on the overall score, what is the recommended learning path?',
        'Please specify',
        'cp_referral',
        'referal_wash',
        'referal_health',
        'referal_other',
        'referal_other_specify',
        'child_received_books',
        'child_received_printout',
        'child_received_internet',
        'Please enter the number phone calls',
        'Phone call Result of follow up',
        'Please enter the number of house visits',
        'House VisitvResult of follow up',
        'Please enter the number of family visit',
        'Familiy Visit Result of follow up',
        'Parent attended visits',
        'pss session attended',
        'pss session number',
        'pss session modality',
        'pss parent attended',
        'pss parent attended other',
        'Attended covid Session?',
        'Please enter the number of sessions',
        'Please indicate modality',
        'Parent who attended the parents meeting',
        'Please specify',
        'Attended followup Session',
        'Please enter the number of sessions',
        'Please indicate modality',
        'Parent who attended the parents meeting',
        'Please specify',
        'pre test attended arabic',
        'pre test modality arabic',
        'pre test arabic',
        'pre test attended english',
        'pre test modality english',
        'pre test english',
        'pre test attended psychomotor',
        'pre test modality psychomotor',
        'pre test psychomotor',
        'pre test attended artistic',
        'pre test modality artistic',
        'pre test artistic',
        'pre test attended math',
        'pre test modality math',
        'pre test math',
        'pre test attended social',
        'pre test modality social',
        'pre test social emotional',
        'post test attended arabic',
        'post test modality arabic',
        'post test arabic',
        'post test attended english',
        'post test modality english',
        'post test english',
        'post test attended psychomotor',
        'post test modality psychomotor',
        'post test psychomotor',
        'post test attended artistic',
        'post test modality artistic',
        'post test artistic',
        'post test attended math',
        'post test modality math',
        'post test math',
        'post test attended social',
        'post test modality social',
        'post test social emotional',
        'Was the child involved in remote learning?',
        'what other reasons for this child not being engaged?',
        'reasons not engaged other',
        'Does the family have reliable internet service in their area during remote learning?',
        'Did both girls and boys in the same family participate in the class and have access to the phone/',
        'Explain',
        'Frequency of Child Engagement in remote learning?',
        'How well did the child meet the learning outcomes?',
        'How do you rate the parents learning support provided to the child through this Remote',
        'Has the child directly been reached with awareness messaging on Covid-19 and prevention measures?',
        'How often?',
        'Has the parents directly been reached with awareness messaging on Covid-19 and prevention',
        'How often?',
        'Was any follow-up done to ensure messages were well received, understood and adopted?',
        'With who child and/or caregiver?',
        'Reason why not doing the Pre-test',
        'Reason why not doing the Post-test',
        'Student outreached?',
        'owner',
        'modified_by',
        'created',
        'modified',
    ]

    for col_num in range(len(columns)):
        ws.write(row_num_student, col_num, columns[col_num], font_style)

    # Sheet body, remaining rows
    font_style = xlwt.XFStyle()

    qs = queryset_students.extra(select={

        'pre_test_attended_arabic': "pre_test->>'BLN_ASSESSMENT/attended_arabic'",
        'pre_test_modality_arabic': "pre_test->>'BLN_ASSESSMENT/modality_arabic'",
        'pre_test_arabic': "pre_test->>'BLN_ASSESSMENT/arabic'",

        'pre_test_attended_english': "pre_test->>'BLN_ASSESSMENT/attended_english'",
        'pre_test_modality_english': "pre_test->>'BLN_ASSESSMENT/modality_english'",
        'pre_test_english': "pre_test->>'BLN_ASSESSMENT/english'",

        'pre_test_attended_psychomotor': "pre_test->>'BLN_ASSESSMENT/attended_psychomotor'",
        'pre_test_modality_psychomotor': "pre_test->>'BLN_ASSESSMENT/modality_psychomotor'",
        'pre_test_psychomotor': "pre_test->>'BLN_ASSESSMENT/psychomotor'",

        'pre_test_attended_artistic': "pre_test->>'BLN_ASSESSMENT/attended_artistic'",
        'pre_test_modality_artistic': "pre_test->>'BLN_ASSESSMENT/modality_artistic'",
        'pre_test_artistic': "pre_test->>'BLN_ASSESSMENT/artistic'",

        'pre_test_attended_math': "pre_test->>'BLN_ASSESSMENT/attended_math'",
        'pre_test_modality_math': "pre_test->>'BLN_ASSESSMENT/modality_math'",
        'pre_test_math': "pre_test->>'BLN_ASSESSMENT/math'",

        'pre_test_attended_social': "pre_test->>'BLN_ASSESSMENT/attended_social'",
        'pre_test_modality_social': "pre_test->>'BLN_ASSESSMENT/modality_social'",
        'pre_test_social_emotional': "pre_test->>'BLN_ASSESSMENT/social_emotional'",

        'post_test_attended_arabic': "post_test->>'BLN_ASSESSMENT/attended_arabic'",
        'post_test_modality_arabic': "post_test->>'BLN_ASSESSMENT/modality_arabic'",
        'post_test_arabic': "post_test->>'BLN_ASSESSMENT/arabic'",

        'post_test_attended_english': "post_test->>'BLN_ASSESSMENT/attended_english'",
        'post_test_modality_english': "post_test->>'BLN_ASSESSMENT/modality_english'",
        'post_test_english': "post_test->>'BLN_ASSESSMENT/english'",

        'post_test_attended_psychomotor': "post_test->>'BLN_ASSESSMENT/attended_psychomotor'",
        'post_test_modality_psychomotor': "post_test->>'BLN_ASSESSMENT/modality_psychomotor'",
        'post_test_psychomotor': "post_test->>'BLN_ASSESSMENT/psychomotor'",

        'post_test_attended_artistic': "post_test->>'BLN_ASSESSMENT/attended_artistic'",
        'post_test_modality_artistic': "post_test->>'BLN_ASSESSMENT/modality_artistic'",
        'post_test_artistic': "post_test->>'BLN_ASSESSMENT/artistic'",

        'post_test_attended_math': "post_test->>'BLN_ASSESSMENT/attended_math'",
        'post_test_modality_math': "post_test->>'BLN_ASSESSMENT/modality_math'",
        'post_test_math': "post_test->>'BLN_ASSESSMENT/math'",

        'post_test_attended_social': "post_test->>'BLN_ASSESSMENT/attended_social'",
        'post_test_modality_social': "post_test->>'BLN_ASSESSMENT/modality_social'",
        'post_test_social_emotional': "post_test->>'BLN_ASSESSMENT/social_emotional'",
    })

    rows = qs.order_by('id')

    for row in rows:
        row_num_student += 1
        ws.write(row_num_student, col_num, row.id , font_style)
        ws.write(row_num_student, col_num, row.new_registry , font_style)
        ws.write(row_num_student, col_num, row.partner__name , font_style)
        ws.write(row_num_student, col_num, row.round__name , font_style)
        ws.write(row_num_student, col_num, row.governorate__name_en , font_style)
        ws.write(row_num_student, col_num, row.district__name_en , font_style)
        ws.write(row_num_student, col_num, row.cadaster__name_en , font_style)
        ws.write(row_num_student, col_num, row.location , font_style)
        ws.write(row_num_student, col_num, row.center__name , font_style)
        ws.write(row_num_student, col_num, row.language , font_style)
        ws.write(row_num_student, col_num, row.student__address , font_style)
        ws.write(row_num_student, col_num, row.registration_level , font_style)
        ws.write(row_num_student, col_num, row.first_attendance_date , font_style)
        ws.write(row_num_student, col_num, row.student__id_number , font_style)
        ws.write(row_num_student, col_num, row.student__number , font_style)
        ws.write(row_num_student, col_num, row.student__first_name , font_style)
        ws.write(row_num_student, col_num, row.student__father_name , font_style)
        ws.write(row_num_student, col_num, row.student__last_name , font_style)
        ws.write(row_num_student, col_num, row.student__mother_fullname , font_style)
        ws.write(row_num_student, col_num, row.student__sex , font_style)
        ws.write(row_num_student, col_num, row.student__nationality__name , font_style)
        ws.write(row_num_student, col_num, row.other_nationality , font_style)
        ws.write(row_num_student, col_num, row.student__birthday_day , font_style)
        ws.write(row_num_student, col_num, row.student__birthday_month , font_style)
        ws.write(row_num_student, col_num, row.student__birthday_year , font_style)
        ws.write(row_num_student, col_num, row.student__p_code , font_style)
        ws.write(row_num_student, col_num, row.disability__name_en , font_style)
        ws.write(row_num_student, col_num, row.education_status , font_style)
        ws.write(row_num_student, col_num, row.miss_school_date , font_style)
        ws.write(row_num_student, col_num, row.internal_number , font_style)
        ws.write(row_num_student, col_num, row.rims_case_number , font_style)
        ws.write(row_num_student, col_num, row.source_of_identification , font_style)
        ws.write(row_num_student, col_num, row.source_of_identification_specify , font_style)
        ws.write(row_num_student, col_num, row.source_of_transportation , font_style)
        ws.write(row_num_student, col_num, row.hh_educational_level__name , font_style)
        ws.write(row_num_student, col_num, row.father_educational_level__name , font_style)
        ws.write(row_num_student, col_num, row.phone_number , font_style)
        ws.write(row_num_student, col_num, row.phone_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.phone_owner , font_style)
        ws.write(row_num_student, col_num, row.second_phone_number , font_style)
        ws.write(row_num_student, col_num, row.second_phone_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.second_phone_owner , font_style)
        ws.write(row_num_student, col_num, row.main_caregiver , font_style)
        ws.write(row_num_student, col_num, row.main_caregiver_nationality__name , font_style)
        ws.write(row_num_student, col_num, row.other_caregiver_relationship , font_style)
        ws.write(row_num_student, col_num, row.main_caregiver_nationality_other , font_style)
        ws.write(row_num_student, col_num, row.caretaker_first_name , font_style)
        ws.write(row_num_student, col_num, row.caretaker_middle_name , font_style)
        ws.write(row_num_student, col_num, row.caretaker_last_name , font_style)
        ws.write(row_num_student, col_num, row.caretaker_mother_name , font_style)
        ws.write(row_num_student, col_num, row.id_type , font_style)
        ws.write(row_num_student, col_num, row.case_number , font_style)
        ws.write(row_num_student, col_num, row.case_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.parent_individual_case_number , font_style)
        ws.write(row_num_student, col_num, row.parent_individual_case_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.individual_case_number , font_style)
        ws.write(row_num_student, col_num, row.individual_case_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.recorded_number , font_style)
        ws.write(row_num_student, col_num, row.recorded_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.parent_national_number , font_style)
        ws.write(row_num_student, col_num, row.parent_national_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.national_number , font_style)
        ws.write(row_num_student, col_num, row.national_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.parent_syrian_national_number , font_style)
        ws.write(row_num_student, col_num, row.parent_syrian_national_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.syrian_national_number , font_style)
        ws.write(row_num_student, col_num, row.syrian_national_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.parent_sop_national_number , font_style)
        ws.write(row_num_student, col_num, row.parent_sop_national_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.sop_national_number , font_style)
        ws.write(row_num_student, col_num, row.sop_national_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.parent_other_number , font_style)
        ws.write(row_num_student, col_num, row.parent_other_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.other_number , font_style)
        ws.write(row_num_student, col_num, row.other_number_confirm , font_style)
        ws.write(row_num_student, col_num, row.student__family_status , font_style)
        ws.write(row_num_student, col_num, row.student__have_children , font_style)
        ws.write(row_num_student, col_num, row.student_number_children , font_style)
        ws.write(row_num_student, col_num, row.have_labour_single_selection , font_style)
        ws.write(row_num_student, col_num, row.labours_single_selection , font_style)
        ws.write(row_num_student, col_num, row.labours_other_specify , font_style)
        ws.write(row_num_student, col_num, row.labour_hours , font_style)
        ws.write(row_num_student, col_num, row.labour_weekly_income , font_style)
        ws.write(row_num_student, col_num, row.participation , font_style)
        ws.write(row_num_student, col_num, row.barriers_single , font_style)
        ws.write(row_num_student, col_num, row.barriers_other , font_style)
        ws.write(row_num_student, col_num, row.test_done , font_style)
        ws.write(row_num_student, col_num, row.round_complete , font_style)
        ws.write(row_num_student, col_num, row.basic_stationery , font_style)
        ws.write(row_num_student, col_num, row.pss_kit , font_style)
        ws.write(row_num_student, col_num, row.learning_result , font_style)
        ws.write(row_num_student, col_num, row.learning_result_other , font_style)
        ws.write(row_num_student, col_num, row.cp_referral , font_style)
        ws.write(row_num_student, col_num, row.referal_wash , font_style)
        ws.write(row_num_student, col_num, row.referal_health , font_style)
        ws.write(row_num_student, col_num, row.referal_other , font_style)
        ws.write(row_num_student, col_num, row.referal_other_specify , font_style)
        ws.write(row_num_student, col_num, row.child_received_books , font_style)
        ws.write(row_num_student, col_num, row.child_received_printout , font_style)
        ws.write(row_num_student, col_num, row.child_received_internet , font_style)
        ws.write(row_num_student, col_num, row.phone_call_number , font_style)
        ws.write(row_num_student, col_num, row.phone_call_follow_up_result , font_style)
        ws.write(row_num_student, col_num, row.house_visit_number , font_style)
        ws.write(row_num_student, col_num, row.house_visit_follow_up_result , font_style)
        ws.write(row_num_student, col_num, row.family_visit_number , font_style)
        ws.write(row_num_student, col_num, row.family_visit_follow_up_result , font_style)
        ws.write(row_num_student, col_num, row.parent_attended_visits , font_style)
        ws.write(row_num_student, col_num, row.pss_session_attended , font_style)
        ws.write(row_num_student, col_num, row.pss_session_number , font_style)
        ws.write(row_num_student, col_num, row.pss_session_modality , font_style)
        ws.write(row_num_student, col_num, row.pss_parent_attended , font_style)
        ws.write(row_num_student, col_num, row.pss_parent_attended_other , font_style)
        ws.write(row_num_student, col_num, row.covid_session_attended , font_style)
        ws.write(row_num_student, col_num, row.covid_session_number , font_style)
        ws.write(row_num_student, col_num, row.covid_session_modality , font_style)
        ws.write(row_num_student, col_num, row.covid_parent_attended , font_style)
        ws.write(row_num_student, col_num, row.covid_parent_attended_other , font_style)
        ws.write(row_num_student, col_num, row.followup_session_attended , font_style)
        ws.write(row_num_student, col_num, row.followup_session_number , font_style)
        ws.write(row_num_student, col_num, row.followup_session_modality , font_style)
        ws.write(row_num_student, col_num, row.followup_parent_attended , font_style)
        ws.write(row_num_student, col_num, row.followup_parent_attended_other , font_style)
        ws.write(row_num_student, col_num, row.pre_test_attended_arabic , font_style)
        ws.write(row_num_student, col_num, row.pre_test_modality_arabic , font_style)
        ws.write(row_num_student, col_num, row.pre_test_arabic , font_style)
        ws.write(row_num_student, col_num, row.pre_test_attended_english , font_style)
        ws.write(row_num_student, col_num, row.pre_test_modality_english , font_style)
        ws.write(row_num_student, col_num, row.pre_test_english , font_style)
        ws.write(row_num_student, col_num, row.pre_test_attended_psychomotor , font_style)
        ws.write(row_num_student, col_num, row.pre_test_modality_psychomotor , font_style)
        ws.write(row_num_student, col_num, row.pre_test_psychomotor , font_style)
        ws.write(row_num_student, col_num, row.pre_test_attended_artistic , font_style)
        ws.write(row_num_student, col_num, row.pre_test_modality_artistic , font_style)
        ws.write(row_num_student, col_num, row.pre_test_artistic , font_style)
        ws.write(row_num_student, col_num, row.pre_test_attended_math , font_style)
        ws.write(row_num_student, col_num, row.pre_test_modality_math , font_style)
        ws.write(row_num_student, col_num, row.pre_test_math , font_style)
        ws.write(row_num_student, col_num, row.pre_test_attended_social , font_style)
        ws.write(row_num_student, col_num, row.pre_test_modality_social , font_style)
        ws.write(row_num_student, col_num, row.pre_test_social_emotional , font_style)
        ws.write(row_num_student, col_num, row.post_test_attended_arabic , font_style)
        ws.write(row_num_student, col_num, row.post_test_modality_arabic , font_style)
        ws.write(row_num_student, col_num, row.post_test_arabic , font_style)
        ws.write(row_num_student, col_num, row.post_test_attended_english , font_style)
        ws.write(row_num_student, col_num, row.post_test_modality_english , font_style)
        ws.write(row_num_student, col_num, row.post_test_english , font_style)
        ws.write(row_num_student, col_num, row.post_test_attended_psychomotor , font_style)
        ws.write(row_num_student, col_num, row.post_test_modality_psychomotor , font_style)
        ws.write(row_num_student, col_num, row.post_test_psychomotor , font_style)
        ws.write(row_num_student, col_num, row.post_test_attended_artistic , font_style)
        ws.write(row_num_student, col_num, row.post_test_modality_artistic , font_style)
        ws.write(row_num_student, col_num, row.post_test_artistic , font_style)
        ws.write(row_num_student, col_num, row.post_test_attended_math , font_style)
        ws.write(row_num_student, col_num, row.post_test_modality_math , font_style)
        ws.write(row_num_student, col_num, row.post_test_math , font_style)
        ws.write(row_num_student, col_num, row.post_test_attended_social , font_style)
        ws.write(row_num_student, col_num, row.post_test_modality_social , font_style)
        ws.write(row_num_student, col_num, row.post_test_social_emotional , font_style)
        ws.write(row_num_student, col_num, row.remote_learning , font_style)
        ws.write(row_num_student, col_num, row.remote_learning_reasons_not_engaged , font_style)
        ws.write(row_num_student, col_num, row.reasons_not_engaged_other , font_style)
        ws.write(row_num_student, col_num, row.reliable_internet , font_style)
        ws.write(row_num_student, col_num, row.gender_participate , font_style)
        ws.write(row_num_student, col_num, row.gender_participate_explain , font_style)
        ws.write(row_num_student, col_num, row.remote_learning_engagement , font_style)
        ws.write(row_num_student, col_num, row.meet_learning_outcomes , font_style)
        ws.write(row_num_student, col_num, row.parent_learning_support_rate , font_style)
        ws.write(row_num_student, col_num, row.covid_message , font_style)
        ws.write(row_num_student, col_num, row.covid_message_how_often , font_style)
        ws.write(row_num_student, col_num, row.covid_parents_message , font_style)
        ws.write(row_num_student, col_num, row.covid_parents_message_how_often , font_style)
        ws.write(row_num_student, col_num, row.follow_up_done , font_style)
        ws.write(row_num_student, col_num, row.follow_up_done_with_who , font_style)
        ws.write(row_num_student, col_num, row.unsuccessful_pretest_reason , font_style)
        ws.write(row_num_student, col_num, row.unsuccessful_posttest_reason , font_style)
        ws.write(row_num_student, col_num, row.student_outreached , font_style)
        ws.write(row_num_student, col_num, row.owner__username , font_style)
        ws.write(row_num_student, col_num, row.modified_by__username , font_style)
        ws.write(row_num_student, col_num, row.created , font_style)
        ws.write(row_num_student, col_num, row.modified , font_style)



    # ids = rows.values_list('id')

    # FC
    wsFC = wbStudent.add_sheet('FC')
    row_num_fc = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True

    columns_fc = [
        'enrollment id',
        'Student first name',
        'Student father name',
        'Student last name',
        'fc type',
        'facilitator name',
        'subject taught',
        'date of monitoring',
        'targeted competencies',
        'activities reported',
        'activities reported other',
        'share expectations',
        'share expectations no reason',
        'share expectations other reason',
        'materials needed available',
        'attend lesson',
        'child interact teacher',
        'child interact friends',
        'child clear responses',
        'child ask questions',
        'child acquire competency',
        'child show improvement',
        'child expected work independently',
        'work independently evaluation',
        'complete printed package',
        'sessions participated',
        'not participating reason',
        'E recharge card provided',
        'action to taken',
        'action to taken specify',
        'child needs pss',
        'child cant access resources',
        'homework after lesson',
        'parents supporting student',
        'completed tasks',
        'meet objectives',
        'meet objectives verified',
        'objectives verified specify',
        'additional notes'
    ]

    for col_num in range(len(columns_fc)):
        wsFC.write(row_num_fc, col_num, columns_fc[col_num], font_style)
    font_style = xlwt.XFStyle()


    # rows_fc = BLN_FC.objects.filter(enrollment__in=ids).values_list(

    rows_fc = queryset_fc

    # .values_list(
    #     'enrollment_id',
    #     'enrollment__student__first_name',
    #     'enrollment__student__father_name',
    #     'enrollment__student__last_name',
    #     'fc_type',
    #     'facilitator_name',
    #     'subject_taught',
    #     'date_of_monitoring',
    #     'targeted_competencies',
    #     'activities_reported',
    #     'activities_reported_other',
    #     'share_expectations',
    #     'share_expectations_no_reason',
    #     'share_expectations_other_reason',
    #     'materials_needed_available',
    #     'attend_lesson',
    #     'child_interact_teacher',
    #     'child_interact_friends',
    #     'child_clear_responses',
    #     'child_ask_questions',
    #     'child_acquire_competency',
    #     'child_show_improvement',
    #     'child_expected_work_independently',
    #     'work_independently_evaluation',
    #     'complete_printed_package',
    #     'sessions_participated',
    #     'not_participating_reason',
    #     'e_recharge_card_provided',
    #     'action_to_taken',
    #     'action_to_taken_specify',
    #     'child_needs_pss',
    #     'child_cant_access_resources',
    #     'homework_after_lesson',
    #     'parents_supporting_student',
    #     'completed_tasks',
    #     'meet_objectives',
    #     'meet_objectives_verified',
    #     'objectives_verified_specify',
    #     'additional_notes'
    # )

    for row in rows_fc:
        row_num_fc += 1
        wsFC.write(row_num_fc, col_num, row.enrollment_id , font_style)
        # wsFC.write(row_num_fc, col_num, row.enrollment__student__first_name , font_style)
        # wsFC.write(row_num_fc, col_num, row.enrollment__student__father_name , font_style)
        # wsFC.write(row_num_fc, col_num, row.enrollment__student__last_name , font_style)
        wsFC.write(row_num_fc, col_num, row.fc_type , font_style)
        wsFC.write(row_num_fc, col_num, row.facilitator_name , font_style)
        wsFC.write(row_num_fc, col_num, row.subject_taught , font_style)
        wsFC.write(row_num_fc, col_num, row.date_of_monitoring , font_style)
        wsFC.write(row_num_fc, col_num, row.targeted_competencies , font_style)
        wsFC.write(row_num_fc, col_num, row.activities_reported , font_style)
        wsFC.write(row_num_fc, col_num, row.activities_reported_other , font_style)
        wsFC.write(row_num_fc, col_num, row.share_expectations , font_style)
        wsFC.write(row_num_fc, col_num, row.share_expectations_no_reason , font_style)
        wsFC.write(row_num_fc, col_num, row.share_expectations_other_reason , font_style)
        wsFC.write(row_num_fc, col_num, row.materials_needed_available , font_style)
        wsFC.write(row_num_fc, col_num, row.attend_lesson , font_style)
        wsFC.write(row_num_fc, col_num, row.child_interact_teacher , font_style)
        wsFC.write(row_num_fc, col_num, row.child_interact_friends , font_style)
        wsFC.write(row_num_fc, col_num, row.child_clear_responses , font_style)
        wsFC.write(row_num_fc, col_num, row.child_ask_questions , font_style)
        wsFC.write(row_num_fc, col_num, row.child_acquire_competency , font_style)
        wsFC.write(row_num_fc, col_num, row.child_show_improvement , font_style)
        wsFC.write(row_num_fc, col_num, row.child_expected_work_independently , font_style)
        wsFC.write(row_num_fc, col_num, row.work_independently_evaluation , font_style)
        wsFC.write(row_num_fc, col_num, row.complete_printed_package , font_style)
        wsFC.write(row_num_fc, col_num, row.sessions_participated , font_style)
        wsFC.write(row_num_fc, col_num, row.not_participating_reason , font_style)
        wsFC.write(row_num_fc, col_num, row.e_recharge_card_provided , font_style)
        wsFC.write(row_num_fc, col_num, row.action_to_taken , font_style)
        wsFC.write(row_num_fc, col_num, row.action_to_taken_specify , font_style)
        wsFC.write(row_num_fc, col_num, row.child_needs_pss , font_style)
        wsFC.write(row_num_fc, col_num, row.child_cant_access_resources , font_style)
        wsFC.write(row_num_fc, col_num, row.homework_after_lesson , font_style)
        wsFC.write(row_num_fc, col_num, row.parents_supporting_student , font_style)
        wsFC.write(row_num_fc, col_num, row.completed_tasks , font_style)
        wsFC.write(row_num_fc, col_num, row.meet_objectives , font_style)
        wsFC.write(row_num_fc, col_num, row.meet_objectives_verified , font_style)
        wsFC.write(row_num_fc, col_num, row.objectives_verified_specify , font_style)
        wsFC.write(row_num_fc, col_num, row.additional_notes , font_style)

    wbStudent.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    response = FileResponse(buffer, content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename="BLN.xls"'

    return response


class MemorySavingQuerysetIterator(object):

    def __init__(self,queryset,max_obj_num=1000):
        self._base_queryset = queryset
        self._generator = self._setup()
        self.max_obj_num = max_obj_num

    def _setup(self):
        for i in xrange(0,self._base_queryset.count(),self.max_obj_num):
            # By making a copy of of the queryset and using that to actually access
            # the objects we ensure that there are only `max_obj_num` objects in
            # memory at any given time
            smaller_queryset = copy.deepcopy(self._base_queryset)[i:i+self.max_obj_num]
            #logger.debug('Grabbing next %s objects from DB' % self.max_obj_num)
            for obj in smaller_queryset.iterator():
                yield obj

    def __iter__(self):
        return self

    def next(self):
        return self._generator.next()


