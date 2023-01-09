
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

    $(data.result).each(function(i, item) {
        console.log(item);
        $('#id_child_first_name').val(item.first_name);
        $('#id_child_father_name').val(item.outreach_caregiver__father_name);
        $('#id_child_last_name').val(item.outreach_caregiver__last_name);
        $('#id_child_mother_fullname').val(item.outreach_caregiver__mother_full_name);
        if (item.date_of_birth){
            dt_string = item.date_of_birth
            var dt = new Date(dt_string);
            $('select#id_child_birthday_year').val(dt.getFullYear())
            $('select#id_child_birthday_month').val(dt.getMonth())
            $('select#id_child_birthday_day').val(dt.getDate())
        }
        $('select#id_gender').val(item.gender)
        var nationality_str = item.nationality
        var nationality_id= get_nationality_id(nationality_str)
        $('select#id_child_nationality').val(nationality_id)

        $('#id_child_nationality_other').val(item.nationality_other);
        $('#id_child_address').val(item.outreach_caregiver__address);

        var disability = item.disability
        if (disability == 'no'){ $('select#id_child_disability').val(1)}
        else if(disability == 'difficulty_seeing'){ $('select#id_child_disability').val(6)}
        else if(disability == 'difficulty_interacting_with_others'){ $('select#id_child_disability').val(9)}
        else if(disability == 'difficulty_speaking'){ $('select#id_child_disability').val(5)}
        else if(disability == 'intellectual_disability'){ $('select#id_child_disability').val(10)}
        else if(disability == 'difficulty_hearing'){ $('select#id_child_disability').val(3)}
        else if(disability == 'learning_difficulties'){ $('select#id_child_disability').val(8)}
        else if(disability == 'difficulty_walking_or_moving_hands'){ $('select#id_child_disability').val(4)}
        else if(disability == 'Other'){ $('select#id_child_disability').val(2)}

        $('#id_disability_other').val(item.disability_other);
        $('#id_child_marital_status').val(Uppercase(item.family_status));

        var main_caregiver_nationality_str = item.outreach_caregiver__caregiver_nationality
        var main_caregiver_nationality_id= get_nationality_id(main_caregiver_nationality_str)
        $('select#id_main_caregiver_nationality').val(main_caregiver_nationality_id)

        $('#id_main_caregiver_nationality_other').val(item.outreach_caregiver__main_caregiver_nationality_other);
        $('select#id_have_labour').val(Uppercase(item.working_status))

        var labour_type=item.work_type
        if (labour_type == 'manufacturing_producing'){$('select#id_labour_type').val('Manufacturing')}
        else if ( labour_type == 'garage_mechanics_workshop'){$('select#id_labour_type').val('')}
        else if ( labour_type == 'construction_site'){$('select#id_labour_type').val('Building')}
        else if ( labour_type == 'shop_restaurant_bakery_barber'){$('select#id_labour_type').val('Retail / Store')}
        else if ( labour_type == 'street_connected_work__begging__vending_'){$('select#id_labour_type').val('Begging')}
        else if ( labour_type == 'agriculture_animal_herding'){$('select#id_labour_type').val('Agriculture')}
        else if ( labour_type == 'others'){$('select#id_labour_type').val('Other services')}

        $('#id_labour_type_specify').val(item.work_type_other);
        $('#id_first_phone_number').val(item.outreach_caregiver__primary_phone);
        $('#id_first_phone_number_confirm').val(item.outreach_caregiver__primary_phone);
        $('#id_second_phone_number').val(item.outreach_caregiver__secondary_phone);
        $('#id_second_phone_number_confirm').val(item.outreach_caregiver__secondary_phone);

        var main_caregiver = item.outreach_caregiver__main_caregiver
        if (main_caregiver == 'الاب'){
            $('select#id_main_caregiver').val('Father')
            $('#id_caregiver_first_name').val(item.outreach_caregiver__father_name)
            $('#id_caregiver_last_name').val(item.outreach_caregiver__last_name)
            }
        else{
            if (main_caregiver == 'الام'){
                $('select#id_main_caregiver').val('Mother')
            }
            else if (main_caregiver == 'اخر'){
                $('select#id_main_caregiver').val('Other')
            }
            $('#id_caregiver_first_name').val(item.outreach_caregiver__caregiver_first_name)
            $('#id_caregiver_last_name').val(item.outreach_caregiver__caregiver_last_name)
            }

        $('#id_caregiver_middle_name').val(item.outreach_caregiver__caregiver_father_name)
        $('#id_caregiver_mother_name').val(item.outreach_caregiver__caregiver_mother_name)

    $('div.child_id').addClass('d-none');

        var id_type = item.outreach_caregiver__id_type
        if (id_type == 'unhcr_registered'){
            $('select#id_id_type').val(1)
            $('div.child_id1').removeClass('d-none');
            $('#id_case_number').val(item.outreach_caregiver__unhcr_case_number)
            $('#id_case_number_confirm').val(item.outreach_caregiver__unhcr_case_number)
            $('#id_parent_individual_case_number').val(item.outreach_caregiver__caregiver_unhcr_id)
            $('#id_parent_individual_case_number_confirm').val(item.outreach_caregiver__caregiver_unhcr_id)
            $('#id_individual_case_number').val(item.child_unhcr_number)
            $('#id_individual_case_number_confirm').val(item.child_unhcr_number)
            }
        else if(id_type == 'unhcr_recorded'){
            $('select#id_id_type').val(2)
            $('div.child_id2').removeClass('d-none');
            $('#id_recorded_number').val(item.outreach_caregiver__unhcr_barcode)
            $('#id_recorded_number_confirm').val(item.outreach_caregiver__unhcr_barcode)
            }
        else if( id_type == 'syrian_id'){
            $('select#id_id_type').val(3)
            $('div.child_id4').removeClass('d-none');
            $('#id_parent_syrian_national_number').val(item.outreach_caregiver__caregiver_personal_id)
            $('#id_parent_syrian_national_number_confirm').val(item.outreach_caregiver__caregiver_personal_id)
            $('#id_syrian_national_number').val(item.child_personal_id)
            $('#id_syrian_national_number_confirm').val(item.child_personal_id)
            }
        else if( id_type == 'palestinian_id'){
            $('select#id_id_type').val(4)
            $('div.child_id5').removeClass('d-none');
            $('#id_sop_parent_national_number').val(item.outreach_caregiver__caregiver_personal_id)
            $('#id_sop_parent_national_number_confirm').val(item.outreach_caregiver__caregiver_personal_id)
            $('#id_sop_national_number').val(item.child_personal_id)
            $('#id_sop_national_number_confirm').val(item.child_personal_id)
            }
        else if( id_type == 'lebanese_id'){
            $('select#id_id_type').val(5)
            $('div.child_id3').removeClass('d-none');
            $('#id_parent_national_number').val(item.outreach_caregiver__caregiver_personal_id)
            $('#id_parent_national_number_confirm').val(item.outreach_caregiver__caregiver_personal_id)
            $('#id_national_number').val(item.child_personal_id)
            $('#id_national_number_confirm').val(item.child_personal_id)
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

//    Main Caregiver
    var main_caregiver = $('select#id_main_caregiver').val();
    if(main_caregiver == 'other'){
        $('div#div_id_other_caregiver_relationship').removeClass('d-none');
        $('#span_other_caregiver_relationship').removeClass('d-none');
    }
    else {
        $('div#div_id_other_caregiver_relationship').addClass('d-none');
        $('#span_other_caregiver_relationship').addClass('d-none');
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
        $('#labour_details_1').removeClass('d-none');
        $('#labour_details_2').removeClass('d-none');
    }
    else
    {
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
