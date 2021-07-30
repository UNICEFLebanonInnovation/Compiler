import io
import xlwt
import csv
from datetime import date
from django.http import HttpResponse, FileResponse

from .models import ABLN_FC, BLN_FC, CBECE_FC, RS_FC


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



def build_xls_extraction(queryset, request, filename, report_type='all_data'):
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
        'referal_health'
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

    qs = queryset.extra(select={

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

    rows = qs.order_by('id').values_list(
        'id',
        'new_registry',
        'partner__name',
        'round__name',
        'governorate__name_en',
        'district__name_en',
        'cadaster__name_en',
        'location',
        'center__name',
        'language',
        'student__address',
        'registration_level',
        'first_attendance_date',
        'student__id_number'
        'student__number',
        'student__first_name',
        'student__father_name',
        'student__last_name',
        'student__mother_fullname',
        'student__sex',
        'student__nationality__name',
        'other_nationality',
        'student__birthday_day',
        'student__birthday_month',
        'student__birthday_year',
        'student__p_code'
        'disability__name_en',
        'education_status',
        'miss_school_date',
        'internal_number',
        'rims_case_number',
        'source_of_identification',
        'source_of_identification_specify',
        'source_of_transportation',
        'hh_educational_level__name',
        'father_educational_level__name',
        'phone_number',
        'phone_number_confirm',
        'phone_owner',
        'second_phone_number',
        'second_phone_number_confirm',
        'second_phone_owner',
        'main_caregiver',
        'main_caregiver_nationality__name',
        'other_caregiver_relationship',
        'main_caregiver_nationality_other',
        'caretaker_first_name',
        'caretaker_middle_name',
        'caretaker_last_name',
        'caretaker_mother_name',
        'id_type',
        'case_number',
        'case_number_confirm',
        'parent_individual_case_number',
        'parent_individual_case_number_confirm',
        'individual_case_number',
        'individual_case_number_confirm',
        'recorded_number',
        'recorded_number_confirm',
        'parent_national_number',
        'parent_national_number_confirm',
        'national_number',
        'national_number_confirm',
        'parent_syrian_national_number',
        'parent_syrian_national_number_confirm',
        'syrian_national_number',
        'syrian_national_number_confirm',
        'parent_sop_national_number',
        'parent_sop_national_number_confirm',
        'sop_national_number',
        'sop_national_number_confirm',
        'parent_other_number',
        'parent_other_number_confirm',
        'other_number',
        'other_number_confirm',
        'student__family_status',
        'student__have_children',
        'student_number_children',
        'have_labour_single_selection',
        'labours_single_selection',
        'labours_other_specify',
        'labour_hours',
        'labour_weekly_income',
        'participation',
        'barriers_single',
        'barriers_other',
        'test_done',
        'round_complete',
        'basic_stationery',
        'pss_kit',
        'learning_result',
        'learning_result_other'
        'cp_referral',
        'referal_wash',
        'referal_health'
        'referal_other',
        'referal_other_specify',
        'child_received_books',
        'child_received_printout',
        'child_received_internet',
        'phone_call_number',
        'phone_call_follow_up_result',
        'house_visit_number',
        'house_visit_follow_up_result',
        'family_visit_number',
        'family_visit_follow_up_result',
        'parent_attended_visits',
        'pss_session_attended',
        'pss_session_number',
        'pss_session_modality',
        'pss_parent_attended',
        'pss_parent_attended_other',
        'covid_session_attended',
        'covid_session_number',
        'covid_session_modality',
        'covid_parent_attended',
        'covid_parent_attended_other',
        'followup_session_attended',
        'followup_session_number',
        'followup_session_modality',
        'followup_parent_attended',
        'followup_parent_attended_other',
        'pre_test_attended_arabic',
        'pre_test_modality_arabic',
        'pre_test_arabic',
        'pre_test_attended_english',
        'pre_test_modality_english',
        'pre_test_english',
        'pre_test_attended_psychomotor',
        'pre_test_modality_psychomotor',
        'pre_test_psychomotor',
        'pre_test_attended_artistic',
        'pre_test_modality_artistic',
        'pre_test_artistic',
        'pre_test_attended_math',
        'pre_test_modality_math',
        'pre_test_math',
        'pre_test_attended_social',
        'pre_test_modality_social',
        'pre_test_social_emotional',
        'post_test_attended_arabic',
        'post_test_modality_arabic',
        'post_test_arabic',
        'post_test_attended_english',
        'post_test_modality_english',
        'post_test_english',
        'post_test_attended_psychomotor',
        'post_test_modality_psychomotor',
        'post_test_psychomotor',
        'post_test_attended_artistic',
        'post_test_modality_artistic',
        'post_test_artistic',
        'post_test_attended_math',
        'post_test_modality_math',
        'post_test_math',
        'post_test_attended_social',
        'post_test_modality_social',
        'post_test_social_emotional',
        'remote_learning',
        'remote_learning_reasons_not_engaged',
        'reasons_not_engaged_other',
        'reliable_internet',
        'gender_participate',
        'gender_participate_explain',
        'remote_learning_engagement',
        'meet_learning_outcomes',
        'parent_learning_support_rate',
        'covid_message',
        'covid_message_how_often',
        'covid_parents_message',
        'covid_parents_message_how_often',
        'follow_up_done',
        'follow_up_done_with_who',
        'unsuccessful_pretest_reason',
        'unsuccessful_posttest_reason',
        'student_outreached',
        'owner__username',
        'modified_by__username',
        'created',
        'modified',
    )
    for row in rows:
        row_num_student += 1
        for col_num in range(len(row)):
            ws.write(row_num_student, col_num, row[col_num], font_style)

    ids = rows.values_list('id')

    # FC
    wsFC = wbStudent.add_sheet('FC')
    row_num_fc = 0

    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    columns_fc = [
        'enrollment id',
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
        'e recharge card provided',
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

    rows_fc = BLN_FC.objects.filter(enrollment__in=ids).order_by('enrollment').values_list(
        'enrollment_id',
        'fc_type',
        'facilitator_name',
        'subject_taught',
        'date_of_monitoring',
        'targeted_competencies',
        'activities_reported',
        'activities_reported_other',
        'share_expectations',
        'share_expectations_no_reason',
        'share_expectations_other_reason',
        'materials_needed_available',
        'attend_lesson',
        'child_interact_teacher',
        'child_interact_friends',
        'child_clear_responses',
        'child_ask_questions',
        'child_acquire_competency',
        'child_show_improvement',
        'child_expected_work_independently',
        'work_independently_evaluation',
        'complete_printed_package',
        'sessions_participated',
        'not_participating_reason',
        'e_recharge_card_provided',
        'action_to_taken',
        'action_to_taken_specify',
        'child_needs_pss',
        'child_cant_access_resources',
        'homework_after_lesson',
        'parents_supporting_student',
        'completed_tasks',
        'meet_objectives',
        'meet_objectives_verified',
        'objectives_verified_specify',
        'additional_notes'
    )

    for row in rows_fc:
        row_num_fc += 1
        for col_num in range(len(row)):
            wsFC.write(row_num_fc, col_num, row[col_num], font_style)

    wbStudent.save(buffer)

    # FileResponse sets the Content-Disposition header so that browsers
    # present the option to save the file.
    buffer.seek(0)
    # print('----------------------------------------------------------------------------------------------------------------------------------------')
    # print(qs.query)
    # print('----------------------------------------------------------------------------------------------------------------------------------------')

    print(rows_fc.query)
    print('----------------------------------------------------------------------------------------------------------------------------------------')
    #


    return FileResponse(buffer, as_attachment=True, filename="{}.xls".format(filename))

