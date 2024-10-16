
var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(window).load(function () {

    /* Background loading full-size images */
    $('.image-link').each(function() {
        var src = $(this).attr('href');
        var img = document.createElement('img');

        img.src = src;
        $('#image-cache').append(img);
    });

});

$(document).ready(function(){

    if($(document).find('#id_dropout_date').length == 1) {
        $('#id_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    learning_result_next_level();

    reorganizeForm_post_assessment();

    $(document).on('change', 'select#id_participation,  select#id_community_Liaison_follow_up, select#id_attended_arabic, select#id_attended_english,  select#id_attended_math,  ' +
        'select#id_attended_social,  select#id_attended_psychomotor ,  select#id_attended_science ,  select#id_attended_artistic , select#id_parent_attended ,' +
        'select#id_pss_parent_attended,  select#id_covid_parent_attended ,  select#id_followup_parent_attended ,' +
        'select#id_attended_biology,  select#id_attended_chemistry ,  select#id_attended_physics ,' +
        'select#id_barriers_single,  select#id_test_done ,  select#id_pss_session_attended , select#id_learning_result , ' +
        'select#id_covid_session_attended,  select#id_followup_session_attended  ' +
        'select#id_referal_other', function(){
       reorganizeForm_post_assessment();
    });

     $(document).on('change', 'select#id_referal_other', function(){
       reorganizeForm_post_assessment();
     });
     $(document).on('change', 'select#id_parent_attended_visits', function(){
       reorganizeForm_post_assessment();
    });


    $(document).on('click', '.delete-button', function(){
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            var callback = function(){
                item.parents('tr').remove();
            };
            delete_student(item, callback());
        }
    });

    $(document).on('click', '.cancel-button', function(e){
        e.preventDefault();
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            window_location(item.attr('href'));
        }
    });


});



