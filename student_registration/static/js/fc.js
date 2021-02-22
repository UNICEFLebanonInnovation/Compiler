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
          //     materials_needed_available
          //
          // share_expectations_caregiver
          //
          // child_participate_others
          //
          // homework_after_lesson
          //
          // homework_after_lesson
          //
          // how_contact_caregivers
          //
          // child_awareness_prevention_covid19


}
    // def clean(self):
    //
    //     cleaned_data = super(ABLNFCForm, self).clean()
    //     materials_needed_available = cleaned_data.get("materials_needed_available")
    //     materials_needed_reason_no = cleaned_data.get("materials_needed_reason_no")
    //     share_expectations_caregiver = cleaned_data.get("share_expectations_caregiver")
    //     share_expectations_no_reason = cleaned_data.get("share_expectations_no_reason")
    //     child_participate_others = cleaned_data.get("child_participate_others")
    //     child_participate_others_no_explain = cleaned_data.get("child_participate_others_no_explain")
    //     homework_after_lesson = cleaned_data.get("homework_after_lesson")
    //     homework_after_lesson_explain = cleaned_data.get("homework_after_lesson_explain")
    //     homework_score = cleaned_data.get("homework_score")
    //     homework_score_explain = cleaned_data.get("homework_score_explain")
    //     parents_supporting_student = cleaned_data.get("parents_supporting_student")
    //     parents_supporting_student_explain = cleaned_data.get("parents_supporting_student_explain")
    //     how_contact_caregivers = cleaned_data.get("how_contact_caregivers")
    //     how_keep_touch_caregivers_specify = cleaned_data.get("how_keep_touch_caregivers_specify")
    //     child_awareness_prevention_covid19 = cleaned_data.get("child_awareness_prevention_covid19")
    //     followup_done_messages = cleaned_data.get("followup_done_messages")
    //     followup_explain = cleaned_data.get("followup_explain")
    //     child_practice_basic_handwashing = cleaned_data.get("child_practice_basic_handwashing")
    //     child_practice_basic_handwashing_explain = cleaned_data.get("child_practice_basic_handwashing_explain")
    //     child_have_pss_wellbeing = cleaned_data.get("child_have_pss_wellbeing")
    //     child_have_pss_wellbeing_explain = cleaned_data.get("child_have_pss_wellbeing_explain")
    //
    //     if materials_needed_available == 'no':
    //         if not materials_needed_reason_no:
    //             self.add_error('materials_needed_reason_no', 'This field is required')
    //
    //     if share_expectations_caregiver == 'no':
    //         if not share_expectations_no_reason:
    //             self.add_error('share_expectations_no_reason', 'This field is required')
    //
    //     if child_participate_others == 'no':
    //         if not child_participate_others_no_explain:
    //             self.add_error('child_participate_others_no_explain', 'This field is required')
    //
    //     if homework_after_lesson == 'no':
    //         if not homework_after_lesson_explain:
    //             self.add_error('homework_after_lesson_explain', 'This field is required')
    //
    //     if homework_after_lesson == 'yes':
    //         if not homework_after_lesson_explain:
    //             self.add_error('homework_after_lesson_explain', 'This field is required')
    //         if not homework_score:
    //             self.add_error('homework_score', 'This field is required')
    //         if not homework_score_explain:
    //             self.add_error('homework_score_explain', 'This field is required')
    //         if not parents_supporting_student:
    //             self.add_error('parents_supporting_student', 'This field is required')
    //         if not parents_supporting_student_explain:
    //             self.add_error('parents_supporting_student_explain', 'This field is required')
    //
    //     if how_contact_caregivers == 'other':
    //         if not how_keep_touch_caregivers_specify:
    //             self.add_error('how_keep_touch_caregivers_specify', 'This field is required')
    //
    //     if child_awareness_prevention_covid19 == 'yes':
    //         if not followup_done_messages:
    //             self.add_error('followup_done_messages', 'This field is required')
    //         if not followup_explain:
    //             self.add_error('followup_explain', 'This field is required')
    //         if not child_practice_basic_handwashing:
    //             self.add_error('child_practice_basic_handwashing', 'This field is required')
    //         if not child_practice_basic_handwashing_explain:
    //             self.add_error('child_practice_basic_handwashing_explain', 'This field is required')
    //         if not child_have_pss_wellbeing:
    //             self.add_error('child_have_pss_wellbeing', 'This field is required')
    //         if not child_have_pss_wellbeing_explain:
    //             self.add_error('child_have_pss_wellbeing_explain', 'This field is required')
