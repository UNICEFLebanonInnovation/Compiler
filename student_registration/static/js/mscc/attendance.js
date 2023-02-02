
var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(document).ready(function() {

    $('.attendance_day_off label').click(function(e) {
        setTimeout(
          function()
          {
                var attendance_day_off = $('input[name=attendance_day_off]:checked').val();

                if (attendance_day_off == 'No') {
                    $('#close_reason').removeClass('hidden');
                    $('#load_attendance_children').addClass('disabled');
                    $('#save_attendance_children').removeClass('disabled');
                }else {
                    $('#close_reason').addClass('hidden');
                    $('#load_attendance_children').removeClass('disabled');
                }
          }, 500);

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
               var attended = $(this).find("input.status:checked").val();
               var absence_reason = $(this).find(".absence_reason").val();
               var absence_reason_other = $(this).find(".absence_reason_other").val();

               children_attendance.push
               (
                  {
                     "child_id": child_id,
                     "attended": attended,
                     "absence_reason": absence_reason,
                     "absence_reason_other": absence_reason_other
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
//                    $('#attendance_children').empty("");
//                    $('#save_attendance_children').addClass('disabled');
//                    $('#load_attendance_children').removeClass('disabled');
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
        var attendance_date = $("#attendance_date").val();
        var data = {
            attendance_date: attendance_date,
        };

        $('#attendance_children').empty("");
        $('#attendance_children').append("Loading...");

       $.ajax({
            type: "POST",
            url: $(this).attr('href'),
            cache: false,
            headers: getHeader(),
            async: true,
            data: JSON.stringify(data),
            dataType: 'json',
            success: function (response) {
                $('#attendance_children').empty("");
                $('#attendance_children').append(response.ChildrenView);
                attendance_data(response.attendance_id,response.attendance_day_off,response.attendance_close_reason)
                $('#save_attendance_children').removeClass('disabled');
//              $('#load_attendance_children').addClass('disabled');
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


function attendance_data(attendance_id,attendance_day_off, attendance_close_reason) {
    $("#close_reason").val(attendance_close_reason);
 }
