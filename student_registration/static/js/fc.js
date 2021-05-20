/**
 * Created by yosr on 11/26/20.
 */

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
    // # child_have_pss_wellbeing, child_have_pss_wellbeing_explain

    if($(document).find('#id_date_of_monitoring').length == 1) {
        $('#id_date_of_monitoring').datepicker({dateFormat: "yy-mm-dd"});
    }

    reorganizeForm();

    $(document).on('change', 'select#id_materials_needed_available, ' +
        'select#id_remote_learning, ' +
        'select#id_homework_after_lesson ', function(){
                reorganizeForm();
    });

    // $(document).on('click', 'input[name=how_contact_caregivers]', function () {
    //     var how_contact_caregivers = $('input[id=id_how_contact_caregivers_4]:checked').val();
    //
    //     if (how_contact_caregivers == 'other') {
    //         $('div#div_id_how_keep_touch_caregivers_specify').removeClass('d-none');
    //         $('#span_how_keep_touch_caregivers_specify').removeClass('d-none');
    //     }
    //     else
    //     {
    //         $('div#div_id_how_keep_touch_caregivers_specify').addClass('d-none');
    //         $('#span_how_keep_touch_caregivers_specify').addClass('d-none');
    //         $('#id_how_keep_touch_caregivers_specify').val('');
    //
    //     }
    //
    // });


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

    pageScripts();

        /* Ajax page load settings */
        $(document).on('pjax:end', pageScripts);
        if (sessionStorage.getItem("pjax-enabled") === "0") {
            return;
        }

        // Comment it to disable Ajax Page load
        $(document).pjax('a', '.content-wrap', {fragment: '.content-wrap'});

        $(document).on('pjax:beforeReplace', function() {
            $('.content-wrap').css('opacity', '0.1');
            setTimeout(function() {
                $('.content-wrap').fadeTo('100', '1');
            }, 1);
        });
});

function pageScripts() {
    /* Magnific Popup */
    $('.image-link').magnificPopup({
        type: 'image',
        gallery: {
            enabled: true
        }
    });
}

function reorganizeForm()
{
    var remote_learning = $('select#id_remote_learning').val();

    var materials_needed_available = $('select#id_materials_needed_available').val();
    var homework_after_lesson = $('select#id_homework_after_lesson').val();
    var child_awareness_prevention_covid19 = $('select#id_child_awareness_prevention_covid19').val();

    $('#weekly_lesson').addClass('hide');
    $('#feedback').addClass('hide');
    $('#follow_up').addClass('hide');
    $('#gender_considerations').addClass('hide');

    if (remote_learning == 'yes') {
        $('#weekly_lesson').removeClass('hide');
        $('#feedback').removeClass('hide');
        $('#follow_up').removeClass('hide');
        $('#gender_considerations').removeClass('hide');

    }
    else {
        $('#weekly_lesson').addClass('hide');
        $('#feedback').addClass('hide');
        $('#follow_up').addClass('hide');
        $('#gender_considerations').addClass('hide');
    }

    $('div#div_id_parents_supporting_student').addClass('d-none');
    $('#span_parents_supporting_student').addClass('d-none');

    if(homework_after_lesson == 'yes'){
        $('div#div_id_parents_supporting_student').removeClass('d-none');
        $('#span_parents_supporting_student').removeClass('d-none');
    }
    else{
        $('#id_parents_supporting_student').val('');
    }


}
