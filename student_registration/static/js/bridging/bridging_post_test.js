$(document).ready(function () {
    $('.image-link').each(function () {
        $('<img>').attr('src', $(this).attr('href')).appendTo('#image-cache');
    });

    if ($('#id_dropout_date').length) {
        $('#id_dropout_date').datepicker({ dateFormat: "yy-mm-dd" });
    }

    learning_result_next_level();
    reorganizeForm_post_assessment();

    // Event listeners for form changes
    const selectors = [
        '#id_participation', '#id_community_Liaison_follow_up', '#id_attended_arabic',
        '#id_attended_english', '#id_attended_math', '#id_attended_social', '#id_attended_psychomotor',
        '#id_attended_science', '#id_attended_artistic', '#id_parent_attended', '#id_pss_parent_attended',
        '#id_covid_parent_attended', '#id_followup_parent_attended', '#id_attended_biology',
        '#id_attended_chemistry', '#id_attended_physics', '#id_barriers_single', '#id_test_done',
        '#id_pss_session_attended', '#id_learning_result', '#id_covid_session_attended',
        '#id_followup_session_attended', '#id_referal_other', '#id_parent_attended_visits'
    ].join(',');

    $(document).on('change', selectors, reorganizeForm_post_assessment);
    $(document).on('change', '#id_registration_level', reorganizeForm_post_assessment);

    $(document).on('click', '.delete-button', function () {
        if (confirm($(this).attr('translation'))) {
            const item = $(this);
            delete_student(item, () => item.closest('tr').remove());
        }
    });

    $(document).on('click', '.cancel-button', function (e) {
        e.preventDefault();
        if (confirm($(this).attr('translation'))) {
            window_location($(this).attr('href'));
        }
    });
});

function getRequiredGradeFieldsWithMax(registrationLevel, isPostAssessment) {
    const efByLevel = {
        level_one: {
            ef_letter_sound: 10, ef_familiar_words: 5, ef_picture_word_matching: 5,
            ef_reading_comprehension_text_1: 5, ef_reading_comprehension_text_2: 5,
            ef_letter_dictation: 5, ef_word_dictation: 5, ef_total_score: 40
        },
        level_two: {
            ef_letter_sound: 10, ef_familiar_words: 5, ef_picture_word_matching: 5,
            ef_reading_comprehension_text_1: 5, ef_reading_comprehension_text_2: 5,
            ef_sentence_dictation: 5, ef_picture_naming: 5, ef_total_score: 40
        },
        level_three: {
            ef_letter_sound: 10, ef_familiar_words: 5, ef_picture_word_matching: 5,
            ef_reading_comprehension_text_1: 5, ef_reading_comprehension_text_2: 5,
            ef_word_dictation: 5, ef_picture_description: 5, ef_total_score: 40
        }
    };

    const arByLevel = {
        level_one: {
            ar_letter_sound: 10, ar_alphabet_vowel_marks: 5, ar_alphabet_long_vowels: 5,
            ar_familiar_words: 5, ar_picture_word_matching: 5, ar_reading_comprehension_text_1: 5,
            ar_reading_comprehension_text_2: 5, ar_letter_dictation: 5, ar_word_dictation: 5,
            ar_total_score: 50
        },
        level_two: {
            ar_letter_sound: 10, ar_alphabet_vowel_marks: 5, ar_alphabet_long_vowels: 5,
            ar_familiar_words: 5, ar_picture_word_matching: 5, ar_reading_comprehension_text_1: 5,
            ar_reading_comprehension_text_2: 5, ar_word_dictation: 5, ar_picture_naming: 5,
            ar_total_score: 50
        },
        level_three: {
            ar_letter_sound: 10, ar_alphabet_vowel_marks: 5, ar_alphabet_long_vowels: 5,
            ar_familiar_words: 5, ar_picture_word_matching: 5, ar_reading_comprehension_text_1: 5,
            ar_reading_comprehension_text_2: 5, ar_sentence_dictation: 5, ar_picture_description: 5,
            ar_total_score: 50
        }
    };

    const preMathByLevel = {
        level_one: {m_natural_numbers: 10, m_addition: 5, m_location: 5, m_plane_figures: 5, m_total_score: 25},
        level_two: {m_natural_numbers: 10, m_addition: 10, m_location: 4, m_plane_figures: 3, m_subtraction: 8, m_total_score: 35},
        level_three: {m_natural_numbers: 12, m_addition: 12, m_plane_figures: 4, m_subtraction: 12, m_multiplication: 5, m_total_score: 45}
    };

    const postMathByLevel = {
        level_one: {m_natural_numbers: 10, m_addition: 6, m_subtraction: 5, m_length: 2, m_solid_figures: 2, m_plane_figures: 5, m_total_score: 25},
        level_two: {m_natural_numbers: 7, m_addition: 8, m_subtraction: 5, m_length: 3, m_solid_figures: 3, m_plane_figures: 4, m_multiplication: 5, m_total_score: 35},
        level_three: {m_natural_numbers: 9, m_addition: 6, m_length: 5, m_multiplication: 7, m_location: 3, m_division: 6, m_fractions: 3, m_total_score: 45}
    };

    const mathByLevel = isPostAssessment ? postMathByLevel : preMathByLevel;
    return Object.assign({}, efByLevel[registrationLevel] || {}, arByLevel[registrationLevel] || {}, mathByLevel[registrationLevel] || {});
}

