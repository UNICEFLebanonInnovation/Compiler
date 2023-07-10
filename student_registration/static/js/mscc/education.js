

$(document).ready(function() {
    reorganizeForm();

    if($(document).find('#id_dropout_date').length == 1) {
        $('#id_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_registration_date').length == 1) {
        $('#id_registration_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', '#id_education_status', function(){
        reorganizeForm();
    });

});

function reorganizeForm()
{
//    Education Status
   var education_status = $('select#id_education_status').val();

    $('div#div_id_dropout_date').addClass('d-none');
    $('#span_dropout_date').addClass('d-none');

    if(education_status == 'Currently registered in Formal Education school but not attending'){
        $('#div_id_dropout_date').removeClass('d-none');
        $('#span_dropout_date').removeClass('d-none');
        $('#id_dropout_date').addClass('error-field');
    }
    else
    {
        $('div#div_id_dropout_date').addClass('d-none');
        $('#id_dropout_date').removeClass('error-field');
        $('#id_dropout_date').val('');
    }
}

