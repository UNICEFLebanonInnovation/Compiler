

$(document).ready(function(){
       reorganizeForm();
       reorganizeTarlForm();

    $(document).on('change', ' select#id_post_test_done' , function(){
       reorganizeForm();
    });
    $(document).on('change', 'select#id_test_taken' , function(){
       reorganizeTarlForm();
    });
    $(document).on('change', 'select#id_math_level_reached' , function(){
       reorganizeTarlForm();
    });


});


function reorganizeForm()
{
    var post_test_done = $('select#id_post_test_done').val();


    if(post_test_done == 'Yes'){
        $('.grade-field').removeClass('d-none');
    }else{
        $('.grade-field').addClass('d-none');
        $('.grade-field').find('input').val(0);
    }
}

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
        wordProblemFields.find('input').prop('required', true);
    }else{
        wordProblemFields.addClass('d-none');
        wordProblemFields.find('input').prop('required', false).val('');
    }
}