function applyRegistrationLevelGradeVisibility() {
    const registrationLevel = $('select#id_registration_level').val();
    const hasPostTestToggle = $('#id_test_done').length > 0;

    const allGradeFields = [
        'ef_letter_sound', 'ef_familiar_words', 'ef_picture_word_matching', 'ef_reading_comprehension_text_1',
        'ef_reading_comprehension_text_2', 'ef_letter_dictation', 'ef_word_dictation', 'ef_sentence_dictation',
        'ef_picture_naming', 'ef_picture_description', 'ef_total_score', 'ar_letter_sound',
        'ar_alphabet_vowel_marks', 'ar_alphabet_long_vowels', 'ar_familiar_words', 'ar_picture_word_matching',
        'ar_reading_comprehension_text_1', 'ar_reading_comprehension_text_2', 'ar_letter_dictation',
        'ar_word_dictation', 'ar_sentence_dictation', 'ar_picture_naming', 'ar_picture_description',
        'ar_total_score', 'm_natural_numbers', 'm_addition', 'm_location', 'm_plane_figures',
        'm_subtraction', 'm_length', 'm_solid_figures', 'm_multiplication', 'm_division', 'm_fractions',
        'm_total_score'
    ];

    const requiredWithMax = getRequiredGradeFieldsWithMax(registrationLevel, hasPostTestToggle);
    allGradeFields.forEach(function (fieldName) {
        $('#div_id_' + fieldName).addClass('d-none');
        const label = $('label[for="id_' + fieldName + '"]');
        if (!label.data('baseText')) {
            label.data('baseText', label.text().replace(/\s*\/\s*\d+$/, '').replace(/\s*\/max by level$/, ''));
        }
    });

    Object.keys(requiredWithMax).forEach(function (fieldName) {
        $('#div_id_' + fieldName).removeClass('d-none');
        const label = $('label[for="id_' + fieldName + '"]');
        if (label.length) {
            const baseText = label.data('baseText') || label.text();
            label.text(baseText + '/' + requiredWithMax[fieldName]);
        }
    });
}

