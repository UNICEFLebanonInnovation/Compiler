/**
 * Created by ali on 10/13/17.
 */

$(document).ready(function(){

    $(document).on('click', '.closing-reason-b', function () {
        if(confirm($(this).attr('translation'))){
            var data = {
                owner: $('input#owner').val(),
                attendance_date: $('select#dates').val(),
                school: $('input#school').val(),
                close_reason: $(this).attr('itemref'),
                students: {}
            };
            set_attendances(data);
            $('.closing-reason-b').hide();
            $('.closing-reason-b').addClass('disabled');
            $(this).show();
        }
    });

    $(document).on('change', '#dates', function(){
        if($(this).val()) {
            window.location = $('#dates').find('option:selected').attr('data-action');
        }
    });

    $(document).on('click', '#save_attendances', function(){
        if(confirm($(this).attr('translation'))) {
            var level_section = get_level_section_attendances(false);

            var data = {
                    owner: $('input#owner').val(),
                    attendance_date: $('input#attendance_date').val(),
                    school: $('input#school').val(),
                    total_enrolled: $('.enrollment_id').length
            };
            set_attendances(data, level_section);
        }
    });

    $(document).on('click', '#attendance_validate', function(){
        var today = new Date();
        var dd = today.getDate();
        var mm = today.getMonth()+1; //January is 0!
        var yyyy = today.getFullYear();
        var attendance = $(this).attr('itemref');
        if(confirm($(this).attr('translation'))) {
            var data = {
                validation_owner: $('input#owner').val(),
                validation_status: true,
                validation_date: yyyy+'-'+mm+'-'+dd
            };
            patch_attendances(attendance, data);
            $(this).addClass('disabled');
            $('.attendance-status').removeClass('icon-pending-check');
            $('.attendance-status').removeClass('icon-check');
            $('.attendance-status').addClass('icon-2-check');
        }
    });

    $(document).on('click', '#exam_day', function(){
        if(confirm($(this).attr('translation'))) {
            var level_section = {};
            var level_section_name = $('#level').val() + "-" + $('#section').val();
            level_section[level_section_name] = {
                students: {},
                total_enrolled: $('.enrollment_id').length,
                total_absences: 0,
                total_attended: 0,
                total_attended_male: 0,
                total_attended_female: 0,
                total_absent_male: 0,
                total_absent_female: 0,
                exam_day: true
            };

            var data = {
                    owner: $('input#owner').val(),
                    attendance_date: $('input#attendance_date').val(),
                    school: $('input#school').val(),
                    total_enrolled: $('.enrollment_id').length
            };
            set_attendances(data, level_section);
            $(this).remove();
            $('#save_attendances').remove();
            $("[class='toggle-status']").remove();
        }
    });

    $("[class='toggle-status']").bootstrapSwitch();
    $("[class='toggle-status']").on('switchChange.bootstrapSwitch', function(event, state) {
        $("[class='status-checkbox']").bootstrapSwitch('state', state);
        var itemid = $(event.target).attr('itemid');
        $(event.target).val(state);
        if(state == false){
            $('#reasons-'+itemid).removeClass('d-none');
        }else{
            $('#reasons-'+itemid).addClass('d-none');
        }
    });
});

function get_level_section_attendances(exam_day)
{
    var students = new Array();
    var level_section = {};
    var total_absences = 0;
    var total_attended = 0;
    var total_attended_male = 0;
    var total_attended_female = 0;
    var total_absent_male = 0;
    var total_absent_female = 0;
    $('.enrollment_id').each(function (i, item) {
        var enrollment_id = $(item).val();
        var status = null;
        var sex = $('#student_sex_'+enrollment_id).val();
        var absence_reason = null;

        if($('#status_'+enrollment_id).val() == '' || $('#status_'+enrollment_id).val() == 'True'){
            status = 'True';
            absence_reason  = '';
            if(sex == 'Male'){
                total_attended_male = total_attended_male + 1;
            }else{
                total_attended_female = total_attended_female + 1;
            }
        }else{
            status = 'False';
            absence_reason  = $('.absence_reason_' + enrollment_id+':checked').val();
            if(sex == 'Male'){
                total_absent_male = total_absent_male + 1;
            }else{
                total_absent_female = total_absent_female + 1;
            }
        }

        total_attended = total_attended_male + total_attended_female;
        total_absences = total_absent_male + total_absent_female;
        var student_id = $('#student_id_' + enrollment_id).val();

        students.push({
            student_id: student_id,
            student_fullname: $('#student_fullname_' + enrollment_id).val(),
            student_sex: sex,
            student_age: $('#student_age_' + enrollment_id).val(),
            student_birthday: $('#student_birthday_' + enrollment_id).val(),
            section: $('#section_' + enrollment_id).val(),
            section_name: $('#section_name_' + enrollment_id).val(),
            level: $('#level_' + enrollment_id).val(),
            level_name: $('#level_name_' + enrollment_id).val(),
            status: status,
            absence_reason: absence_reason
        });

    });

    var level_section_name = $('#level').val() + "-" + $('#section').val();
    level_section[level_section_name] = {
        students: students,
        total_enrolled: students.length,
        total_absences: total_absences,
        total_attended: total_attended,
        total_attended_male: total_attended_male,
        total_attended_female: total_attended_female,
        total_absent_male: total_absent_male,
        total_absent_female: total_absent_female,
        exam_day: exam_day
    };
    return level_section;
}

function disable_attendance()
{
    $('.closing-reason-b').attr('disabled', 'disabled');
    $('.row-class').addClass('disabled');
}

function set_attendances(data, patch_data)
{
    $.ajax({
        type: "POST",
        url: "/api/attendances/",
        data: data,
        cache: false,
        async: true,
        headers: getHeader(),
        dataType: 'json',
        success: function (response, result, jqXHR) {
            if(response.data){
                console.log(response.status);
                console.log(patch_data);
                if(response.status == 200 && patch_data == undefined){
                    patch_attendances(response.data, data);
                }else{
                    update_attendances(response.data, patch_data);
                }
            }else{
                display_feedback(true);
            }
        },
        error: function (response) {
            console.log(response);
            display_feedback(false);
        }
    });
}

function update_attendances(id, data)
{
    $.ajax({
        type: "PUT",
        url: "/api/attendances/"+id+"/",
        data: JSON.stringify(data),
        cache: false,
        async: true,
        headers: getHeader(),
        dataType: 'json',
        success: function (response, result, jqXHR) {
            if(response.data){
                display_feedback(true);
            }
        },
        error: function (response) {
            display_feedback(false);
        }
    });
}

function patch_attendances(id, data)
{
    $.ajax({
        type: "PATCH",
        url: "/api/attendances/"+id+"/",
        data: data,
        cache: false,
        async: true,
        headers: getHeader(),
        dataType: 'json',
        success: function (response, result, jqXHR) {
            if(response.data){
                display_feedback(true);
            }
        },
        error: function (response) {
            display_feedback(false);
        }
    });
}

function display_feedback(status)
{
    $('.alert').addClass('d-none');

    if(status){
        $('.alert-success').removeClass('d-none');
    }else{
        $('.alert-danger').removeClass('d-none');
    }
}
