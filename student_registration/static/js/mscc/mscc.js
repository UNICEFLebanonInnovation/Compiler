
var arabic_fields = "#id_child_first_name, #id_child_father_name, #id_child_last_name, #id_child_mother_fullname, " +
    " #id_caregiver_mother_name, #id_caregiver_last_name, #id_caregiver_middle_name, #id_caregiver_first_name";
var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(document).ready(function() {

    $(document).on('change', 'select#id_source_of_identification', function(){
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
//        Child have no ID = 7
        if($(this).val() != 7){
            return true;
        }

    });
    reorganizeForm();

    $(document).on('change', 'select#id_child_have_children, select#id_child_nationality, select#id_main_caregiver, select#id_main_caregiver_nationality, select#id_have_labour, select#id_labour_type', function(){
         reorganizeForm();
    });
    $(document).on('change', 'select#id_student_nationality, select#id_have_labour_single_selection, select#id_labour_weekly_income', function(){
        reorganizeForm();
    });

    $(document).on('change', 'input#id_child_first_name, input#id_child_father_name, input#id_child_last_name', function () {
        mscc_child_search();
    });

    $(document).on('change', 'select#id_child_birthday_year, select#id_child_birthday_month, select#id_child_birthday_day', function(){
        $('#search_loader').removeClass('hidden');
        mscc_child_search();
    });

    $(document).on('change', 'select#id_main_caregiver', function(){
        var main_caregiver = $('select#id_main_caregiver').val();
        if(main_caregiver == 'Father'){
            var father_name = $('#id_child_father_name').val();
            var last_name = $('#id_child_last_name').val();
            $('#id_caregiver_first_name').val(father_name);
            $('#id_caregiver_last_name').val(last_name);
        }
        else {
            $('#id_caregiver_first_name').val('');
            $('#id_caregiver_last_name').val('');
        }
    });

    $(document).on('blur', arabic_fields, function(){
        checkArabicOnly($(this));
    });


});

function mscc_child_search() {

    if (isAddPage() ) {

        var birthday_year = $('#id_child_birthday_year').val();
        var birthday_month = $('#id_child_birthday_month').val();
        var birthday_day = $('#id_child_birthday_day').val();
        var first_name = $('#id_child_first_name').val();
        var father_name = $('#id_child_father_name').val();
        var last_name = $('#id_child_last_name').val();

        if (birthday_year!='')
        {
            var data = {
                birthday_year: birthday_year,
                birthday_month: birthday_month,
                birthday_day: birthday_day,
                first_name: first_name,
                father_name: father_name,
                last_name: last_name,
            };
            requestHeaders = getHeader();
            requestHeaders["content-type"] = 'application/json';
            $.ajax({
                type: "POST",
                url: '/MSCC/mscc-child-search/',
                data: JSON.stringify(data),
                cache: false,
                async: true,
                headers: requestHeaders,
                dataType: 'json',
                success: function (response) {

                    append_new_result(response);
                },
                error: function (response) {
                    console.log(response);
                }
            });
        }
    }
}

function append_new_result(data)
{

    var child_html = '';
    $('#outreach_search_result').empty();
    $('#search_loader').addClass('hidden');

    $(data.result).each(function(i, item) {
        var full_name = "";
        full_name = full_name.concat(item.first_name, " ", item.outreach_caregiver__father_name, " ", item.outreach_caregiver__last_name);

        var html_line1 = '<div class="vertical-timeline-item vertical-timeline-element"><div><div class="vertical-timeline-element-icon bounce-in"><div class="timeline-icon border-success"><span class="text-success">'+ item.score +'%</span></div></div><div class="vertical-timeline-element-content bounce-in">';
        var html_line2 = '<h4 class="timeline-title text-success"><a href="javascript:get_child_data('+ item.id +');">'+full_name+'</a></h4>';
        var html_line3 = '<p>'+ item.date_of_birth + ' - '+ item.outreach_caregiver__mother_full_name +'</p>';
        var html_line4 = '<p>'+ item.gender + ' - '+ item.nationality +'</p></div></div></div>';

        child_html = html_line1 + html_line2 + html_line3 + html_line4;

        $('#outreach_search_result').append(child_html);
    });
}

function get_child_data(id)
{
    $('#search_loader').removeClass('hidden');

    var data = {
        id: id,
    };
    requestHeaders = getHeader();
    requestHeaders["content-type"] = 'application/json';
    $.ajax({
        type: "POST",
        url: '/MSCC/mscc-outreach-child/',
        data: JSON.stringify(data),
        cache: false,
        async: true,
        headers: requestHeaders,
        dataType: 'json',
        success: function (response) {
            console.log(response);
            fill_outreach_child_data(response);
        },
        error: function (response) {
            console.log(response);
        }
    });
}

function fill_outreach_child_data(data)
{
    $('#search_loader').addClass('hidden');
    $(data).each(function(i, item) {
        console.log(item);
        {
            Object.keys(item).forEach(key => {
                $('#id_'+ key).val(item[key]);
            });
        }
    });
    $('#search_loader').addClass('hidden');
}

function Uppercase(str){
     var str_upper = str.charAt(0).toUpperCase() + str.slice(1);
     return str_upper
}

function get_nationality_id(nationality_str){
        if (nationality_str == 'syrian'){ return 1; }
        else if(nationality_str == 'lebanese'){ return 5;}
        else if(nationality_str == 'palestinian'){ return 4;}
        else if(nationality_str == 'iraqi'){return 2;}
        else if(nationality_str == 'stateless'){return 7;}
        else if(nationality_str == 'other'){return 6;}
}

function isAddPage()
{
    var url_loc = window.location.toString();
    return (url_loc.toLowerCase().search(/^.*\/MSCC\/child-add(\/)?(\?.*)?$/i)>=0);
}

function reorganizeForm()
{
//    Child Nationality
   var child_nationality = $('select#id_child_nationality').val();
    $('div#div_id_child_nationality_other').addClass('d-none');
    if(child_nationality == 6){
        $('#div_id_child_nationality_other').removeClass('d-none');
    }
    else
    {
        $('#id_child_nationality_other').val('');
    }

//    Child have children
    var child_have_children = $('select#id_child_have_children').val();

    if(child_have_children =='Yes'){
        $('div#div_id_child_children_number').removeClass('d-none');
    }
    else{
        $('div#div_id_child_children_number').addClass('d-none');
        $('#id_child_children_number').val('');
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
    7	"Child have no ID" */

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

    //  Labour
    var have_labour = $('select#id_have_labour').val();
    if(have_labour != 'No'){
        $('div#div_id_labour_type').removeClass('d-none');
        $('#labour_details_1').removeClass('d-none');
        $('#labour_details_2').removeClass('d-none');
    }
    else
    {
        $('div#div_id_labour_type').addClass('d-none');
        $('#labour_details_1').addClass('d-none');
        $('#labour_details_2').addClass('d-none');
        $('#id_labour_type').val('')
        $('#id_labour_type_specify').val('')
        $('#id_labour_hours').val('')
        $('#id_labour_weekly_income').val('')
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
