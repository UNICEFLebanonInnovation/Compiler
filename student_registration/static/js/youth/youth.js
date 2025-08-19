
var english_fields = "#id_adolescent_first_name, #id_adolescent_father_name, #id_adolescent_last_name, #id_adolescent_mother_fullname, " +
    " #id_caregiver_mother_name, #id_caregiver_last_name, #id_caregiver_middle_name, #id_caregiver_first_name";

$(document).ready(function() {


    $('.show-progarmme-details').click(function(e){
        e.preventDefault();

        $('#programme-body-content').empty("");
        $('#programme-body-content').append("Loading...");
        $('#programmeModal').modal('show');

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#programme-body-content').empty("");
                $('#programme-body-content').append(response);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    $('.show-view-all').click(function(e){
        e.preventDefault();

        $('#programme-body-content').empty("");
        $('#programme-body-content').append("Loading...");
        $('#programmeModal').modal('show');

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#programme-body-content').empty("");
                $('#programme-body-content').append(response);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    $('.attendance_month').click(function(e){
        e.preventDefault();

        $('.app-drawer-overlay').removeClass('d-none');

        $.ajax({
            type: "GET",
            url: $(this).attr('data-href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#tab-faq-1').empty("");
                $('#tab-faq-1').append(response);
                $('.app-drawer-overlay').addClass('d-none');
            },
            error: function(response) {
                console.log(response);
                $('.app-drawer-overlay').addClass('d-none');
            }
        });
    });

    $(document).on('click', '.show-child-details', function(e){
        e.preventDefault();

        $('#child-content').empty("");
        $('#child-content').append("Loading...");
        $('#childModal').modal('show');

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#child-content').empty("");
                $('#child-content').append(response);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    $(document).on('change', 'select#id_source_of_identification', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_adolescent_gender', function(){
        reorganizeForm();
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
//        Caregiver has no ID = 7
        if($(this).val() != 7){
            return true;
        }

    });
    reorganizeForm();

    $(document).on('change', 'select#id_adolescent_have_children, select#id_adolescent_nationality, select#id_main_caregiver, select#id_main_caregiver_nationality, select#id_have_labour, select#id_labour_type, select#id_adolescent_have_sibling', function(){
         reorganizeForm();
    });
    $(document).on('change', 'select#id_student_nationality, select#id_have_labour_single_selection, select#id_labour_weekly_income', function(){
        reorganizeForm();
    });

    $(document).on('change', 'select#id_adolescent_first_name, select#id_adolescent_father_name, select#id_adolescent_last_name, select#id_adolescent_birthday_year, select#id_adolescent_birthday_month, select#id_adolescent_birthday_day', function(){
        $('#search_loader').removeClass('hidden');
        $('#nfe_search_loader').removeClass('hidden');

        var first_name = $('#id_adolescent_first_name').val();
        var father_name = $('#id_adolescent_father_name').val();
        var last_name = $('#id_adolescent_last_name').val();
        if ( first_name!= '' && father_name!= '' && last_name!= '')
        {
            outreach_adolescent_search();
            old_adolescent_search();
            adolescent_duplication_check();
        }
    });

    $(document).on('change', 'select#id_main_caregiver', function(){
        var main_caregiver = $('select#id_main_caregiver').val();
        if(main_caregiver == 'Father'){
            var father_name = $('#id_adolescent_father_name').val();
            var last_name = $('#id_adolescent_last_name').val();
            $('#id_caregiver_first_name').val(father_name);
            $('#id_caregiver_last_name').val(last_name);
        }
        else {
            $('#id_caregiver_first_name').val('');
            $('#id_caregiver_last_name').val('');
        }
    });

    $(document).on('blur', english_fields, function(){
        checkEnglishOnly($(this));
    });

    $(document).on('click', '#next-page', function(e){
        e.preventDefault();
        $(this).removeClass('error-field');
        var error_fields = false;
        $('input, select').filter('[required]:visible').each(function(){
            if($(this).val() == null || $(this).val() == ''){
                $(this).addClass('error-field');
                error_fields = true;
            }
        });
        if(typeof validateMainForm === 'function' && !validateMainForm(false)){
            error_fields = true;
        }
        if(!error_fields){
            $('#next-btn22').trigger('click');
            $(this).removeClass('error-field');
         }else{
            $('#formErrorModal').modal('show');
         }
    });


});

function load_districts(url)
{
    var value = $("#id_adolescent_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_adolescent_governorate': value
        },
        success: function (data) {
            $("#id_adolescent_district").html(data);
        }
    })
}

function load_cadasters(url)
{
    var value = $("#id_adolescent_district").val();
    $.ajax({
        url: url,
        data: {
            'id_adolescent_district': value
        },
        success: function (data) {
            $("#id_adolescent_cadaster").html(data);
        }
    })
}

function reorganizeForm()
{
//  adolescent_gender
    var adolescent_gender = $('select#id_adolescent_gender').val();

    if(adolescent_gender =='Female'){
        $("#id_adolescent_have_children").append('<option value="Child pregnant or expecting children">Child pregnant or expecting children</option>');
    }
    else
     {
        $("#id_adolescent_have_children option[value='Child pregnant or expecting children']").remove();
    }

//    Child Nationality
    var child_nationality = $('select#id_adolescent_nationality').val();
    $('div#div_id_adolescent_nationality_other').addClass('d-none');

    if(child_nationality == 6){
        $('#div_id_adolescent_nationality_other').removeClass('d-none');
    }
    else{
        $('#id_adolescent_nationality_other').val('');
    }


//   Source of Identification
    var source_of_identification = $('select#id_source_of_identification').val();
    $('div#div_id_source_of_identification_specify').addClass('d-none');
    $('#span_source_of_identification_specify').addClass('d-none');

    if(source_of_identification == 'Other Sources'){
        $('#div_id_source_of_identification_specify').removeClass('d-none');
        $('#span_source_of_identification_specify').removeClass('d-none');
    }

//    Main Caregiver
    var main_caregiver = $('select#id_main_caregiver').val();
    $('div#div_id_main_caregiver_other').addClass('d-none');
    if(main_caregiver == 'Other'){
        $('#div_id_main_caregiver_other').removeClass('d-none');
    }
    else
    {
        $('#id_main_caregiver_other').val('');
    }

//    Main Caregiver Nationality
    var main_caregiver_nationality = $('select#id_main_caregiver_nationality').val();
    $('div#div_id_main_caregiver_nationality_other').addClass('d-none');
    if(main_caregiver_nationality == 6){
        $('#div_id_main_caregiver_nationality_other').removeClass('d-none');
    }
    else
    {
        $('#id_main_caregiver_nationality_other').val('');
    }


//    ID Type
    var id_type = $('select#id_id_type').val();

/*  1	"UNHCR Registered"
    2	"UNHCR Recorded"
    3	"Syrian national ID"
    4	"Palestinian national ID"
    5	"Lebanese national ID"
    6	"Other nationality"
    7	"Caregiver has no ID" */

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

    if(id_type == 9){
        $('div.child_id7').removeClass('d-none');
    }
    if(id_type == 12){
        $('div.child_id8').removeClass('d-none');
    }

    //  Labour
    var have_labour = $('select#id_have_labour').val();
    if(have_labour == '' || have_labour == 'No'){
        $('div#div_id_labour_type').addClass('d-none');
        $('#labour_details_1').addClass('d-none');
        $('#labour_details_2').addClass('d-none');
        $('#labour_details_3').addClass('d-none');
        $('#id_labour_type').val('')
        $('#id_labour_type_specify').val('')
        $('#id_labour_hours').val('')
        $('#id_labour_weekly_income').val('')
        $('#labour_condition').val('')
    }
    else
    {
        $('div#div_id_labour_type').removeClass('d-none');
        $('#labour_details_1').removeClass('d-none');
        $('#labour_details_2').removeClass('d-none');
        $('#labour_details_3').removeClass('d-none');
    }

    var labour_type = $('select#id_labour_type').val();
    if(labour_type == 'Other services'){
        $('div#div_id_labour_type_specify').removeClass('d-none');
    }
    else
    {
        $('div#div_id_labour_type_specify').addClass('d-none');
        $('#id_labour_type_specify').val('');
    }
}
