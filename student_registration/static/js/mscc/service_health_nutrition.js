

$(document).ready(function(){

//    age_questions();
    reorganizeForm();
     if($(document).find('#id_counselling_date').length == 1) {
        $('#id_counselling_date').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_next_counselling_date').length == 1) {
        $('#id_next_counselling_date').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_ecd_counselling_date').length == 1) {
        $('#id_ecd_counselling_date').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_next_ecd_counselling_date').length == 1) {
        $('#id_next_ecd_counselling_date').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_health_nutrition_session_date').length == 1) {
        $('#id_health_nutrition_session_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_baby_breastfed, select#id_eat_solid_food, select#id_caregiver_counselling, select#id_caregiver_ecd_counselling, select#id_child_screened_malnutrition, select#id_child_immunization_screened, select#id_attended_health_nutrition_session' , function(){
       reorganizeForm();
    });
});


function reorganizeForm() {
    var age = $('#id_child_age').val();

    if(age<=5){
        var baby_breastfed = $('select#id_baby_breastfed').val();
        if(baby_breastfed == 'Yes'){
            $('div#div_id_infant_exclusively_breastfed').removeClass('d-none');
            if ($('#id_infant_exclusively_breastfed').val()== null || $('#id_infant_exclusively_breastfed').val()=='')
            {
                $('#id_infant_exclusively_breastfed').addClass('error-field');
            }
        }
        else{
            $('#id_infant_exclusively_breastfed').val('');
            $('div#div_id_infant_exclusively_breastfed').addClass('d-none');
            $('#id_infant_exclusively_breastfed').removeClass('error-field');
        }
        var eat_solid_food = $('select#id_eat_solid_food').val();
        if(eat_solid_food == 'Yes'){
            $('div#div_id_age_eat_solid_food').removeClass('d-none');
            if ($('#id_age_eat_solid_food').val()== null || $('#id_age_eat_solid_food').val()=='')
            {
                $('#id_age_eat_solid_food').addClass('error-field');
            }
        }
        else{
            $('#id_age_eat_solid_food').val('');
            $('div#div_id_age_eat_solid_food').addClass('d-none');
            $('#id_age_eat_solid_food').removeClass('error-field');
        }

  }

//     caregiver_counselling
        var caregiver_counselling = $('select#id_caregiver_counselling').val();
        if(caregiver_counselling == 'Yes'){
            $('div#div_id_counselling_date').removeClass('d-none');
            if ($('#id_counselling_date').val()== null || $('#id_counselling_date').val()=='')
            {
                $('#id_counselling_date').addClass('error-field');
            }
            $('div#div_id_next_counselling_date').removeClass('d-none');
            if ($('#id_next_counselling_date').val()== null || $('#id_next_counselling_date').val()=='')
            {
                $('#id_next_counselling_date').addClass('error-field');
            }
        }
        else{
            $('#id_counselling_date').val('');
            $('div#div_id_counselling_date').addClass('d-none');
            $('#id_counselling_date').removeClass('error-field');
            $('#id_next_counselling_date').val('');
            $('div#div_id_next_counselling_date').addClass('d-none');
            $('#id_next_counselling_date').removeClass('error-field');
        }

        //    caregiver_ecd_counselling
//
//
        var caregiver_ecd_counselling = $('select#id_caregiver_ecd_counselling').val();
        if(caregiver_ecd_counselling == 'Yes'){
            $('div#div_id_ecd_counselling_date').removeClass('d-none');
            if ($('#id_ecd_counselling_date').val()== null || $('#id_ecd_counselling_date').val()=='')
            {
                $('#id_ecd_counselling_date').addClass('error-field');
            }
            $('div#div_id_next_ecd_counselling_date').removeClass('d-none');
            if ($('#id_next_ecd_counselling_date').val()== null || $('#id_next_ecd_counselling_date').val()=='')
            {
                $('#id_next_ecd_counselling_date').addClass('error-field');
            }
        }
        else{
            $('#id_ecd_counselling_date').val('');
            $('div#div_id_ecd_counselling_date').addClass('d-none');
            $('#id_ecd_counselling_date').removeClass('error-field');

            $('#id_next_ecd_counselling_date').val('');
            $('div#div_id_next_ecd_counselling_date').addClass('d-none');
            $('#id_next_ecd_counselling_date').removeClass('error-field');
        }



//    child_screened_malnutrition
        var child_screened_malnutrition = $('select#id_child_screened_malnutrition').val();
        if(child_screened_malnutrition == 'Yes'){
            $('div#div_id_child_malnutrition_screening').removeClass('d-none');
            if ($('#id_child_malnutrition_screening').val()== null || $('#id_child_malnutrition_screening').val()=='')
            {
                $('#id_child_malnutrition_screening').addClass('error-field');
            }
        }
        else{
            $('#id_child_malnutrition_screening').val('');
            $('div#div_id_child_malnutrition_screening').addClass('d-none');
            $('#id_child_malnutrition_screening').removeClass('error-field');
        }

//    child_immunization_screened
        var child_immunization_screened = $('select#id_child_immunization_screened').val();
        if(child_immunization_screened == 'Yes'){
            $('div#div_id_missing_vaccine').removeClass('d-none');
            if ($('#id_missing_vaccine').val()== null || $('#id_missing_vaccine').val()=='')
            {
                $('#id_missing_vaccine').addClass('error-field');
            }
        }
        else{
            $('#id_missing_vaccine').val('');
            $('div#div_id_missing_vaccine').addClass('d-none');
            $('#id_missing_vaccine').removeClass('error-field');
        }


//    health_nutrition_session_title
//    health_nutrition_session_date


//    attended_health_nutrition_session
        var attended_health_nutrition_session = $('select#id_attended_health_nutrition_session').val();
        if(attended_health_nutrition_session == 'Yes'){
            $('div#div_id_health_nutrition_session_title').removeClass('d-none');
            if ($('#id_health_nutrition_session_title').val()== null || $('#id_health_nutrition_session_title').val()=='')
            {
                $('#id_health_nutrition_session_title').addClass('error-field');
            }
            $('div#div_id_health_nutrition_session_date').removeClass('d-none');
            if ($('#id_health_nutrition_session_date').val()== null || $('#id_health_nutrition_session_date').val()=='')
            {
                $('#id_health_nutrition_session_date').addClass('error-field');
            }
        }
        else{
            $('#id_health_nutrition_session_title').val('');
            $('div#div_id_health_nutrition_session_title').addClass('d-none');
            $('#id_health_nutrition_session_title').removeClass('error-field');

            $('#id_health_nutrition_session_date').val('');
            $('div#div_id_health_nutrition_session_date').addClass('d-none');
            $('#id_health_nutrition_session_date').removeClass('error-field');
        }

 }