function learning_result_next_level() {
    var registration_level = $('select#id_registration_level').val();
    var clm_type = $('#id_clmtype').val();
    if(clm_type=='ABLN' && registration_level=='level_two')
    {
        $("#id_learning_result option[value=" + 'graduated_to_abln_next_round_higher_level' + "]").hide();
    }
    else if(clm_type=='BLN' && registration_level=='level_three')
    {
        $("#id_learning_result option[value=" + 'graduated_to_bln_next_round_higher_level' + "]").hide();
    }
    else if(clm_type=='CBECE' && registration_level=='level_three')
    {
        $("#id_learning_result option[value=" + 'graduated_to_cbece_next_round_higher_level' + "]").hide();
    }
    else if(clm_type=='RS' && registration_level=='level_three')
    {
        $("#id_learning_result option[value=" + 'graduated_to_rs_next_round_higher_level' + "]").hide();
    }
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

    if(test_done == 'yes'){
    $('#div_id_round_complete').removeClass('d-none');
    $('#span_round_complete').removeClass('d-none');
    $('#grades').removeClass('hide');
    $('div.grades').removeClass('d-none');

    //    id_language
    if (language == 'english_arabic')
    {
        $('#div_id_english_alphabet_knowledge').removeClass('d-none');
        $('#div_id_english_familiar_words').removeClass('d-none');
        $('#div_id_english_reading_comprehension').removeClass('d-none');
        $('#span_english').removeClass('d-none');
    }
    else
    {
        $('#div_id_english_alphabet_knowledge').addClass('d-none');
        $('#div_id_english_familiar_words').addClass('d-none');
        $('#div_id_english_reading_comprehension').addClass('d-none');
        $('#span_english').addClass('d-none');
    }
    if (language == 'french_arabic')
    {
        $('#div_id_french_alphabet_knowledge').removeClass('d-none');
        $('#div_id_french_familiar_words').removeClass('d-none');
        $('#div_id_french_reading_comprehension').removeClass('d-none');
        $('#span_french').removeClass('d-none');
    }
    else
    {
        $('#div_id_french_alphabet_knowledge').addClass('d-none');
        $('#div_id_french_familiar_words').addClass('d-none');
        $('#div_id_french_reading_comprehension').addClass('d-none');
        $('#span_french').addClass('d-none');
    }
    }
    else
    {
        $('select#id_round_complete').val("");

        // grades

        $('#id_arabic_alphabet_knowledge').val('');
        $('#id_arabic_familiar_words').val('');
        $('#id_arabic_reading_comprehension').val('');
        $('#id_english_alphabet_knowledge').val('');
        $('#id_english_familiar_words').val('');
        $('#id_english_reading_comprehension').val('');
        $('#id_french_alphabet_knowledge').val('');
        $('#id_french_familiar_words').val('');
        $('#id_french_reading_comprehension').val('');
        $('#id_math').val('');

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

    // pss_parent_attended
    $('#div_id_pss_parent_attended_other').addClass('d-none');
    $('#span_pss_parent_attended_other').addClass('d-none');
    if(pss_parent_attended == 'other'){
        $('#div_id_pss_parent_attended_other').removeClass('d-none');
        $('#span_pss_parent_attended_other').removeClass('d-none');
    }
    else
    {
        $('#id_pss_parent_attended_other').val('');
    }

    // pss_session_modality
    $('div#div_id_pss_session_number').addClass('d-none');
    $('#span_pss_session_number').addClass('d-none');
    $('div#div_id_pss_session_modality').addClass('d-none');
    $('#span_pss_session_modality').addClass('d-none');
    $('div#div_id_pss_parent_attended').addClass('d-none');
    $('#span_pss_parent_attended').addClass('d-none');


    if(pss_session_attended == 'yes'){
        $('div#div_id_pss_session_number').removeClass('d-none');
        $('#span_pss_session_number').removeClass('d-none');
        $('div#div_id_pss_session_modality').removeClass('d-none');
        $('#span_pss_session_modality').removeClass('d-none');
        $('div#div_id_pss_parent_attended').removeClass('d-none');
        $('#span_pss_parent_attended').removeClass('d-none');
    }
    else{
        $('#id_pss_session_number').val('');
        $('select#div_id_pss_session_modality').val("");
        $('#span_pss_parent_attended_other').val('');
        $('select#div_id_pss_parent_attended').val("");

    }

 // covid_parent_attended
    $('#div_id_covid_parent_attended_other').addClass('d-none');
    $('#span_covid_parent_attended_other').addClass('d-none');
    if(covid_parent_attended == 'other'){
        $('#div_id_covid_parent_attended_other').removeClass('d-none');
        $('#span_covid_parent_attended_other').removeClass('d-none');
    }
    else
    {
        $('#id_covid_parent_attended_other').val('');
    }

    // covid_session_modality
    $('div#div_id_covid_session_number').addClass('d-none');
    $('#span_covid_session_number').addClass('d-none');
    $('div#div_id_covid_session_modality').addClass('d-none');
    $('#span_covid_session_modality').addClass('d-none');
    $('div#div_id_covid_parent_attended').addClass('d-none');
    $('#span_covid_parent_attended').addClass('d-none');


    if(covid_session_attended == 'yes'){
        $('div#div_id_covid_session_number').removeClass('d-none');
        $('#span_covid_session_number').removeClass('d-none');
        $('div#div_id_covid_session_modality').removeClass('d-none');
        $('#span_covid_session_modality').removeClass('d-none');
        $('div#div_id_covid_parent_attended').removeClass('d-none');
        $('#span_covid_parent_attended').removeClass('d-none');
    }
    else{
        $('#id_covid_session_number').val('');
        $('select#div_id_covid_session_modality').val("");
        $('#span_covid_parent_attended_other').val('');
        $('select#div_id_covid_parent_attended').val("");
    }

     // followup_parent_attended
    $('#div_id_followup_parent_attended_other').addClass('d-none');
    $('#span_followup_parent_attended_other').addClass('d-none');
    if(followup_parent_attended == 'other'){
        $('#div_id_followup_parent_attended_other').removeClass('d-none');
        $('#span_followup_parent_attended_other').removeClass('d-none');
    }
    else
    {
        $('#id_followup_parent_attended_other').val('');
    }

    // followup_session_modality
    $('div#div_id_followup_session_number').addClass('d-none');
    $('#span_followup_session_number').addClass('d-none');
    $('div#div_id_followup_session_modality').addClass('d-none');
    $('#span_followup_session_modality').addClass('d-none');
    $('div#div_id_followup_parent_attended').addClass('d-none');
    $('#span_followup_parent_attended').addClass('d-none');

    if(followup_session_attended == 'yes'){
        $('div#div_id_followup_session_number').removeClass('d-none');
        $('#span_followup_session_number').removeClass('d-none');
        $('div#div_id_followup_session_modality').removeClass('d-none');
        $('#span_followup_session_modality').removeClass('d-none');
        $('div#div_id_followup_parent_attended').removeClass('d-none');
        $('#span_followup_parent_attended').removeClass('d-none');
    }
    else{
        $('#id_followup_session_number').val('');
        $('select#div_id_followup_session_modality').val("");
        $('#span_followup_parent_attended_other').val('');
        $('select#div_id_followup_parent_attended').val("");
    }

    $('div.parent_visits').addClass('d-none');
    $('#parent_visits').addClass('hide');

    if(parent_attended_visits == 'yes'){
    $('#parent_visits').removeClass('hide');
    $('div.parent_visits').removeClass('d-none');

    }
    else
    {
        $('#id_followup_session_number').val('');
        $('select#div_id_followup_session_modality').val("");
        $('#span_followup_parent_attended_other').val('');
        $('select#div_id_followup_parent_attended').val("");
        $('#id_covid_session_number').val('');
        $('select#div_id_covid_session_modality').val("");
        $('#span_covid_parent_attended_other').val('');
        $('select#div_id_covid_parent_attended').val("");
        $('#id_pss_session_number').val('');
        $('select#div_id_pss_session_modality').val("");
        $('#span_pss_parent_attended_other').val('');
        $('select#div_id_pss_parent_attended').val("");
        $('div.parent_visits').addClass('d-none');
        $('#parent_visits').addClass('hide');
    }
    $('div#div_id_referal_other_specify').addClass('d-none');
    $('#span_referal_other_specify').addClass('d-none');

      if(referal_other == 'yes'){
        $('#div_id_referal_other_specify').removeClass('d-none');
        $('#span_referal_other_specify').removeClass('d-none');
     }
     else
        {
            $('#id_referal_other_specify').val('');
        }



}
