

$(document).ready(function(){
    reorganizeTarlForm();
    $(document).on('change', 'select#id_test_taken' , function(){
       reorganizeTarlForm();
    });
    $(document).on('change', 'select#id_math_level_reached' , function(){
       reorganizeTarlForm();
    });


});


function reorganizeTarlForm()
{
    var test_taken = $('select#id_test_taken').val();
    var math_level = $('select#id_math_level_reached').val();
    var tarlFields = $('.tarl-dependent');
    var wordProblemFields = $('.tarl-word-problem');

    if (!tarlFields.length) {
        return;
    }

    if (test_taken == 'Yes'){
        tarlFields.removeClass('d-none');
        tarlFields.find('select, input').prop('required', true);
    }else{
        tarlFields.addClass('d-none');
        tarlFields.find('select, input').prop('required', false).val('');
    }


    if (test_taken == 'Yes' && (math_level == 'Subtraction' || math_level == 'Division')){
        wordProblemFields.removeClass('d-none');
        wordProblemFields.find('select, input').prop('required', true);
    }else{
        wordProblemFields.addClass('d-none');
        wordProblemFields.find('select, input').prop('required', false);
    }
}
