
var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(document).ready(function() {

$('[data-toggle="datepicker-icon"]').datepicker({trigger:".datepicker-trigger"});

//  Default Setting: close_reason is hidden
    $('#close_reason').addClass('d-none');
    $('input[name=attendance_day_off]').change(function(e) {
        var attendance_day_off = this.value

        if (attendance_day_off == 'No') {
            $('#close_reason').removeClass('d-none');
        }
        else {
            $('#close_reason').addClass('d-none');
        }
//        $('#save_attendance_children').addClass('disabled');
//        $('#load_attendance_children').removeClass('disabled');
        });

    $(document).on('click', '#save_attendance_children', function(e){
        e.preventDefault();

        var attendance_day_off = $("input[name='attendance_day_off']:checked").val();
        var attendance_date = $("#attendance_date").val();
        var close_reason = $("#close_reason").val();
        children_attendance = [];

        $(".list-group-item")
        .each
        (
            function()
            {
               var child_id = $(this).find(".child_id").val();
               var attended = $("input[name='attendance_status[]']:checked").val();
               var absence_reason = $(this).find(".absence_reason").val();

               children_attendance.push
               (
                  {
                     "child_id": child_id,
                     "attended": attended,
                     "absence_reason": absence_reason
                  }
               );
            }
        );


        var attendance_information =
        {
           "attendance_date": attendance_date,
           "attendance_day_off": attendance_day_off,
           "close_reason": close_reason,
           "children_attendance": children_attendance
        };

        $.ajax({
            type: "POST",
            url: $(this).attr('href'),
            cache: false,
            headers: getHeader(),
            data: JSON.stringify(attendance_information),
            async: true,
            dataType: 'json',
            success: function (response) {
                if (response.result) {
                    $('#attendance_children').empty("");
                    $('#save_attendance_children').addClass('disabled');
                    $('#load_attendance_children').removeClass('disabled');
                    alert("Attendance successfully saved");
                }
                console.log(response);
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

                $('#save_attendance_children').removeClass('disabled');
                $('#load_attendance_children').addClass('disabled');
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
