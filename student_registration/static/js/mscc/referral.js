

$(document).ready(function(){
    reorganizeForm();

    if($(document).find('#id_dropout_date').length == 1) {
        $('#id_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }
    $(document).on('change', 'select#id_referred_service' , function(){
       reorganizeForm();
    });
    $(document).on('change', 'select#id_recommended_learning_path' , function(){
       reorganizeForm();
    });
    $(document).on('change', 'select#id_retention_support_enrolled', function(){
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

    var recommended_learning_path = $('select#id_recommended_learning_path').val();
    var progressToFormalEducation = recommended_learning_path == 'Progress to FE';
    var educationProgram = $('#id_education_program').val();
    var programmesWithFormalEducationDetails = [
        'CBECE Level 1',
        'BLN Level 1',
        'BLN Level 2',
        'BLN Level 3',
        'BLN Level 4',
        'BLN Level 5',
        'BLN Level 6',
        'BLN Level 7',
        'BLN Level 8',
        'BLN Level 9'
    ];
    var showFormalEducationDetails = progressToFormalEducation &&
        programmesWithFormalEducationDetails.indexOf(educationProgram) !== -1;

    if(progressToFormalEducation){
        $('#referred-school-fields').removeClass('d-none');
        if ($('#id_referred_school').val()== null || $('#id_referred_school').val()=='')
        {
        $('#id_referred_school').addClass('error-field');
        }
    }
    else{
        $('#id_referred_school').val('');
        $('#referred-school-fields').addClass('d-none');
        $('#id_referred_school').removeClass('error-field');
    }

    if(recommended_learning_path == 'Drop out'){
        $('div#div_id_dropout_date').removeClass('d-none');
    }
    else{
        $('#id_dropout_date').val('');
        $('div#div_id_dropout_date').addClass('d-none');
    }

    $('#formal-education-fields').toggleClass('d-none', !showFormalEducationDetails);
    if (!showFormalEducationDetails) {
        $('#id_cerd_number, #id_formal_education_school_type, ' +
          '#id_formal_education_grade_level').val('');
    }

    $('#transition-fields').toggleClass('d-none', !progressToFormalEducation);
    if (!progressToFormalEducation) {
        $('#id_transition_arabic_grade, #id_transition_foreign_languages_grade, ' +
          '#id_transition_math_grade, #id_retention_support_enrolled').val('');
    }

    var showRetentionSupportDetails = progressToFormalEducation &&
        $('#id_retention_support_enrolled').val() == 'Yes';
    $('#retention-support-fields').toggleClass('d-none', !showRetentionSupportDetails);
    if (!showRetentionSupportDetails) {
        $('#id_retention_support_partner, #id_retention_support_center').val('');
    }
  }
