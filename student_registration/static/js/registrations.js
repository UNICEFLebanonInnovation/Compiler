/**
 * Created by ali on 7/22/17.
 */

var arabic_fields = "#id_student_first_name, #id_student_father_name, #id_student_last_name, #id_student_mother_fullname, input#id_location";
var protocol = window.location.protocol;
var host = protocol+window.location.host;
var moved_student_path = host+'/api/logging-student-move/';
var current_school = null;
var eligibility_msg = '';
var min_age_limit_msg = '';
var max_age_limit_msg = '';

$(document).ready(function(){

    if($(document).find('#id_registration_date').length == 1) {
        $('#id_registration_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    reorganizeForm();

    $(document).on('change', 'select#id_level', function(){

         if($(document).find('#id_exam_result_arabic').length == 1) {
             var max_value = 30;
             var value = $('select#id_level').val();
             if(value == 4 || value == 5 || value == 6){
                 max_value = 60;
             }
             if(value == 7 || value == 8 || value == 9){
                 max_value = 90;
             }
             $('#id_exam_result_arabic, #id_exam_result_language, #id_exam_result_math, #id_exam_result_science').attr('max', max_value);
         }
    });

    $(document).on('change', 'select#id_site', function(){
         reorganizeForm();
    });

    // $(document).on('change', 'select#id_classroom, select#id_student_birthday_day, select#id_student_birthday_month, select#id_student_birthday_year', function(){
    //      verify_age_level();
    // });

    $(document).on('change', 'select#id_student_registered_in_unhcr', function(){
        reorganizeForm();
    });

    $(document).on('click', 'input[name=have_labour]', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_new_registry', function(){
        reorganizeForm();
    });
    $(document).on('change', 'select#id_student_outreached', function(){
        reorganizeForm();
    });
    $(document).on('change', 'select#id_have_barcode', function(){
        reorganizeForm();
    });

    $(document).on('change', '#id_student_family_status', function(){
        reorganizeForm();
    });

    $(document).on('blur', arabic_fields, function(){
        checkArabicOnly($(this));
    });

    $(document).on('blur', '#id_student_id_number', function(){
        var result = true;
        var type = $('#id_student_id_type').val();
        var value = $(this).val();
        if(type == 1){
            result = check_unhcr_number(value);
        }
        if(type == 3) {
            result = check_national_id(value);
        }
        if(!result){
            $(this).val('');
        }
    });

    $(document).on('click', '.moved-button', function(){
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            moved_student(item.attr('itemscope'));
            item.parents('tr').remove();
        }
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
            window.location = item.attr('href');
        }
    });

    if($(document).find('#id_search_student').length == 1) {

        $("#id_search_student").autocomplete({
            source: function (request, response) {
                var school = $('#id_search_school').val();
                if (school == '') { school = 0; }

                var school_type = $('#id_school_type').val();
                if (school_type == undefined){
                    school_type = 'alp';
                }

                $.ajax({
                    url: '/api/students-search/?school=' + school + '&school_type=' + school_type,
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                        response(data);
                    }
                });
            },
            minLength: 3,
            select: function (event, ui) {
                var registry_id = 0;
                var eligibility = true;
                var school_type = $('#id_school_type').val();
                if(school_type == undefined || school_type == 'alp'){
                    registry_id = ui.item.registration.id;
                    if(school_type == 'alp') {
                        var refer_to_level = ui.item.registration.refer_to_level;
                        if (!$.inArray(refer_to_level, [1, 10, 11, 12, 13, 14, 15, 16, 17])) {
                            if (confirm(eligibility_msg)) {
                                eligibility = false;
                            } else {
                                return false;
                            }
                        }
                        log_student_program_move(ui.item.registration, eligibility);
                    }
                }else{
                    registry_id = ui.item.enrollment.id;
                }
                var params = {
                    enrollment_id: registry_id,
                    new_registry: $('select#id_new_registry').val(),
                    student_outreached: $('select#id_student_outreached').val(),
                    have_barcode: $('select#id_have_barcode').val(),
                    school_type: school_type
                };
                var str = '?'+jQuery.param( params );

                window.location = $(document).find('form').attr('action')+str;
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#id_search_student").autocomplete("instance")._renderItem = function (ul, item) {
            var registry = item.enrollment;
            if(registry){
                var education_year_name = registry.education_year_name;
            }
            if($('#id_school_type').val() == undefined || $('#id_school_type').val() == 'alp'){
                registry = item.registration;
                education_year_name = registry.alp_round_name;
            }

            return $("<li>")
                .append("<div style='border: 1px solid;'>"
                    + "<b>Base Data:</b> " + item.full_name + " - " + item.mother_fullname + " - " + item.id_number
                    + "<br/> <b>Gender - Birthday:</b> " + item.sex + " - " + item.birthday
                    + "<br/> <b>Last education year:</b> " + education_year_name
                    + "<br/> <b>Last education school:</b> " + registry.school_name + " - " + registry.school_number
                    + "<br/> <b>Class / Section:</b> " + registry.classroom_name + " / " + registry.section_name
                    + "</div>")
                .appendTo(ul);
        };
    }

    if($(document).find('#id_search_clm_student').length == 1) {

        $("#id_search_clm_student").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/api/clm-students/?clm_type='+$('#id_clm_type').val(),
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                        response(data);
                    }
                });
            },
            minLength: 3,
            select: function (event, ui) {
                var params = {
                    enrollment_id: ui.item.id,
                    new_registry: $('select#id_new_registry').val(),
                    student_outreached: $('select#id_student_outreached').val(),
                    have_barcode: $('select#id_have_barcode').val()
                };
                var str = '?'+jQuery.param( params );

                window.location = $(document).find('form').attr('action')+str;
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#id_search_clm_student").autocomplete("instance")._renderItem = function (ul, item) {

            return $("<li>")
                .append("<div style='border: 1px solid;'>"
                    + "<b>Base Data:</b> " + item.student_full_name + " - " + item.student_mother_fullname
                    + "<br/> <b>Gender - Birthday:</b> " + item.student_sex + " - " + item.student_birthday
                    // + "<br/> <b>Round:</b> " + item.round_name
                    + "</div>")
                .appendTo(ul);
        };
    }

    if($(document).find('#id_search_barcode').length == 1) {

        $("#id_search_barcode").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/api/child/',
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                        response(data);
                    }
                });
            },
            minLength: 10,
            select: function (event, ui) {

                var params = {
                    child_id: ui.item.child_id,
                    new_registry: $('select#id_new_registry').val(),
                    student_outreached: $('select#id_student_outreached').val(),
                    have_barcode: $('select#id_have_barcode').val()
                };
                var str = '?'+jQuery.param( params );

                window.location = $(document).find('form').attr('action')+str;
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#id_search_barcode").autocomplete("instance")._renderItem = function (ul, item) {
            return $("<li>")
                .append("<div style='border: 1px solid;'>"
                    + "<b>Base Data:</b> " + item.student_full_name + " - " + item.student_mother_fullname + " - " + item.student_id_number
                    + "<br/> <b>Gender - Birthday:</b> " + item.student_sex + " - " + item.student_birthday
                    + "</div>")
                .appendTo(ul);
        };
    }

    if($(document).find('#id_outreach_barcode').length == 1) {

        $("#id_outreach_barcode").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/api/child/',
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                        response(data);
                    }
                });
            },
            minLength: 10,
            select: function (event, ui) {
                console.log(ui.item);
                $('#id_outreach_barcode').val(ui.item.barcode_subset);
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#id_outreach_barcode").autocomplete("instance")._renderItem = function (ul, item) {
            return $("<li>")
                .append("<div style='border: 1px solid;'>"
                    + "<b>Base Data:</b> " + item.student_full_name + " - " + item.stduent_mother_fullname + " - " + item.student_id_number
                    + "<br/> <b>Gender - Birthday:</b> " + item.student_sex + " - " + item.student_birthday
                    + "</div>")
                .appendTo(ul);
        };
    }

    if($(document).find('#search_moved_student').length == 1) {

        $("#search_moved_student").autocomplete({
            source: function (request, response) {
                $.ajax({
                    url: '/api/logging-student-move/',
                    dataType: "json",
                    data: {
                        term: request.term
                    },
                    success: function (data) {
                        response(data);
                    }
                });
            },
            minLength: 3,
            select: function (event, ui) {
                console.log(ui);
                $("#search_moved_student").val('');
                window.location = '/enrollments/moved/' + ui.item.enrolment_id + '/' + ui.item.id;
                return false;
            }
        }).autocomplete("instance")._renderMenu = function (ul, items) {
            var that = this;
            $.each(items, function (index, item) {
                that._renderItemData(ul, item);
            });
            $(ul).find("li:odd").addClass("odd");
        };

        $("#search_moved_student").autocomplete("instance")._renderItem = function (ul, item) {
            return $("<li>")
                .append("<div style='border: 1px solid;'>" + item.student_full_name + " - " + item.student_mother_fullname + " (" + item.student_sex + " - " + item.student_age + ") "
                    + "<br> Current situation: " + item.school_name + " - " + item.school_number + " / " + item.classroom_name + " / " + item.section_name
                    + "</div>")
                .appendTo(ul);
        };
    }
});

