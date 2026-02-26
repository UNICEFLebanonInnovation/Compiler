
var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(window).load(function () {

    /* Background loading full-size images */
    $('.image-link').each(function() {
        var src = $(this).attr('href');
        var img = document.createElement('img');

        img.src = src;
        $('#image-cache').append(img);
    });

});

$(document).ready(function(){

    reorganizeForm();

     $(document).on('change', 'select#id_mid_test_done ', function(){
           reorganizeForm();
        });
    $(document).on('change', 'select#id_registration_level', function(){
           reorganizeForm();
        });

    $(document).on('click', '.delete-button', function(){
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            var callback = function(){
                item.parents('tr').remove();
            };
            delete_student(item, callback());
        }
    });

    $(document).on('click', '.cancel-button', function(e){
        e.preventDefault();
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            window_location(item.attr('href'));
//            window.location = item.attr('href');
        }
    });


});

function getRequiredMidFieldsWithMax(registrationLevel)
{
    var byLevel = {
        level_one: {ef_letter_sound: 10, ef_familiar_words: 20, ef_reading_comprehension_text_1: 10, ar_letter_sound: 10, ar_familiar_words: 20, ar_reading_comprehension_text_1: 10, m_total_score: 50},
        level_two: {ef_letter_sound: 10, ef_familiar_words: 20, ef_reading_comprehension_text_1: 10, ar_letter_sound: 10, ar_familiar_words: 20, ar_reading_comprehension_text_1: 10, m_total_score: 88},
        level_three: {ef_letter_sound: 10, ef_familiar_words: 20, ef_reading_comprehension_text_1: 10, ar_letter_sound: 10, ar_familiar_words: 20, ar_reading_comprehension_text_1: 10, m_total_score: 103}
    };
    return byLevel[registrationLevel] || {};
}

function applyMidRegistrationLevelGradeVisibility()
{
    var registrationLevel = $('select#id_registration_level').val();
    var allFields = ['ef_letter_sound', 'ef_familiar_words', 'ef_reading_comprehension_text_1', 'ar_letter_sound', 'ar_familiar_words', 'ar_reading_comprehension_text_1', 'm_total_score'];
    var requiredWithMax = getRequiredMidFieldsWithMax(registrationLevel);
    allFields.forEach(function(fieldName){
        $('#div_id_' + fieldName).addClass('d-none');
        var label = $('label[for="id_' + fieldName + '"]');
        if (!label.data('baseText')) {
            label.data('baseText', label.text().replace(/\s*\/\s*\d+$/, '').replace(/\s*\/max by level$/, ''));
        }
    });

    Object.keys(requiredWithMax).forEach(function(fieldName){
        $('#div_id_' + fieldName).removeClass('d-none');
        var label = $('label[for="id_' + fieldName + '"]');
        if (label.length) {
            var baseText = label.data('baseText') || label.text();
            label.text(baseText + '/' + requiredWithMax[fieldName]);
        }
    });
}


function reorganizeForm()
{
    var mid_test_done = $('select#id_mid_test_done').val();
    $('div.grades').addClass('d-none');
    if(mid_test_done == 'no')
    {
        Object.keys(getRequiredMidFieldsWithMax($('select#id_registration_level').val())).forEach(function(fieldName){
            $('#id_' + fieldName).val('');
        });
    }
    else
    {
        $('div.grades').removeClass('d-none');
        applyMidRegistrationLevelGradeVisibility();
    }

}
