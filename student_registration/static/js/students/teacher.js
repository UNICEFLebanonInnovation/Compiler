/**
 * Created by yosr on 05/31/22.
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
var arabic_fields = "#id_first_name, #id_father_name, #id_last_name, #id_child_mother_fullname";

$(document).ready(function() {

    organize_form();
    if($(document).find('#id_academic_year_start').length == 1) {
        $('#id_academic_year_start').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_academic_year_end').length == 1) {
        $('#id_academic_year_end').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('click', '.justify-button', function(){
        var item = $(this);
        var itemscope = item.attr('itemscope');
        if(confirm($(this).attr('translation'))) {
            $('.justify-date-block').addClass('d-none');
            $('#justify_date_block_'+itemscope).removeClass('d-none');
            var itemscope = item.attr('itemscope');
            justify_student_enrollment(item.attr('itemscope'));
        }
    });

    $(document).on('blur', arabic_fields, function(){
        checkArabicOnly($(this));
    });

    $(document).on('click', '.cancel-button', function(e){
        e.preventDefault();
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            window_location(item.attr('href'));
        }
    });

    $(document).on('change', 'select#id_extra_coaching, select#id_teacher_assignment', function () {
        organize_form();
    });

    pageScripts();

    /* Ajax page load settings */
    $(document).on('pjax:end', pageScripts);
    if (sessionStorage.getItem("pjax-enabled") === "0") {
        return;
    }
    // Comment it to disable Ajax Page load
    //$(document).pjax('a', '.content-wrap', {fragment: '.content-wrap'});

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

function organize_form() {
    extra_coaching = $('#id_extra_coaching').val();
    if (extra_coaching == 'yes') {
        $('#div_id_extra_coaching_specify').removeClass('d-none');
        $('#span_extra_coaching_specify').removeClass('d-none');
    }
    else
     {
        $('#span_extra_coaching_specify').addClass('d-none');
        $('#id_extra_coaching_specify').val('');
        $('#div_id_extra_coaching_specify').addClass('d-none');
    }

    teacher_assignment = $('#id_teacher_assignment').val();
    if (teacher_assignment == 'Private and Dirasa') {
        $('#div_id_teaching_hours_private_school').removeClass('d-none');
        $('#span_teaching_hours_private_school').removeClass('d-none');

        $('#div_id_teaching_hours_dirasa').removeClass('d-none');
        $('#span_teaching_hours_dirasa').removeClass('d-none');
    }
    else
     {
        $('#span_teaching_hours_private_school').addClass('d-none');
        $('#id_teaching_hours_private_school').val('');
        $('#div_id_teaching_hours_private_school').addClass('d-none');


        $('#span_teaching_hours_dirasa').addClass('d-none');
        $('#id_teaching_hours_dirasa').val('');
        $('#div_id_teaching_hours_dirasa').addClass('d-none');
    }
}

function urlParam(name){
	var results = new RegExp('[\?&]' + name + '=([^&#]*)').exec(window.location.href);
	if (results && results.length){
        return results[1] || 0;
    }
    return 0;
}

function window_location(value)
{
    console.log('OK');
    $('head').append('<meta http-equiv="refresh" content="0; URL='+value+'" id="redirect"/>');
}

function load_districts(url)
{
    var value = $("#id_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_governorate': value
        },
        success: function (data) {
            $("#id_district").html(data);
        }
    })
}
function load_cadasters(url)
{
    var value = $("#id_district").val();
    $.ajax({
        url: url,
        data: {
            'id_district': value
        },
        success: function (data) {
            $("#id_cadaster").html(data);
        }
    })
}
function load_schools(url)
{
    var value = $("#id_governorate").val();
    $.ajax({
        url: url,
        data: {
            'id_governorate': value
        },
        success: function (data) {
            $("#id_school").html(data);
        }
    })
}

