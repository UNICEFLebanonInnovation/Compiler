
var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(window).load(function () {

});

$(document).ready(function(){
    reorganizeForm();

    if($(document).find('#id_dropout_date').length == 1) {
        $('#id_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_follow_up_type, select#id_follow_up_result, select#id_parent_attended_meeting, select#id_caregiver_attended' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
//  Followup
    var follow_up_type = $('select#id_follow_up_type').val();
     if (follow_up_type == 'Phone call'){
        $('div#div_id_phone_call_number').removeClass('d-none');
        $('#id_phone_call_number').addClass('error-field');

        $('#id_house_visit_number').val(0);
        $('div#div_id_house_visit_number').addClass('d-none');
        $('#id_house_visit_number').removeClass('error-field');

        $('#id_caregiver_visit_number').val(0);
        $('div#div_id_caregiver_visit_number').addClass('d-none');
        $('#id_caregiver_visit_number').removeClass('error-field');
     }
     else if(follow_up_type == 'Home Visits'){
        $('div#div_id_house_visit_number').removeClass('d-none');
        $('#id_house_visit_number').addClass('error-field');

        $('#id_phone_call_number').val(0);
        $('div#div_id_phone_call_number').addClass('d-none');
        $('#id_phone_call_number').removeClass('error-field');

        $('#id_caregiver_visit_number').val(0);
        $('div#div_id_caregiver_visit_number').addClass('d-none');
        $('#id_caregiver_visit_number').removeClass('error-field');
     }
     else if(follow_up_type == 'Caregiver visited the center'){
        $('div#div_id_caregiver_visit_number').removeClass('d-none');
        $('#id_caregiver_visit_number').addClass('error-field');

        $('#id_phone_call_number').val(0);
        $('div#div_id_phone_call_number').addClass('d-none');
        $('#id_phone_call_number').removeClass('error-field');

        $('#id_house_visit_number').val(0);
        $('div#div_id_house_visit_number').addClass('d-none');
        $('#id_house_visit_number').removeClass('error-field');
     }
     else{
        $('#id_phone_call_number').val(0);
        $('div#div_id_phone_call_number').addClass('d-none');
        $('#id_phone_call_number').removeClass('error-field');

        $('#id_house_visit_number').val(0);
        $('div#div_id_house_visit_number').addClass('d-none');
        $('#id_house_visit_number').removeClass('error-field');

        $('#id_caregiver_visit_number').val(0);
        $('div#div_id_caregiver_visit_number').addClass('d-none');
        $('#id_caregiver_visit_number').removeClass('error-field');
     }

//    Dropout
    var follow_up_result = $('select#id_follow_up_result').val();
    if (follow_up_result == 'Dropout/No Interest'){
        $('#div_id_dropout_reason').removeClass('d-none');
        $('#id_dropout_reason').addClass('error-field');

        $('#div_id_dropout_date').removeClass('d-none');
        $('#id_dropout_date').addClass('error-field');
    }
    else
    {
        $('div#div_id_dropout_reason').addClass('d-none');
        $('#id_dropout_reason').removeClass('error-field');
        $('#id_dropout_reason').val('');

        $('div#div_id_dropout_date').addClass('d-none');
        $('#id_dropout_date').removeClass('error-field');
        $('#id_dropout_date').val('');
    }

//    Parents meeting
    var parent_attended_meeting = $('select#id_parent_attended_meeting').val();
    if (parent_attended_meeting == 'Yes'){
        $('#div_id_meeting_type').removeClass('d-none');
        $('#id_meeting_type').addClass('error-field');

        $('#div_id_meeting_number').removeClass('d-none');
        $('#id_meeting_number').addClass('error-field');

        $('#div_id_meeting_modality').removeClass('d-none');
        $('#id_meeting_modality').addClass('error-field');

        $('#div_id_caregiver_attended').removeClass('d-none');
        $('#id_caregiver_attended').addClass('error-field');

        var caregiver_attended = $('select#id_caregiver_attended').val();
        alert(caregiver_attended);
        if (caregiver_attended=='Other'){
            alert('other');
            $('#div_id_caregiver_attended_other').removeClass('d-none');
            $('#id_caregiver_attended_other').addClass('error-field');
        }
        else
        {
            $('div#div_id_caregiver_attended_other').addClass('d-none');
            $('#id_caregiver_attended_other').removeClass('error-field');
            $('#id_caregiver_attended_other').val('');
        }
    }
    else
    {
        $('div#div_id_meeting_type').addClass('d-none');
        $('#id_meeting_type').removeClass('error-field');
        $('#id_meeting_type').val('');

        $('div#div_id_meeting_number').addClass('d-none');
        $('#id_meeting_number').removeClass('error-field');
        $('#id_meeting_number').val(0);

        $('div#div_id_meeting_modality').addClass('d-none');
        $('#id_meeting_modality').removeClass('error-field');
        $('#id_meeting_modality').val('');

        $('div#div_id_caregiver_attended').addClass('d-none');
        $('#id_caregiver_attended').removeClass('error-field');
        $('#id_caregiver_attended').val('');

        $('div#div_id_caregiver_attended_other').addClass('d-none');
        $('#id_caregiver_attended_other').removeClass('error-field');
        $('#id_caregiver_attended_other').val('');
    }
  }

