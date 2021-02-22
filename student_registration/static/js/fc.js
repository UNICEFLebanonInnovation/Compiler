/**
 * Created by yosr on 11/26/20.
 */

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

    alert('hiiiiiiii  ');
    reorganizeForm();



    $(document).on('change', 'select#id_materials_needed_available,  select#id_share_expectations_caregiver, select#id_child_participate_others,  select#id_homework_after_lesson,  ' +
        'select#id_homework_after_lesson,  select#id_how_contact_caregivers ,  select#id_child_awareness_prevention_covid19  ', function(){
       reorganizeForm();
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

function reorganizeForm()
{

    alert('helo');




    var materials_needed_available = $('select#id_materials_needed_available').val();
    var share_expectations_caregiver = $('select#id_share_expectations_caregiver').val();
    var child_participate_others = $('select#id_child_participate_others').val();
    var homework_after_lesson = $('select#id_homework_after_lesson').val();
    var how_contact_caregivers = $('select#id_how_contact_caregivers').val();
    var child_awareness_prevention_covid19 = $('select#id_child_awareness_prevention_covid19').val();


    $('div#div_id_materials_needed_reason_no').addClass('d-none');
    $('#span_materials_needed_reason_no').addClass('d-none');
    if(materials_needed_available == 'no'){
        $('div#div_id_materials_needed_reason_no').removeClass('d-none');
        $('#span_materials_needed_reason_no').removeClass('d-none');
    }
    else{
        $('#id_materials_needed_reason_no').val('');
    }

    $('div#div_id_share_expectations_no_reason').addClass('d-none');
    $('#span_share_expectations_caregiver').addClass('d-none');
    if(share_expectations_caregiver == 'no'){
        $('div#div_id_share_expectations_no_reason').removeClass('d-none');
        $('#span_share_expectations_caregiver').removeClass('d-none');

    }
    else{
        $('#id_share_expectations_caregiver').val('');

    }

    $('div#div_id_child_participate_others_no_explain').addClass('d-none');
    $('#span_child_participate_others_no_explain').addClass('d-none');
    if(child_participate_others == 'no'){
        $('div#div_id_child_participate_others_no_explain').removeClass('d-none');
        $('#span_child_participate_others_no_explain').removeClass('d-none');
    }
    else{
        $('#id_child_participate_others_no_explain').val('');
    }

    $('div#div_id_homework_after_lesson_explain').addClass('d-none');
    $('#span_homework_after_lesson_explain').addClass('d-none');

    $('div#div_id_homework_score').addClass('d-none');
    $('#span_homework_score').addClass('d-none');

    $('div#div_id_homework_score_explain').addClass('d-none');
    $('#span_homework_score_explain').addClass('d-none');

    $('div#div_id_parents_supporting_student').addClass('d-none');
    $('#span_parents_supporting_student').addClass('d-none');

    $('div#div_id_parents_supporting_student_explain').addClass('d-none');
    $('#span_parents_supporting_student_explain').addClass('d-none');

    if(homework_after_lesson == 'yes'){
        $('div#div_id_homework_after_lesson_explain').removeClass('d-none');
        $('#span_homework_after_lesson_explain').removeClass('d-none');
        $('div#div_id_homework_score').removeClass('d-none');
        $('#span_homework_score').removeClass('d-none');
        $('div#div_id_homework_score_explain').removeClass('d-none');
        $('#span_homework_score_explain').removeClass('d-none');
        $('div#div_id_parents_supporting_student').removeClass('d-none');
        $('#span_parents_supporting_student').removeClass('d-none');
        $('div#div_id_parents_supporting_student_explain').removeClass('d-none');
        $('#span_parents_supporting_student_explain').removeClass('d-none');
    }
    else{
        $('#id_materials_needed_reason_no').val('');
        $('#id_homework_score').val('');
        $('#id_homework_score_explain').val('');
        $('#id_parents_supporting_student').val('');
        $('#id_parents_supporting_student_explain').val('');
    }


    $('div#div_id_how_keep_touch_caregivers_specify').addClass('d-none');
    $('#span_how_keep_touch_caregivers_specify').addClass('d-none');
    if(how_contact_caregivers == 'other'){
        $('div#div_id_how_keep_touch_caregivers_specify').removeClass('d-none');
        $('#span_how_keep_touch_caregivers_specify').removeClass('d-none');
    }
    else{
        $('#id_how_keep_touch_caregivers_specify').val('');
    }


    $('div#div_id_followup_done_messages').addClass('d-none');
    $('#span_followup_done_messages').addClass('d-none');

    $('div#div_id_followup_explain').addClass('d-none');
    $('#span_followup_explain').addClass('d-none');

    $('div#div_id_child_practice_basic_handwashing').addClass('d-none');
    $('#span_child_practice_basic_handwashing').addClass('d-none');

    $('div#div_id_child_practice_basic_handwashing_explain').addClass('d-none');
    $('#span_child_practice_basic_handwashing_explain').addClass('d-none');

    $('div#div_id_child_have_pss_wellbeing').addClass('d-none');
    $('#span_child_have_pss_wellbeing').addClass('d-none');

    $('div#div_id_child_have_pss_wellbeing_explain').addClass('d-none');
    $('#span_child_have_pss_wellbeing_explain').addClass('d-none');

    if(child_awareness_prevention_covid19 == 'yes'){
        $('div#div_id_followup_done_messages').removeClass('d-none');
        $('#span_followup_done_messages').removeClass('d-none');

        $('div#div_id_followup_explain').removeClass('d-none');
        $('#span_followup_explain').removeClass('d-none');

        $('div#div_id_child_practice_basic_handwashing').removeClass('d-none');
        $('#span_child_practice_basic_handwashing').removeClass('d-none');

        $('div#div_id_child_practice_basic_handwashing_explain').removeClass('d-none');
        $('#span_child_practice_basic_handwashing_explain').removeClass('d-none');

        $('div#div_id_child_have_pss_wellbeing').removeClass('d-none');
        $('#span_child_have_pss_wellbeing').removeClass('d-none');

        $('div#div_id_child_have_pss_wellbeing_explain').removeClass('d-none');
        $('#span_child_have_pss_wellbeing_explain').removeClass('d-none');
    }
    else{
        $('#id_followup_done_messages').val('');
        $('#id_followup_explain').val('');
        $('#id_child_practice_basic_handwashing').val('');
        $('#id_child_practice_basic_handwashing_explain').val('');
        $('#id_child_have_pss_wellbeing').val('');
        $('#id_child_have_pss_wellbeing_explain').val('');
    }
}
