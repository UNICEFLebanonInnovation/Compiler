/* Project specific Javascript goes here. */

setInterval(function () { window.applicationCache.update(); }, 3600000); // Check for an updated manifest file every 60 minutes. If it's updated, download a new cache as defined by the new manifest file.

window.applicationCache.addEventListener('updateready', function(){ // when an updated cache is downloaded and ready to be used
        console.log('update page');
        window.applicationCache.swapCache(); //swap to the newest version of the cache
}, false);

hashCode = function(str){
    var hash = 0;
    if (str.length == 0) return hash;
    for (i = 0; i < str.length; i++) {
        char = str.charCodeAt(i);
        hash = ((hash<<5)-hash)+char;
        hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash);
};

djb2Code = function(str){
    var hash = 5381;
    for (i = 0; i < str.length; i++) {
        char = str.charCodeAt(i);
        hash = ((hash << 5) + hash) + char; /* hash * 33 + c */
    }
    return hash;
};

sdbmCode = function(str){
    var hash = 0;
    for (i = 0; i < str.length; i++) {
        char = str.charCodeAt(i);
        hash = char + (hash << 6) + (hash << 16) - hash;
    }
    return hash;
};

loseCode = function(str){
    var hash = 0;
    for (i = 0; i < str.length; i++) {
        char = str.charCodeAt(i);
        hash += char;
    }
    return hash;
};


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

function generate_student_number(student)
{
    var name = student.student_full_name;
    var mother_name = student.student_mother_fullname;
    var gender = student.student_sex;
    var bd_year = student.student_birthday_year;
    var bd_month = student.student_birthday_month;
    var bd_day = student.student_birthday_day;

    var ttl_char_student = name.length;
    var ttl_char_mother = mother_name.length;
    var gender_char = gender.charAt(0);
    var fullname_sections = name.split(' ');
    //console.log(fullname_sections);
    var fullname_code = hashCode(name);
    var mother_name_code = hashCode(mother_name);

    var number = String(ttl_char_student)+String(ttl_char_mother)+String(fullname_code)+String(mother_name_code)+gender_char+bd_day+bd_month+bd_year;
    return number;
}
