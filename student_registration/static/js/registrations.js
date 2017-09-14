/**
 * Created by ali on 7/22/17.
 */

var arabic_fields = "#id_student_first_name, #id_student_father_name, #id_student_last_name, #id_student_mother_fullname";
var protocol = window.location.protocol;
var host = protocol+window.location.host;
var moved_student_path = host+'/api/logging-student-move/';
var current_school = null;

$(document).ready(function(){

    if($(document).find('#id_registration_date').length == 1) {
        $('#id_registration_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    reorganizeForm();

    $(document).on('click', 'input[name=new_registry], input[name=student_outreached], input[name=have_barcode], #id_student_family_status, input[name=have_labour]:checked', function(){
        reorganizeForm();
    });

    $(document).on('blur', arabic_fields, function(){
        checkArabicOnly($(this));
    });

    $(document).on('click', '.moved-button', function(){
        var item = $(this);
        if(confirm("Are you sure you want to tag this student as moved?")) {
            moved_student(item.attr('itemscope'));
            item.parents('tr').remove();
        }
    });
    $(document).on('click', '.delete-button', function(){
        var item = $(this);
        if(confirm("Are you sure you want to delete this student?")) {
            delete_student(item);
            item.parents('tr').remove();
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
                if($('#id_school_type').val() == undefined || $('#id_school_type').val() == 'alp'){
                    registry_id = ui.item.registration.id;
                    var refer_to_level = ui.item.registration.refer_to_level;
                    if(!$.inArray(refer_to_level, [1, 10, 11, 12, 13, 14, 15, 16, 17])){
                        if(confirm("This student is not eligible to go into 2nd shift program, are you sure you want to register this student")){
                            eligibility = false;
                        }else{
                            return false;
                        }
                    }
                    log_student_program_move(ui.item.registration, eligibility);
                }else{
                    registry_id = ui.item.enrollment.id;
                }
                var params = {
                    enrollment_id: registry_id,
                    new_registry: $('input[name=new_registry]:checked').val(),
                    student_outreached: $('input[name=student_outreached]:checked').val(),
                    have_barcode: $('input[name=have_barcode]:checked').val()
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
                    new_registry: $('input[name=new_registry]:checked').val(),
                    student_outreached: $('input[name=student_outreached]:checked').val(),
                    have_barcode: $('input[name=have_barcode]:checked').val()
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
                    + "<b>Base Data:</b> " + item.student_full_name + " - " + item.stduent_mother_fullname + " - " + item.student_id_number
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
    var new_registry = $('input[name=new_registry]:checked').val();
    var outreached = $('input[name=student_outreached]:checked').val();
    var have_barcode = $('input[name=have_barcode]:checked').val();
    var family_status = $('#id_student_family_status').val();
    var have_labour = $('input[name=have_labour]:checked').val();

    if(urlParam('child_id') || urlParam('enrollment_id') || $('#registry_block').hasClass('d-none')) {
        $('#registry_block').addClass('d-none');
        $('#register_by_barcode').addClass('d-none');
        $('#search_options').addClass('d-none');
        return true;
    }

    if(family_status == 'married' || family_status == 'divorced'){
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


    if(outreached == '0'){
        $('input[name=have_barcode]').val('0');
        $('#have_barcode_option').addClass('d-none');
        $('#have_barcode_option').prev().addClass('d-none');
    }else{
        $('#have_barcode_option').removeClass('d-none');
        $('#have_barcode_option').prev().removeClass('d-none');
    }
    if(have_barcode == '0'){
        $('#block_id_outreach_barcode').addClass('d-none');
        $('#block_id_outreach_barcode').prev().addClass('d-none');
    }else{
        $('#block_id_outreach_barcode').removeClass('d-none');
        $('#block_id_outreach_barcode').prev().removeClass('d-none');
    }

    if(new_registry == '1' && outreached == '1' && have_barcode == '1'){
        $('#block_id_outreach_barcode').addClass('d-none');
        $('#block_id_outreach_barcode').prev().addClass('d-none');

        $('#register_by_barcode').removeClass('d-none');
        $('#search_options').addClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

    if(new_registry == '1' && outreached == '1' && have_barcode == '0'){
        $('#register_by_barcode').addClass('d-none');
        $('#search_options').addClass('d-none');
        $('.child_data').removeClass('d-none');
        return true;
    }

    if(new_registry == '1' && outreached == '0'){

        $('#register_by_barcode').addClass('d-none');
        $('#search_options').addClass('d-none');
        $('.child_data').removeClass('d-none');

        return true;
    }

    if(new_registry == '0' && outreached == '0'){

        $('#register_by_barcode').addClass('d-none');
        $('#search_options').removeClass('d-none');
        $('.child_data').addClass('d-none');
        return true;
    }

    if(new_registry == '0' && outreached == '1' && have_barcode == '1'){

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

function delete_student(item)
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
