
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

//    age_questions();


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

function age_questions() {
    var age = 6
    if(age<=2)
    {
        $('div#div_id_eating_minimum_meals').addClass('d-none');
        $('div#div_id_positive_parenting').addClass('d-none');
        $('div#div_id_respond_stressful_events').addClass('d-none');

        $('div#div_id_baby_breastfed').removeClass('d-none');
        $('div#div_id_infant_exclusively_breastfed').removeClass('d-none');
        $('div#div_id_eat_solid_food').removeClass('d-none');
        $('div#div_id_age_eat_solid_food').removeClass('d-none');
        $('div#div_id_development_delays_identified').removeClass('d-none');
    }
    else if(age>=3 && age<=5){
        $('div#div_id_baby_breastfed').addClass('d-none');
        $('div#div_id_infant_exclusively_breastfed').addClass('d-none');
        $('div#div_id_eat_solid_food').addClass('d-none');
        $('div#div_id_age_eat_solid_food').addClass('d-none');
        $('div#div_id_respond_stressful_events').addClass('d-none');

        $('div#div_id_development_delays_identified').removeClass('d-none');
        $('div#div_id_eating_minimum_meals').removeClass('d-none');
        $('div#div_id_positive_parenting').removeClass('d-none');

    }
    else if(age>=6 && age<=18)
    {
        $('div#div_id_baby_breastfed').addClass('d-none');

        $('div#div_id_infant_exclusively_breastfed').addClass('d-none');
        $('div#div_id_eat_solid_food').addClass('d-none');
        $('div#div_id_age_eat_solid_food').addClass('d-none');
        $('div#div_id_development_delays_identified').addClass('d-none')
        $('div#div_id_positive_parenting').addClass('d-none');

        $('div#div_id_eating_minimum_meals').removeClass('d-none');
        $('div#div_id_respond_stressful_events').removeClass('d-none');

    }
}

