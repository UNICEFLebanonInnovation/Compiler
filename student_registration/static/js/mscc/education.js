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

    if($(document).find('#id_dropout_date').length == 1) {
        $('#id_dropout_date').datepicker({dateFormat: "yy-mm-dd"});
    }
     if($(document).find('#id_registration_date').length == 1) {
        $('#id_registration_date').datepicker({dateFormat: "yy-mm-dd"});
    }


    $(document).on('click', '.cancel-button', function(e){
        e.preventDefault();
        var item = $(this);
        if(confirm($(this).attr('translation'))) {
            window_location(item.attr('href'));
        }
    });
});


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