function urlParam(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results && results.length){
        return results[1] || 0;
    }
    return 0;
}

function reorganizeForm()
{
    var new_registry = $('select#id_new_registry').val();
    var outreached = $('select#id_student_outreached').val();
    var have_barcode = $('select#id_have_barcode').val();
    var family_status = $('select#id_student_family_status').val();
    var have_labour = $('input[name=have_labour]:checked').val();
    var program_site = $('select#id_site').val();
    var registered_unhcr = $('select#id_student_registered_in_unhcr').val();

    if(program_site == 'out_school') {
        $('div#div_id_school').parent().addClass('d-none');
        $('div#div_id_school').parent().prev().addClass('d-none');
    }else{
        $('div#div_id_school').parent().removeClass('d-none');
        $('div#div_id_school').parent().prev().removeClass('d-none');
    }

    if(family_status == 'married' || family_status == 'divorced' || family_status == 'widower'){
        $('div#student_have_children').removeClass('d-none');
        $('div#student_have_children').prev().removeClass('d-none');
    }else{
        $('div#student_have_children').addClass('d-none');
        $('div#student_have_children').prev().addClass('d-none');
    }

    if(have_labour == 'yes_morning' || have_labour == 'yes_afternoon'){
        $('div#labours').removeClass('d-none');
        $('div#labours').prev().removeClass('d-none');
        $('div#labour_hours').removeClass('d-none');
        $('div#labour_hours').prev().removeClass('d-none');
    }else{
        $('div#labours').addClass('d-none');
        $('div#labours').prev().addClass('d-none');
        $('div#labour_hours').addClass('d-none');
        $('div#labour_hours').prev().addClass('d-none');
    }

    if(registered_unhcr == '1') {
        $('select#id_student_id_type').val(1);
    }

    if(have_barcode == 'no'){
        $('#block_id_outreach_barcode').addClass('d-none');
        $('#block_id_outreach_barcode').prev().addClass('d-none');
    }else{
        $('#block_id_outreach_barcode').removeClass('d-none');
        $('#block_id_outreach_barcode').prev().removeClass('d-none');
    }

    if(urlParam('child_id') || urlParam('enrollment_id') || $('#registry_block').hasClass('d-none')) {
        $('#registry_block').addClass('d-none');
        $('#register_by_barcode').addClass('d-none');
        $('#search_options').addClass('d-none');
        return true;
    }

    if(outreached == 'no'){
        $('#have_barcode_option').addClass('d-none');
        $('#have_barcode_option').prev().addClass('d-none');
        $('select#id_have_barcode').val('no');
    }else{
        $('#have_barcode_option').removeClass('d-none');
        $('#have_barcode_option').prev().removeClass('d-none');
        // $('select#id_have_barcode').val('yes');
    }

    if(new_registry == 'yes' && outreached == 'yes' && have_barcode == 'yes'){
        $('#block_id_outreach_barcode').removeClass('d-none');
        $('#block_id_outreach_barcode').prev().removeClass('d-none');

        $('#register_by_barcode').removeClass('d-none');
        $('#search_options').addClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

    if(new_registry == 'yes' && outreached == 'yes' && have_barcode == 'no'){
        $('#register_by_barcode').addClass('d-none');
        $('#search_options').addClass('d-none');
        $('.child_data').removeClass('d-none');
        return true;
    }

    if(new_registry == 'yes' && outreached == 'no'){

        $('#register_by_barcode').addClass('d-none');
        $('#search_options').addClass('d-none');
        $('.child_data').removeClass('d-none');

        return true;
    }

    if(new_registry == 'no' && outreached == 'no'){

        $('#register_by_barcode').addClass('d-none');
        $('#search_options').removeClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

    if(new_registry == 'no' && outreached == 'yes' && have_barcode == 'yes'){

        $('#register_by_barcode').addClass('d-none');
        $('#search_options').removeClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }
    if(new_registry == 'no' && outreached == 'yes' && have_barcode == 'no'){

        $('#register_by_barcode').addClass('d-none');
        $('#search_options').removeClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

}


function moved_student(item)
{
    var data = {moved: item};

    $.ajax({
        type: "POST",
        url: '/api/logging-student-move/',
        data: data,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}

function delete_student(item, callback)
{
    var url = item.attr('data-action');

    $.ajax({
        type: "DELETE",
        url: url+'/',
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            if(callback != undefined){
                callback();
            }
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}

// log student move from ALP to 2nd shift
function log_student_program_move(item, eligibility)
{
    var data = {
        student: item.student_id,
        registry: item.id,
        school_from: item.school,
        school_to: current_school,
        eligibility: eligibility
    };

    $.ajax({
        type: "POST",
        url: '/api/logging-student-program-move/',
        data: data,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            console.log(response);
        },
        error: function(response) {
            console.log(response);
        }
    });
}


function verify_age_level()
{
    var level = $('select#id_classroom').val();
    var day = $('select#id_student_birthday_day').val();
    var month = $('select#id_student_birthday_month').val();
    var year = $('select#id_student_birthday_year').val();
    var birthday = year+"-"+month+"-"+day;
    var dob = new Date(birthday);
    var min_date = new Date('2017-01-31');

    if(dob == NaN || level == '') {
        return false;
    }

    if(level == '1') { //KG
        min_date = new Date('2017-09-14');
        display_alert(dob, 5, 9, min_date);
    }
    if(level == '2') { //Level 1
        display_alert(dob, 6, 10, min_date);
    }
    if(level == '3') { //Level 2
        display_alert(dob, 7, 13, min_date);
    }
    if(level == '4') { //Level 3
        display_alert(dob, 8, 14, min_date);
    }
    if(level == '5') { //Level 4
        display_alert(dob, 9, 15, min_date);
    }
    if(level == '6') { //Level 5
        display_alert(dob, 10, 18, min_date);
    }
    if(level == '7') { //Level 6
        display_alert(dob, 11, 18, min_date);
    }
    if(level == '8') { //Level 7
        display_alert(dob, 12, 18, min_date);
    }
    if(level == '9') { //Level 8
        display_alert(dob, 13, 19, min_date);
    }
    if(level == '10') { //Level 9
        display_alert(dob, 14, 20, min_date);
    }
}

function display_alert(dob, min_value, max_value, min_date)
{
    var today = new Date();
    var min_age = Math.floor((min_date-dob) / (365.25 * 24 * 60 * 60 * 1000));
    var max_age = Math.floor((today-dob) / (365.25 * 24 * 60 * 60 * 1000));

    if(min_age < min_value) {
        var msg1 = min_age_limit_msg + " : " + min_value;
        alert(msg1);
        $('select#id_student_birthday_year').val("");
        return false;
    }
    if(max_age > max_value) {
        var msg2 = max_age_limit_msg + " : " + max_value;
        if(confirm(msg2)){

        }else{
            $('select#id_student_birthday_year').val("");
        }
        return false;
    }
    return true;
}
