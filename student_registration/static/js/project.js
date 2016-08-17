/* Project specific Javascript goes here. */

setInterval(function () { window.applicationCache.update(); }, 3600000); // Check for an updated manifest file every 60 minutes. If it's updated, download a new cache as defined by the new manifest file.

window.applicationCache.addEventListener('updateready', function(){ // when an updated cache is downloaded and ready to be used
        console.log('update page');
        window.applicationCache.swapCache(); //swap to the newest version of the cache
}, false);

function getCookie(name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

/**
 *
 * @returns yyyy-mm-dd
 */
function getCurrentDate()
{
    var today = new Date();
    var dd = today.getDate();
    var mm = today.getMonth()+1; //January is 0!

    var yyyy = today.getFullYear();
    if(dd<10){
        dd='0'+dd
    }
    if(mm<10){
        mm='0'+mm
    }
    return yyyy+'-'+mm+'-'+dd;
}

function generate_student_number(itemscope)
{
    var line = $('#line-'+itemscope);
    var name = line.find('#student_full_name').val();

    var id_number = line.find('#student_id_number').val();
    var bd_year = line.find('#student_birthday_year').val();
    var bd_month = line.find('#student_birthday_month').val();
    var bd_day = line.find('#student_birthday_day').val();
    var code_char1 = String(name.charCodeAt(0));
    var code_char2 = String(name.charCodeAt(1));
    var number = code_char1+code_char2+id_number+bd_year+bd_month+bd_day;

    line.find('#student_number').val(number);
    line.find('#student_number').trigger('blur');
}
