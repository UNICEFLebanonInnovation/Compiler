

$(document).ready(function(){

    age_questions();
    reorganizeForm();
    $(document).on('change', 'select#id_baby_breastfed, select#id_eat_solid_food' , function(){
       reorganizeForm();
    });
});

function age_questions() {
    var age = $('#id_child_age').val();

    if(age<=2)
    {
        $('div#div_id_eating_minimum_meals').addClass('d-none');
        $('div#div_id_positive_parenting').addClass('d-none');
        $('div#div_id_respond_stressful_events').addClass('d-none');

        $('div#div_id_baby_breastfed').removeClass('d-none');
        $('div#div_id_infant_exclusively_breastfed').removeClass('d-none');
        $('div#div_id_eat_solid_food').removeClass('d-none');
        $('div#div_id_age_eat_solid_food').removeClass('d-none');
        $('div#div_id_development_delays_identified').removeClass('d-none');
    }
    else if(age>=3 && age<=5){
        $('div#div_id_baby_breastfed').addClass('d-none');
        $('div#div_id_infant_exclusively_breastfed').addClass('d-none');
        $('div#div_id_eat_solid_food').addClass('d-none');
        $('div#div_id_age_eat_solid_food').addClass('d-none');
        $('div#div_id_respond_stressful_events').addClass('d-none');

        $('div#div_id_development_delays_identified').removeClass('d-none');
        $('div#div_id_eating_minimum_meals').removeClass('d-none');
        $('div#div_id_positive_parenting').removeClass('d-none');

    }
    else
    {
        $('div#div_id_baby_breastfed').addClass('d-none');

        $('div#div_id_infant_exclusively_breastfed').addClass('d-none');
        $('div#div_id_eat_solid_food').addClass('d-none');
        $('div#div_id_age_eat_solid_food').addClass('d-none');
        $('div#div_id_development_delays_identified').addClass('d-none')
        $('div#div_id_positive_parenting').addClass('d-none');

        $('div#div_id_eating_minimum_meals').removeClass('d-none');
        $('div#div_id_respond_stressful_events').removeClass('d-none');

    }
}

function reorganizeForm() {
    var age = $('#id_child_age').val();
    if(age<=2){
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

