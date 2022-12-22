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

$(document).ready(function() {
    reorganizeForm();

    if($(document).find('#id_miss_school_date').length == 1) {
        $('#id_miss_school_date').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_first_attendance_date').length == 1) {
        $('#id_first_attendance_date').datepicker({dateFormat: "yy-mm-dd"});
    }

    $(document).on('change', 'select#id_education_status', function(){
        reorganizeForm();
    });

    $(document).on('click', '.cancel-button', function(e){
        e.preventDefault();
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            window_location(item.attr('href'));
        }
    });
});

function reorganizeForm()
{
    var student_age = $('#id_student_age').val();
    var education_status = $('select#id_education_status').val();
    $('div#div_id_miss_school_date').addClass('d-none');
    $('#span_miss_school_date').addClass('d-none');
    $('div#div_id_dropout_program').addClass('d-none');
    $('#span_dropout_program').addClass('d-none');

    if(education_status != 'out of school'){
        $('#div_id_miss_school_date').removeClass('d-none');
        $('#span_miss_school_date').removeClass('d-none');
        $('div#div_id_dropout_program').removeClass('d-none');
        $('#span_dropout_program').removeClass('d-none');
    }
    if (student_age >= 16){
        $('#youth').removeClass('d-none');
    }
    else{
        $('#youth').addClass('d-none');
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

