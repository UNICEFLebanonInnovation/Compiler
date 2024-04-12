

$(document).ready(function(){
    reorganizeForm();

    $(document).on('change', 'select#id_referred_service' , function(){
       reorganizeForm();
    });
    $(document).on('change', 'select#id_referred_formal_education' , function(){
       reorganizeForm();
    });

});


function reorganizeForm()
{
    var referred_service = $('select#id_referred_service').val();
    if(referred_service == 'Other'){
        $('div#div_id_referred_service_other').removeClass('d-none');
        if ($('#id_referred_service_other').val()== null || $('#id_referred_service_other').val()=='')
        {
        $('#id_referred_service_other').addClass('error-field');
        }
    }
    else{
        $('#id_barriers_other').val('');
        $('div#div_id_referred_service_other').addClass('d-none');
        $('#id_referred_service_other').removeClass('error-field');
    }

    var referred_formal_education = $('select#id_referred_formal_education').val();
    if(referred_formal_education == 'Yes'){
        $('div#div_id_referred_school').removeClass('d-none');
        if ($('#id_referred_school').val()== null || $('#id_referred_school').val()=='')
        {
        $('#id_referred_school').addClass('error-field');
        }
    }
    else{
        $('#id_referred_school').val('');
        $('div#div_id_referred_school').addClass('d-none');
        $('#id_referred_school').removeClass('error-field');
    }
  }

