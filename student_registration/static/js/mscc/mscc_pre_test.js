

$(document).ready(function(){

    reorganizeForm_post_assessment();

    if($(document).find('#id_adolescent_dropout_date').length == 1) {
        $('#id_adolescent_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_attended_arabic, select#id_attended_foreign_language,  select#id_attended_math', function(){
       reorganizeForm_post_assessment();
    });

});


function reorganizeForm_post_assessment()
{
    var attended_arabic = $('select#id_attended_arabic').val();
    var attended_foreign_language = $('select#id_attended_foreign_language').val();
    var attended_math = $('select#id_attended_math').val();

    $('div#div_id_arabic').addClass('d-none');
    $('#span_arabic').addClass('d-none');
    $('div#div_id_modality_arabic').addClass('d-none');
    $('#span_modality_arabic').addClass('d-none');

    $('div#div_id_foreign_language').addClass('d-none');
    $('#span_foreign_language').addClass('d-none');
    $('div#div_id_modality_foreign_language').addClass('d-none');
    $('#span_modality_foreign_language').addClass('d-none');

    $('div#div_id_math').addClass('d-none');
    $('#span_math').addClass('d-none');
    $('div#div_id_modality_math').addClass('d-none');
    $('#span_modality_math').addClass('d-none');



    // attended_arabic
    if(attended_arabic == 'yes'){
        $('div#div_id_arabic').removeClass('d-none');
        $('#span_arabic').removeClass('d-none');
        $('div#div_id_modality_arabic').removeClass('d-none');
        $('#span_modality_arabic').removeClass('d-none');

    }
    else{
        $('#id_arabic').val('');
        $('select#id_modality_arabic').val("");

    }

    // attended_english
    if(attended_foreign_language == 'yes'){
        $('div#div_id_foreign_language').removeClass('d-none');
        $('#span_foreign_language').removeClass('d-none');
        $('div#div_id_modality_foreign_language').removeClass('d-none');
        $('#span_modality_foreign_language').removeClass('d-none');

    }
    else{
        $('#id_foreign_language').val('');
        $('select#id_modality_foreign_language').val("");
    }
    // attended_math
    if(attended_math == 'yes'){
        $('div#div_id_math').removeClass('d-none');
        $('#span_math').removeClass('d-none');
        $('div#div_id_modality_math').removeClass('d-none');
        $('#span_modality_math').removeClass('d-none');
    }
    else{
        $('#id_math').val('');
        $('select#id_modality_math').val("");
    }

  }

