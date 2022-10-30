
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

    reorganizeForm_post_assessment();

    if($(document).find('#id_adolescent_dropout_date').length == 1) {
        $('#id_adolescent_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_participation,  select#id_community_Liaison_follow_up, select#id_attended_arabic, select#id_attended_foreign_language,  select#id_attended_math,  ' +
        'select#id_attended_social,  select#id_attended_psychomotor ,  select#id_attended_science ,  select#id_attended_artistic , select#id_parent_attended ,' +
        'select#id_pss_parent_attended,  select#id_covid_parent_attended ,  select#id_followup_parent_attended ,' +
        'select#id_attended_biology,  select#id_attended_chemistry ,  select#id_attended_physics ,' +
        'select#id_participate_volunteering,  select#id_yfs_course_completed ,  select#id_participate_community_initiatives ,' +
        'select#id_adolescent_attendance ,' +
        'select#id_barriers_single,  select#id_test_done , select#id_test_diagnostic_done,  select#id_pss_session_attended , select#id_learning_result , ' +
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
//            window.location = item.attr('href');
        }
    });

    pageScripts();

        /* Ajax page load settings */
        $(document).on('pjax:end', pageScripts);
        if (sessionStorage.getItem("pjax-enabled") === "0") {
            return;
        }

        // Comment it to disable Ajax Page load
        $(document).pjax('a', '.content-wrap', {fragment: '.content-wrap'});

        $(document).on('pjax:beforeReplace', function() {
            $('.content-wrap').css('opacity', '0.1');
            setTimeout(function() {
                $('.content-wrap').fadeTo('100', '1');
            }, 1);
        });
});

function pageScripts() {
    /* Magnific Popup */
    $('.image-link').magnificPopup({
        type: 'image',
        gallery: {
            enabled: true
        }
    });
}

