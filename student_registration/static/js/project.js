/* Project specific Javascript goes here. */

var user_token = null;
var db = null;

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

function scrollToBottom()
{
    $("html, body").animate({ scrollTop: $(document).height() }, 10);
}

function getHeader()
{
    var csrftoken = getCookie('csrftoken');
    var header = {'Authorization': 'Token '+user_token, 'X-CSRFToken': csrftoken};
    return header;
}

function getStoreByName(name)
{
    var store = db.transaction([name], "readwrite").objectStore(name);
    return store;
}

function pull_data_from_server(url, store_name)
{
    $.ajax({
        type: "GET",
        url: url,
        cache: false,
        async: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            var store = getStoreByName(store_name);
            $(response.data).each(function(i, item){
                store.put(item);
            });
        },
        error: function(response) {
            console.log(response);
        }
    });
}

function delete_data_from_server(url, original_id, itemid, store_name)
{
    $.ajax({
        type: "DELETE",
        url: url+original_id+'/',
        cache: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            if(response.status = '200') {
                var store = getStoreByName(store_name);
                store.delete(parseInt(itemid));
            }
        },
        error: function (response) {
            console.log(response);
        }
    });
}

function update_data_server(url, itemid, callback_success, callback_error)
{
    $.ajax({
        type: "PUT",
        url: url+itemid+'/',
        data: item,
        cache: false,
        headers: getHeader(),
        dataType: 'json',
        success: function (response) {
            if(response.status == '200'){
                if(callback_success){
                    callback_success();
                }
            }
        },
        error: function (response) {
            if(callback_error){
                callback_error();
            }
            console.log(response);
        }
    });
}