function reorganizeForm_post_assessment()
{
   var learning_result =  $('select#id_learning_result').val();

    $('#span_learning_result_other').addClass('d-none');
    $('#div_id_learning_result_other').addClass('d-none');
    if(learning_result == 'other'){
        $('#span_learning_result_other').removeClass('d-none');
        $('#div_id_learning_result_other').removeClass('d-none');
    }

    $('#div_id_dropout_reason').addClass('d-none');
    $('#span_dropout_reason').addClass('d-none');
    $('#div_id_dropout_date').addClass('d-none');
    $('#span_dropout_date').addClass('d-none');
    if(learning_result == 'dropout'){
        $('#div_id_dropout_reason').removeClass('d-none');
        $('#span_dropout_reason').removeClass('d-none');
        $('#div_id_dropout_date').removeClass('d-none');
        $('#span_dropout_date').removeClass('d-none');
    }

    $('div#div_id_referral_school').addClass('d-none');
    $('#span_referral_school').addClass('d-none');
    $('div#div_id_referral_school_type').addClass('d-none');
    $('#span_referral_school_type').addClass('d-none');
    if(learning_result == 'referred_public_school'){
        $('div#div_id_referral_school').removeClass('d-none');
        $('#span_referral_school').removeClass('d-none');
        $('div#div_id_referral_school_type').removeClass('d-none');
        $('#span_referral_school_type').removeClass('d-none');
    }

    var participation = $('select#id_participation').val();
    var barriers_single = $('select#id_barriers_single').val();
    var test_done = $('select#id_test_done').val();
    var language  = $('select#id_language').val();

    var community_Liaison_follow_up = $('select#id_community_Liaison_follow_up').val();

    var pss_session_attended = $('select#id_pss_session_attended').val();
    var covid_session_attended = $('select#id_covid_session_attended').val();
    var followup_session_attended = $('select#id_followup_session_attended').val();

    var pss_parent_attended =  $('select#id_pss_parent_attended').val();
    var covid_parent_attended =  $('select#id_covid_parent_attended').val();
    var followup_parent_attended =  $('select#id_followup_parent_attended').val();

    var parent_attended_visits = $('select#id_parent_attended_visits').val();
    var grade_registration = $('select#id_grade_registration').val();

    var referal_other = $('select#id_referal_other').val();

    // id_participation
    $('div#div_id_barriers_single').addClass('d-none');
    $('#span_barriers_single').addClass('d-none');
    $('div#div_id_barriers_other').addClass('d-none');
    $('#span_barriers_other').addClass('d-none');
    $('#div_id_community_Liaison_follow_up').removeClass('d-none');
    $('#span_community_Liaison_follow_up').removeClass('d-none');

    if(participation != 'no_absence'){
        $('#div_id_barriers_single').removeClass('d-none');
        $('#span_barriers_single').removeClass('d-none');
        if (barriers_single =='other'){
            $('div#div_id_barriers_other').removeClass('d-none');
            $('#span_barriers_other').removeClass('d-none');
        }
        $('#div_id_community_Liaison_follow_up').removeClass('d-none');
        $('#span_community_Liaison_follow_up').removeClass('d-none');
    }
    else{
        $('#div_id_barriers_single').addClass('d-none');
        $('#span_barriers_single').addClass('d-none');
        $('div#div_id_barriers_other').addClass('d-none');
        $('#span_barriers_other').addClass('d-none');
        $('#div_id_community_Liaison_follow_up').addClass('d-none');
        $('#span_community_Liaison_follow_up').addClass('d-none');
        $('#span_community_liaison_specify').addClass('d-none');
        $('div#div_id_community_liaison_specify').addClass('d-none');
    }

    $('#span_community_liaison_specify').addClass('d-none');
    $('div#div_id_community_liaison_specify').addClass('d-none');
    if(community_Liaison_follow_up == 'yes'){
        $('#div_id_community_liaison_specify').removeClass('d-none');
        $('#span_community_liaison_specify').removeClass('d-none');
    }
    else
    {
        $('#span_community_liaison_specify').addClass('d-none');
        $('div#div_id_community_liaison_specify').addClass('d-none');
    }

    $('div#div_id_round_complete').addClass('d-none');
    $('#span_round_complete').addClass('d-none');

    if(test_done == 'yes' || $('#id_test_done').length === 0){
    $('#div_id_round_complete').removeClass('d-none');
    $('#span_round_complete').removeClass('d-none');
    $('#grades').removeClass('hide');
    $('div.grades').removeClass('d-none');
    applyRegistrationLevelGradeVisibility();

    //    id_language
    if (language == 'english_arabic')
    {
        $('#span_english').removeClass('d-none');
    }
    else
    {
        $('#span_english').addClass('d-none');
    }
    if (language == 'french_arabic')
    {
        $('#span_french').removeClass('d-none');
    }
    else
    {
        $('#span_french').addClass('d-none');
    }
    }
    else
    {
        $('select#id_round_complete').val("");

        // grades


        [
            'ef_letter_sound', 'ef_familiar_words', 'ef_picture_word_matching', 'ef_reading_comprehension_text_1',
            'ef_reading_comprehension_text_2', 'ef_letter_dictation', 'ef_word_dictation', 'ef_sentence_dictation',
            'ef_picture_naming', 'ef_picture_description', 'ef_total_score', 'ar_letter_sound',
            'ar_alphabet_vowel_marks', 'ar_alphabet_long_vowels', 'ar_familiar_words', 'ar_picture_word_matching',
            'ar_reading_comprehension_text_1', 'ar_reading_comprehension_text_2', 'ar_letter_dictation',
            'ar_word_dictation', 'ar_sentence_dictation', 'ar_picture_naming', 'ar_picture_description',
            'ar_total_score', 'm_natural_numbers', 'm_addition', 'm_location', 'm_plane_figures',
            'm_subtraction', 'm_length', 'm_solid_figures', 'm_multiplication', 'm_division', 'm_fractions',
            'm_total_score'
        ].forEach(function (fieldName) {
            $('#id_' + fieldName).val('');
        });

        $('div.grades').addClass('d-none');
        $('#grades').addClass('hide');
    }

    learning_result_next_level();

    // grade_registration
    $('div.grd6').addClass('d-none');
    $('#grd6').addClass('hide');
    $('div.grd7').addClass('d-none');
    $('#grd7').addClass('hide');


     if (grade_registration == '7' || grade_registration == '8' || grade_registration == '9') {
        $('div.grd6').addClass('d-none');
        $('#grd6').addClass('hide');
        $('div.grd7').removeClass('d-none');
        $('#grd7').removeClass('hide');
        $('#id_science').val('');
        $('select#id_attended_science').val("no");
        $('select#id_modality_science').val("");
    }
    else {
        $('#grd6').removeClass('hide');
        $('div.grd6').removeClass('d-none');
        $('#grd7').addClass('hide');
        $('div.grd7').addClass('d-none');
        $('#id_biology').val('');
        $('select#id_attended_biology').val("no");
        $('select#id_modality_biology').val("");

        $('#id_chemistry').val('');
        $('select#id_attended_chemistry').val("no");
        $('select#id_modality_chemistry').val("");

        $('#id_physics').val('');
        $('select#id_attended_physics').val("no");
        $('select#id_modality_physics').val("");
    }
}
