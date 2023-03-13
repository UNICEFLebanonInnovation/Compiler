

$(document).ready(function(){

//    age_questions();
    reorganizeForm();
    $(document).on('change', 'select#id_baby_breastfed, select#id_eat_solid_food' , function(){
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

 }