function reorganizeForm_post_assessment()
{

    var participation = $('select#id_participation').val();
    var barriers_single = $('select#id_barriers_single').val();
    var test_done = $('select#id_test_done').val();
    var test_diagnostic_done = $('select#id_test_diagnostic_done').val();
    var community_Liaison_follow_up = $('select#id_community_Liaison_follow_up').val();
//    var follow_up_type = $('select#id_follow_up_type').val();
    var attended_arabic = $('select#id_attended_arabic').val();
    var attended_foreign_language = $('select#id_attended_foreign_language').val();
    var attended_math = $('select#id_attended_math').val();


    var pss_session_attended = $('select#id_pss_session_attended').val();
    var covid_session_attended = $('select#id_covid_session_attended').val();
    var followup_session_attended = $('select#id_followup_session_attended').val();

    var pss_parent_attended =  $('select#id_pss_parent_attended').val();
    var covid_parent_attended =  $('select#id_covid_parent_attended').val();
    var followup_parent_attended =  $('select#id_followup_parent_attended').val();

    var parent_attended_visits = $('select#id_parent_attended_visits').val();
    var grade_registration = $('select#id_grade_registration').val();

    var learning_result = $('select#id_learning_result').val();
    var referal_other = $('select#id_referal_other').val();

    // id_participation
    $('div#div_id_barriers_single').addClass('d-none');
    $('#span_barriers_single').addClass('d-none');
    $('div#div_id_barriers_other').addClass('d-none');
    $('#span_barriers_other').addClass('d-none');
    $('#community_Liaison').removeClass('hide');
    $('div.community_Liaison').removeClass('d-none');

    if(participation != 'no_absence'){
        $('#div_id_barriers_single').removeClass('d-none');
        $('#span_barriers_single').removeClass('d-none');
    }
    else{
        $('div.community_Liaison').addClass('d-none');
        $('#community_Liaison').addClass('hide');
    }

    $('#span_community_liaison_specify').addClass('d-none');
    $('div#div_id_community_liaison_specify').addClass('d-none');
    if(community_Liaison_follow_up == 'yes'){
        $('#div_id_community_liaison_specify').removeClass('d-none');
        $('#span_community_liaison_specify').removeClass('d-none');
    }

    // learning_result
    $('div#div_id_learning_result_other').addClass('d-none');
    $('#span_learning_result_other').addClass('d-none');
    if(learning_result == 'other'){
        $('#div_id_learning_result_other').removeClass('d-none');
        $('#span_learning_result_other').removeClass('d-none');
    }

    $('div#div_id_round_complete').addClass('d-none');
    $('#span_round_complete').addClass('d-none');
    $('div.grades').addClass('d-none');
    $('#grades').addClass('hide');

    if(test_done == 'yes'){
    $('#div_id_round_complete').removeClass('d-none');
    $('#span_round_complete').removeClass('d-none');
    $('#grades').removeClass('hide');
    $('div.grades').removeClass('d-none');
    }
    else
    {
        $('select#id_round_complete').val("");
//        $('#id_arabic').val('');
//        $('select#id_attended_arabic').val("no");
//        $('select#id_modality_arabic').val("");
//        $('#id_foreign_language').val('');
//        $('select#id_attended_foreign_language').val("no");
//        $('select#id_modality_foreign_language').val("");
//        $('#id_math').val('');
//        $('select#id_attended_math').val("no");
//        $('select#id_modality_math').val("");

        $('div.grades').addClass('d-none');
        $('#grades').addClass('hide');
    }

    $('div#div_id_arabic').addClass('d-none');
    $('#span_arabic').addClass('d-none');
    $('div#div_id_modality_arabic').addClass('d-none');
    $('#span_modality_arabic').addClass('d-none');

    $('div#div_id_foreign_language').addClass('d-none');
    $('#span_foreign_language').addClass('d-none');
    $('div#div_id_modality_foreign_language').addClass('d-none');
    $('#span_modality_foreign_language').addClass('d-none');

    $('div#div_id_math').addClass('d-none');
    $('#span_math').addClass('d-none');
    $('div#div_id_modality_math').addClass('d-none');
    $('#span_modality_math').addClass('d-none');



    // attended_arabic
    if(attended_arabic == 'yes'){
        $('div#div_id_arabic').removeClass('d-none');
        $('#span_arabic').removeClass('d-none');
        $('div#div_id_modality_arabic').removeClass('d-none');
        $('#span_modality_arabic').removeClass('d-none');

    }
    else{
        $('#id_arabic').val('');
        $('select#id_modality_arabic').val("");

    }

    // attended_english
    if(attended_foreign_language == 'yes'){
        $('div#div_id_foreign_language').removeClass('d-none');
        $('#span_foreign_language').removeClass('d-none');
        $('div#div_id_modality_foreign_language').removeClass('d-none');
        $('#span_modality_foreign_language').removeClass('d-none');

    }
    else{
        $('#id_foreign_language').val('');
        $('select#id_modality_foreign_language').val("");
    }
    // attended_math
    if(attended_math == 'yes'){
        $('div#div_id_math').removeClass('d-none');
        $('#span_math').removeClass('d-none');
        $('div#div_id_modality_math').removeClass('d-none');
        $('#span_modality_math').removeClass('d-none');
    }
    else{
        $('#id_math').val('');
        $('select#id_modality_math').val("");
    }

    if(test_diagnostic_done == 'yes'){
    $('#div_id_receive_passing_grade').removeClass('d-none');
    $('#span_receive_passing_grade').removeClass('d-none');
    }
    else
    {
        $('select#id_receive_passing_grade').val("");
        $('#div_id_receive_passing_grade').addClass('d-none');
        $('#span_receive_passing_grade').addClass('d-none');
    }


    var participate_volunteering = $('select#id_participate_volunteering').val();
    var yfs_course_completed = $('select#id_yfs_course_completed').val();
    if(participate_volunteering == 'yes'){
        $('#div_id_volunteering_specify').removeClass('d-none');
        $('#span_volunteering_specify').removeClass('d-none');
    }
    else
    {
        $('select#id_volunteering_specify').val("");
        $('#div_id_volunteering_specify').addClass('d-none');
        $('#span_volunteering_specify').addClass('d-none');
    }

    var yfs_course_completed = $('select#id_yfs_course_completed').val();
    if(yfs_course_completed == 'yes'){
        $('#div_id_training_material').removeClass('d-none');
        $('#span_training_material').removeClass('d-none');
    }
    else
    {
        $('select#id_training_material').val("");
        $('#div_id_training_material').addClass('d-none');
        $('#span_training_material').addClass('d-none');
    }




    var participate_community_initiatives = $('select#id_participate_community_initiatives').val();

    if(participate_community_initiatives == 'yes'){
        $('#div_id_community_initiatives_specify').removeClass('d-none');
        $('#span_community_initiatives_specify').removeClass('d-none');
    }
    else
    {
        $('select#id_community_initiatives_specify').val("");
        $('#div_id_community_initiatives_specify').addClass('d-none');
        $('#span_community_initiatives_specify').addClass('d-none');
    }



    var adolescent_attendance = $('select#id_adolescent_attendance').val();
    var adolescent_dropout_reason = $('select#id_adolescent_dropout_reason').val();
    var adolescent_dropout_date = $('select#id_adolescent_dropout_date').val();

    if(adolescent_attendance == 'Dropout'){
    $('#div_id_adolescent_dropout_reason').removeClass('d-none');
    $('#span_adolescent_dropout_reason').removeClass('d-none');
    $('#div_id_adolescent_dropout_date').removeClass('d-none');
    $('#span_adolescent_dropout_daten').removeClass('d-none');
    }
    else
    {
        $('select#id_adolescent_dropout_reason').val("");
        $('#div_id_adolescent_dropout_reason').addClass('d-none');
        $('#span_adolescent_dropout_reason').addClass('d-none');
        $('select#id_adolescent_dropout_date').val("");
        $('#div_id_adolescent_dropout_date').addClass('d-none');
        $('#span_adolescent_dropout_date').addClass('d-none');
    }


  }

