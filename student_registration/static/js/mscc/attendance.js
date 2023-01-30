
var arabic_fields = "#id_child_first_name, #id_child_father_name, #id_child_last_name, #id_child_mother_fullname, " +
    " #id_caregiver_mother_name, #id_caregiver_last_name, #id_caregiver_middle_name, #id_caregiver_first_name";
var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(document).ready(function() {

    $(document).on('change', '.attendance_day_off', function(e){
        console.log($(this).val());
        if($(this).val() == ''){

        }
    });

    $(document).on('click', '#save_attendance_children', function(e){
        e.preventDefault();



        var params = [];

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            data: params,
            async: true,
            dataType: 'json',
            success: function (response) {
            },
            error: function(response) {
                console.log(response);
            }
        });
    });


    $(document).on('click', '#load_attendance_children', function(e){
        e.preventDefault();

        $('#attendance_children').empty("");
        $('#attendance_children').append("Loading...");

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#attendance_children').empty("");
                $('#attendance_children').append(response);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    $(document).on('click', '.show-child-details', function(e){
        e.preventDefault();

        $('#child-content').empty("");
        $('#child-content').append("Loading...");
        $('#childModal').modal('show');

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#child-content').empty("");
                $('#child-content').append(response);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

});
