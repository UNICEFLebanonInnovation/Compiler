

$(document).ready(function(){

    age_questions();
    reorganizeForm();
    $(document).on('change', 'select#id_baby_breastfed, select#id_eat_solid_food' , function(){
       reorganizeForm();
    });
});

function age_questions() {
    var age = $('#id_child_age').val();
    if(age<=5)
    {
        $('div#div_id_respond_stressful_events').addClass('d-none');
        $('div#div_id_baby_breastfed').removeClass('d-none');
        $('div#div_id_eat_solid_food').removeClass('d-none');
        $('div#div_id_age_eat_solid_food').removeClass('d-none');
        $('div#div_id_immunization_record_screened').removeClass('d-none');
        $('div#div_id_vaccine_missing').removeClass('d-none');
        $('div#div_id_muac_malnutrition_screening').removeClass('d-none');
        $('div#div_id_positive_parenting').removeClass('d-none');
        $('div#div_id_development_delays_identified').removeClass('d-none');
        $('#id_respond_stressful_events').val('');
        $('div#div_id_respond_stressful_events').addClass('d-none');
        $('#id_physical_activity').val('');
        $('div#div_id_physical_activity').addClass('d-none');
        $('#id_accessing_reproductive_health').val('');
        $('div#div_id_accessing_reproductive_health').addClass('d-none');
    }
    else if(age>=6 && age<=18){
        $('div#div_id_baby_breastfed').addClass('d-none');
        $('#id_baby_breastfed').val('');
        $('#id_infant_exclusively_breastfed').val('');
        $('div#div_id_infant_exclusively_breastfed').addClass('d-none');
        $('div#div_id_eat_solid_food').addClass('d-none');
        $('#id_eat_solid_food').val('');
        $('div#div_id_age_eat_solid_food').addClass('d-none');
        $('#id_age_eat_solid_food').val('');
        $('div#div_id_immunization_record_screened').addClass('d-none');
        $('#id_immunization_record_screened').val('');
        $('div#div_id_vaccine_missing').addClass('d-none');
        $('#id_vaccine_missing').val('');
        $('div#div_id_muac_malnutrition_screening').addClass('d-none');
        $('#id_muac_malnutrition_screening').val('');
        $('div#div_id_positive_parenting').addClass('d-none');
        $('#id_positive_parenting').val('');
        $('div#div_id_development_delays_identified').addClass('d-none');
        $('#id_development_delays_identified').val('');
        $('div#div_id_respond_stressful_events').removeClass('d-none');
        $('div#div_id_physical_activity').removeClass('d-none');
        $('div#div_id_accessing_reproductive_health').removeClass('d-none');
    }
}

function reorganizeForm() {
    var age = $('#id_child_age').val();
    if(age<=5){
        var baby_breastfed = $('select#id_baby_breastfed').val();
        if(baby_breastfed == 'Yes'){
            $('div#div_id_infant_exclusively_breastfed').removeClass('d-none');
            $('#id_infant_exclusively_breastfed').addClass('error-field');
        }
        else{
            $('#id_infant_exclusively_breastfed').val('');
            $('div#div_id_infant_exclusively_breastfed').addClass('d-none');
            $('#id_infant_exclusively_breastfed').removeClass('error-field');
        }
        var eat_solid_food = $('select#id_eat_solid_food').val();
        if(eat_solid_food == 'Yes'){
            $('div#div_id_age_eat_solid_food').removeClass('d-none');
            $('#id_age_eat_solid_food').addClass('error-field');
        }
        else{
            $('#id_age_eat_solid_food').val('');
            $('div#div_id_age_eat_solid_food').addClass('d-none');
            $('#id_age_eat_solid_food').removeClass('error-field');
        }

  }

 }

