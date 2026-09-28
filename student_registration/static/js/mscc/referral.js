

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
    $(document).on('input', '#id_public_school', lookupPublicSchool);
    lookupPublicSchool();
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
    $('#public-school-fields').toggleClass('d-none', !progressToFormalEducation);
    if (!progressToFormalEducation) {
        $('#id_public_school').val('');
        $('#public-school-name').text('');
    } else {
        lookupPublicSchool();
    }
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

    if(recommended_learning_path == 'Drop out'){
        $('div#div_id_dropout_date').removeClass('d-none');
    }
    else{
        $('#id_dropout_date').val('');
        $('div#div_id_dropout_date').addClass('d-none');
    }

    $('#formal-education-fields').toggleClass('d-none', !showFormalEducationDetails);
    if (!showFormalEducationDetails) {
        $('#id_formal_education_grade_level').val('');
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

function lookupPublicSchool()
{
    var cerd = $('#id_public_school').val();
    var schoolName = $('#public-school-name');
    schoolName.text('');
    if (!/^[0-9]{1,6}$/.test(cerd || '')) {
        return;
    }
    $.getJSON($('#id_public_school').data('lookup-url') || '/mscc/public-school-lookup/', {cerd: cerd})
        .done(function(data) {
            if ($('#id_public_school').val() === cerd) {
                schoolName.text(data.name || 'No matching public school');
            }
        });
}
