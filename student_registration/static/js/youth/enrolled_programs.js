

$(document).ready(function() {
    reorganizeForm();

    if($(document).find('#id_dropout_date').length == 1) {
        $('#id_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_registration_date').length == 1) {
        $('#id_registration_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    if($(document).find('#id_completion_date').length == 1) {
        $('#id_completion_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_education_status', function(){
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



function load_program_document(url)
{
    var value = $("#id_donor").val();
    $.ajax({
        url: url,
        data: {
            'id_donor': value
        },
        success: function (data) {
            $("#id_program_document").html(data);
        }
    })
}

function load_master_program(url)
{
    var value = $("#id_program_document").val();
    $.ajax({
        url: url,
        data: {
            'id_program_document': value
        },
        success: function (data) {
            $("#id_master_program").html(data);
        }
    })
}

function load_sub_program(url)
{
    var value = $("#id_master_program").val();
    $.ajax({
        url: url,
        data: {
            'id_master_program': value
        },
        success: function (data) {
            $("#id_sub_program").html(data);
        }
    })
}


function urlParam(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results && results.length){
        return results[1] || 0;
    }
    return 0;
}
