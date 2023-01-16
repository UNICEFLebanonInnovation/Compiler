

$(document).ready(function(){
    reorganizeForm();

    $(document).on('change', 'select#id_referred_service' , function(){
       reorganizeForm();
    });
});


function reorganizeForm()
{
    var is_cbece = $('#id_is_cbece').val();
    if (is_cbece == 'Yes'){
        $('div#div_id_referred_formal_education').removeClass('d-none');
//        $('#id_referred_formal_education').addClass('error-field');

        $('div#div_id_referred_school').removeClass('d-none');
//        $('#id_referred_school').addClass('error-field');
    }
    else{
        $('#id_referred_formal_education').val('');
        $('div#div_id_referred_formal_education').addClass('d-none');
//        $('#id_referred_formal_education').removeClass('error-field');

        $('#id_referred_school').val('');
        $('div#div_id_referred_school').addClass('d-none');
//        $('#id_referred_school').removeClass('error-field');
    }

    var referred_service = $('select#id_referred_service').val();
    if(referred_service == 'Other'){
        $('div#div_id_referred_service_other').removeClass('d-none');
        $('#id_referred_service_other').addClass('error-field');
    }
    else{
        $('#id_barriers_other').val('');
        $('div#div_id_referred_service_other').addClass('d-none');
        $('#id_referred_service_other').removeClass('error-field');
    }
  }

