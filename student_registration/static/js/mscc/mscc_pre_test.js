
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

    reorganizeForm_post_assessment();

    if($(document).find('#id_adolescent_dropout_date').length == 1) {
        $('#id_adolescent_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_attended_arabic, select#id_attended_foreign_language,  select#id_attended_math', function(){
       reorganizeForm_post_assessment();
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

