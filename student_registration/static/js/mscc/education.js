

$(document).ready(function() {
    reorganizeForm();

    if($(document).find('#id_dropout_date').length == 1) {
        $('#id_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_registration_date').length == 1) {
        $('#id_registration_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', '#id_dropout_program', function(){
        reorganizeForm();
    });

});

// todo do we still need this function?
function reorganizeForm()
{
//    Dropout Program
   var dropout_program = $('select#id_dropout_program').val();
    if(dropout_program == 'Other'){
        $('#div_id_dropout_program_specify').removeClass('d-none');
        if ($('#id_dropout_program_specify').val()== null || $('#id_dropout_program_specify').val()=='')
        {
            $('#id_dropout_program_specify').addClass('error-field');
        }

    }
    else
    {
        $('div#div_id_dropout_program_specify').addClass('d-none');
        $('#id_dropout_program_specify').removeClass('error-field');
        $('#id_dropout_program_specify').val('');
    }
}

