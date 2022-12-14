
var arabic_fields = "#id_child_first_name, #id_child_father_name, #id_child_last_name, #id_child_mother_fullname, ," +
    " #id_caregiver_mother_name, #id_caregiver_last_name, #id_caregiver_middle_name, #id_caregiver_first_name";
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

$(document).ready(function() {

    $(document).on('click', '.delete-button', function(){
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            var callback = function(){
                item.parents('tr').remove();
            };
            delete_student(item, callback());
        }
    });

    $(document).on('change', 'select#id_source_of_identification', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_round', function () {
        duplicate_search_student_name();
    });

    $(document).on('change', 'input#id_student_first_name', function () {
        duplicate_search_student_name();
    });

    $(document).on('change', 'input#id_student_father_name', function(){
        duplicate_search_student_name();
    });

    $(document).on('change', 'input#id_student_last_name', function () {
        duplicate_search_student_name();

    });

    $(document).on('change', 'input#id_student_mother_fullname', function () {
        duplicate_search_student_name();

    });

    $(document).on('change', 'input#id_case_number, ' +
        'input#id_recorded_number, ' +
        'input#id_parent_syrian_national_number, ' +
        'input#id_parent_sop_national_number, ' +
        'input#id_parent_national_number, ' +
        'input#id_parent_other_number', function () {
        duplicate_search('id');

    });

    $(document).on('change', 'input#id_phone_number', function() {
        var student_first_name= $('#id_student_first_name').val();
        // var student_father_name= $('#id_student_father_name').val();
        var phone_number= $('#id_phone_number').val();

        if (student_first_name!='' && phone_number!='' )
        {
            duplicate_search('phone');
        }
    });

    $(document).on('change', '#id_id_type', function(){
        reorganizeForm();

        $('#id_case_number').val('');
        $('#id_case_number_confirm').val('');
        $('#id_individual_case_number').val('');
        $('#id_individual_case_number_confirm').val('');
        $('#id_parent_individual_case_number').val('');
        $('#id_parent_individual_case_number_confirm').val('');
        $('#id_recorded_number').val('');
        $('#id_recorded_number_confirm').val('');
        $('#id_national_number').val('');
        $('#id_national_number_confirm').val('');
        $('#id_syrian_national_number').val('');
        $('#id_syrian_national_number_confirm').val('');
        $('#id_sop_national_number').val('');
        $('#id_sop_national_number_confirm').val('');
        $('#id_parent_national_number').val('');
        $('#id_parent_national_number_confirm').val('');
        $('#id_parent_syrian_national_number').val('');
        $('#id_parent_syrian_national_number_confirm').val('');
        $('#id_parent_sop_national_number').val('');
        $('#id_parent_sop_national_number_confirm').val('');
        $('#id_parent_other_number').val('');
        $('#id_parent_other_number_confirm').val('');
        $('#id_other_number').val('');
        $('#id_other_number_confirm').val('');
//        Child have no ID = 7
        if($(this).val() != 7){
            return true;
        }
        if(confirm($(this).attr('translation'))) {
            $('#id_no_child_id_confirmation').val('confirmed');
        }else{
            $('#id_id_type').val('');
            $('#id_no_child_id_confirmation').val('');
        }

    });

    $(document).on('change', '#id_parent_id_type', function(){
        reorganizeForm();
        if($(this).val() != 'Parent have no ID'){

            return true;
        }
        if(confirm($(this).attr('translation'))) {
            $('#id_no_parent_id_confirmation').val('confirmed');
        }else{
            $('#id_parent_id_type').val('');
            $('#id_no_parent_id_confirmation').val('');
        }
    });

    reorganizeForm();

    $(document).on('change', 'select#id_child_marital_status', function(){

         marital_status();
    });

    $(document).on('change', 'select#id_student_nationality, select#id_have_labour_single_selection, select#id_labour_weekly_income', function(){
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

    $(document).on('change', 'select#id_main_caregiver', function(){
        var main_caregiver = $('select#id_main_caregiver').val();

        $('div#div_id_other_caregiver_relationship').addClass('d-none');
        $('#span_other_caregiver_relationship').addClass('d-none');

        if(main_caregiver == 'father'){
            var student_father_name = $('#id_student_father_name').val();
            var student_last_name = $('#id_student_last_name').val();
            $('#id_caretaker_first_name').val(student_father_name);
            $('#id_caretaker_last_name').val(student_last_name);
        }
        else if(main_caregiver == 'mother'){
            var student_mother_name = $('#id_student_mother_fullname').val();
            $('#id_caretaker_mother_name').val(student_mother_name);
        }

        else if(main_caregiver == 'other'){
            $('div#div_id_other_caregiver_relationship').removeClass('d-none');
            $('#span_other_caregiver_relationship').removeClass('d-none');

            $('#id_caretaker_first_name').val('');
            $('#id_caretaker_last_name').val('');
        }
        else {
            $('#id_caretaker_first_name').val('');
            $('#id_caretaker_last_name').val('');
        }
    });

    $(document).on('change', 'select#id_main_caregiver_nationality', function(){

        var nationality = $('select#id_main_caregiver_nationality').val();
        $('div#div_id_main_caregiver_nationality_other').addClass('d-none');
        $('#span_main_caregiver_nationality_other').addClass('d-none');

        if(nationality == 6){
            $('div#div_id_main_caregiver_nationality_other').removeClass('d-none');
            $('#span_main_caregiver_nationality_other').removeClass('d-none');
        }
        else {
            $('#id_main_caregiver_nationality_other').val('');
        }
    });

    $(document).on('click', 'input[name=student_have_children]', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_student_registered_in_unhcr', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_have_barcode', function(){
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
    //$(document).pjax('a', '.content-wrap', {fragment: '.content-wrap'});

    $(document).on('pjax:beforeReplace', function()
    {
        $('.content-wrap').css('opacity', '0.1');
        setTimeout(function() {
            $('.content-wrap').fadeTo('100', '1');
        }, 1);
    });
});

function pageScripts()
{
    /* Magnific Popup */
    $('.image-link').magnificPopup({
        type: 'image',
        gallery: {
            enabled: true
        }
    });
}

function urlParam(name)
{
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results && results.length){
        return results[1] || 0;
    }
    return 0;
}

function check_duplicate_registration()
{
    enrollment_id = $('#id_enrollment_id').val();
    partner_name = $('#id_partner_name').val();
    id_round = $('#id_round').val();
    if (enrollment_id > 0 && id_round > 0 )
    {
        if (isAddPage() && ($('.errorlist').length == 0) )
        {
            alert("The child already exists with the partner " + partner_name);
            $(':input[type="submit"][name="save_add_another"]').prop('disabled', true);
            $(':input[type="submit"][name="save"]').prop('disabled', true);
        }
        else
        {
            $(':input[type="submit"][name="save_add_another"]').prop('disabled', false);
            $(':input[type="submit"][name="save"]').prop('disabled', false);
        }
    }
}

function isAddPage()
{
    var url_loc = window.location.toString();
    return (url_loc.toLowerCase().search(/^.*\/clm\/mscc-add|abln-add|cbece-add|rs-add|inclusion-add|bridging-add|outreach-add(\*)(\?.*)?$/i)>=0);
}

function reorganizeForm()
{
    var registered_unhcr = $('select#id_student_registered_in_unhcr').val();
    var id_type = $('select#id_id_type').val();
    var nationality = $('select#id_student_nationality').val();
    var have_children = $('input[name=student_have_children]:checked').val();
    var have_labour = $('select#id_have_labour_single_selection').val();
    var labour_selection = $('select#id_labours_single_selection').val();
    var main_caregiver = $('select#id_main_caregiver').val();
    var source_of_identification = $('select#id_source_of_identification').val();

     // source_of_identification
    $('div#div_id_source_of_identification_specify').addClass('d-none');
    $('#span_source_of_identification_specify').addClass('d-none');

    $('div#div_id_rims_case_number').addClass('d-none');
    $('#span_rims_case_number').addClass('d-none');


    if(source_of_identification == 'Other Sources'){
        $('#div_id_source_of_identification_specify').removeClass('d-none');
        $('#span_source_of_identification_specify').removeClass('d-none');
    }

    if(source_of_identification == 'RIMS'){
        $('#div_id_rims_case_number').removeClass('d-none');
        $('#span_rims_case_number').removeClass('d-none');
    }

    $('div.child_id').addClass('d-none');

    // id_student_nationality
    $('div#div_id_other_nationality').addClass('d-none');
    $('#span_other_nationality').addClass('d-none');

    if(nationality == '6'){
        $('#div_id_other_nationality').removeClass('d-none');
        $('#span_other_nationality').removeClass('d-none');
    }

    // have_children
    $('div#div_id_student_number_children').addClass('d-none');
    $('#span_student_number_children').addClass('d-none');
    if(have_children =='1'){
        $('div#div_id_student_number_children').removeClass('d-none');
        $('#span_student_number_children').removeClass('d-none');
    }else{
        $('#id_student_number_children').val('');
    }

    // have_labour_single_selection
     $('#labour_details_1').addClass('d-none');
     $('#labour_details_2').addClass('d-none');
    if(have_labour != 'no'){
        $('#labour_details_1').removeClass('d-none');
        $('#labour_details_2').removeClass('d-none');
    }
    else
    {
        $('#id_labours_single_selection').val('')
        $('#id_labours_other_specify').val('')
        $('#id_labour_hours').val('')
        $('#id_labour_weekly_income').val('')

    }

     // labour_selection
    $('div#div_id_labours_other_specify').addClass('d-none');
    $('#span_labours_other_specify').addClass('d-none');
    if(labour_selection =='other_many_other'){
        $('div#div_id_labours_other_specify').removeClass('d-none');
        $('#span_labours_other_specify').removeClass('d-none');
    }
    else
    {
        $('#id_labours_other_specify').val('');
    }

//    1	"UNHCR Registered"
//    2	"UNHCR Recorded"
//    3	"Syrian national ID"
//    4	"Palestinian national ID"
//    5	"Lebanese national ID"
//    6	"Other nationality"
//    7	"Child have no ID"
    $('div.child_id').addClass('d-none');
    if(id_type == 1){
        $('div.child_id1').removeClass('d-none');
    }

    if(id_type == 2){
        $('div.child_id2').removeClass('d-none');
    }

    if(id_type == 5){
        $('div.child_id3').removeClass('d-none');
    }

    if(id_type == 3){
        $('div.child_id4').removeClass('d-none');
    }

    if(id_type == 4){
        $('div.child_id5').removeClass('d-none');
    }

    if(id_type == 6){
        $('div.child_id6').removeClass('d-none');
    }


    if(main_caregiver == 'other'){
        $('div#div_id_other_caregiver_relationship').removeClass('d-none');
        $('#span_other_caregiver_relationship').removeClass('d-none');
    }
    else {
        $('div#div_id_other_caregiver_relationship').addClass('d-none');
        $('#span_other_caregiver_relationship').addClass('d-none');
        }

}

function marital_status()
{
    var marital_status = $('select#id_child_marital_status').val();

    $('div#div_id_student_have_children').addClass('d-none');
    $('#span_student_have_children').addClass('d-none');
    if(marital_status !='single'){
        $('div#div_id_student_have_children').removeClass('d-none');
        $('#span_student_have_children').removeClass('d-none');
    }
    else{
        $('input:radio[name=student_have_children]').filter('[value=0]').prop('checked', true);
        $('#id_student_number_children').val('');
        $('div#div_id_student_number_children').addClass('d-none');
        $('#span_student_number_children').addClass('d-none');


    }
}

function duplicate_search_student_name()
{
    var student_first_name= $('#id_student_first_name').val();
    var student_father_name= $('#id_student_father_name').val();
    var student_last_name= $('#id_student_last_name').val();
    var student_mother_fullname= $('#student_mother_fullname').val();

    if (student_first_name!='' && student_father_name!='' && student_last_name!=''  && student_mother_fullname!='')
    {
        duplicate_search('student name');
    }

}

function duplicate_search(search_by)
{

    if (isAddPage() ) {
        var search_by = search_by;
        var round = $('select#id_round').val();
        var clm_type = $('#id_clm_type').val();
        var student_id = $('#id_student_id').val();
        var student_first_name = $('#id_student_first_name').val();
        var student_father_name = $('#id_student_father_name').val();
        var student_last_name = $('#id_student_last_name').val();
        var student_mother_fullname = $('#id_student_mother_fullname').val();
        var phone_number = $('#id_phone_number').val();
//        var id_type = $('#id_id_type').val();
        var case_number = $('#id_case_number').val();
        var recorded_number = $('#id_recorded_number').val();
        var parent_syrian_national_number = $('#id_parent_syrian_national_number').val();
        var parent_sop_national_number = $('#id_parent_sop_national_number').val();
        var parent_national_number = $('#id_parent_national_number').val();
        var parent_other_number = $('#id_parent_other_number').val();

        var data = {
            search_by: search_by,
            round_id: round,
            clm_type: clm_type,
            student_id: student_id,
            student_first_name: student_first_name,
            student_father_name: student_father_name,
            student_last_name: student_last_name,
            student_mother_fullname: student_mother_fullname,
            phone_number: phone_number,
//            id_type: id_type,
            id_type: '',
            case_number: case_number,
            recorded_number: recorded_number,
            parent_syrian_national_number: parent_syrian_national_number,
            parent_sop_national_number: parent_sop_national_number,
            parent_national_number: parent_national_number,
            parent_other_number: parent_other_number,
        };
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        $.ajax({
            type: "POST",
            url: '/clm/search-clm-duplicate-registration/',
            data: JSON.stringify(data),
            cache: false,
            async: false,
            headers: requestHeaders,
            dataType: 'json',
            success: function (response) {

                if (response.result != "") {
                    alert("The child already exists with the partner  " + response.result);
                    $(':input[type="submit"][name="save_add_another"]').prop('disabled', true);
                    $(':input[type="submit"][name="save"]').prop('disabled', true);
                    // $('#').addClass('d-none');

                }
                else {
                    $(':input[type="submit"][name="save_add_another"]').prop('disabled', false);
                    $(':input[type="submit"][name="save"]').prop('disabled', false);
                }

                console.log(response);
            },
            error: function (response) {
                console.log(response);
            }


        });


    }

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

function patch_registration(item, callback)
{
    var url = item.attr('data-action');
    var data = {section: '', registered_in_level: ''};

    $.ajax({
        type: "PATCH",
        url: url+'/',
        cache: false,
        data: data,
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

function window_location(value)
{
    console.log('OK');
    $('head').append('<meta http-equiv="refresh" content="0; URL='+value+'" id="redirect"/>');
}

function load_districts(url)
{
    var value = $("#id_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_governorate': value
        },
        success: function (data) {
            $("#id_district").html(data);
        }
    })
}

function load_cadasters(url)
{
    var value = $("#id_district").val();
    $.ajax({
        url: url,
        data: {
            'id_district': value
        },
        success: function (data) {
            $("#id_cadaster").html(data);
        }
    })
}

function load_schools(url)
{
    var value = $("#id_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_governorate': value
        },
        success: function (data) {
            $("#id_school").html(data);
        }
    })
}


