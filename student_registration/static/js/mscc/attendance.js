
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

        var attendance_day_off = $("input[name='attendance_day_off']:checked").val();
        var attendance_date = $("#attendance_date").val();

        children_attendance = [];

        $(".list-group-item")
        .each
        (
            function()
            {
               child_id = $(this).find(".child_id").val();

               var attended = $("input[name='attendance_status[]']:checked").val();

               children_attendance.push
               (
                  {
                     "child_id": child_id,
                     "attended": attended
                  }
               );
            }
        );


        var attendance_information =
        {
           "attendance_date": attendance_date,
           "attendance_day_off": attendance_day_off,
           "children_attendance": children_attendance
        };

        var params = [];

        $.ajax({
            type: "POST",
            url: $(this).attr('href'),
            cache: false,
            headers: getHeader(),
            data: JSON.stringify(attendance_information),
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
