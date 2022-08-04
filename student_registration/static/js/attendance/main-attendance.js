
$(document).ready(
   function()
   {
        if($(document).find('#id_attendance_date').length == 1) {
            $('#id_attendance_date').datepicker({dateFormat: "yy-mm-dd"});
        }


//      Default Setting: close_reason is hidden
        $('div#div_id_close_reason').addClass('d-none');
        $(document).on('change', 'select#id_day_off', function () {
            day_off = $("#id_day_off").val();
            if (day_off == 'yes') {
                $('div#div_id_close_reason').removeClass('d-none');
                $('#submit-id-save').attr('disabled', false);
            }
            else {
                $('div#div_id_close_reason').addClass('d-none');
                loadButtonDisabled = $('#button-id-loadstudentsbutton').attr('disabled');
                $('#submit-id-save').attr('disabled', (!loadButtonDisabled));

            }
        });

        $(document).on('change', 'select#id_school, select#id_registration_level ' , function () {
            filter_changed();
        });


//        $("#id_attendance_date").on("change", function() {
//            filter_changed();
//            var selectedDate = $(this).datepicker('getDate');
//            alert("Selected date is : " + selectedDate );
//            var today = new Date();
//            var twoWeeksbefore = new Date(today.setDate(today.getDate() - 14));
//            if (selectedDate.getTime() > today.setHours(0,0,0,0)) {
//                alert(selectedDate.getTime())
//                alert (today.setHours(0,0,0,0))
//                alert('You cannot enter attendance for a future date');
//                return false;
//            }
//            else if (selectedDate.getTime() < twoWeeksbefore.setHours(0,0,0,0)) {
//                alert('More than 2 weeks');
//                return false;
//            }
//        });
//        $( "#id_attendance_date" ).datepicker({
//             minDate: -5,
//             maxDate: "+5D",
//             beforeShowDay: disableHoliday
//        });


        $("#button-id-loadstudentsbutton").click
        (
         function ()
         {
            schoolID = $("#id_school").val();
            registrationLevel = $("#id_registration_level").val();
            day_off = $("#id_day_off").val();
            attendance_date = $("#id_attendance_date").val();
            if (schoolID>0 && registrationLevel!='' )
            {
                if(day_off=='yes')
                {
                    close_reason = $("#id_close_reason").val();
                    if (close_reason!='')
                    {
                        window.location = window.location.origin
                        + "/attendances/main-attendance/?attendance_date="+attendance_date.toString()
                        +"&school="+schoolID.toString()
                        +"&registration_level="+registrationLevel.toString()
                        +"&day_off="+day_off.toString()
                    }
                    else
                    {
                        alert("Please specify the reason for day off");
                    }
                }
                else
                {
                    window.location = window.location.origin
                    + "/attendances/main-attendance/?attendance_date="+attendance_date.toString()
                    +"&school="+schoolID.toString()
                    +"&registration_level="+registrationLevel.toString()
                    +"&day_off="+day_off.toString()
                    ;
                }
            }
            else
            {
                alert("School and Registration Level are mandatory")
            }

         }
      );
   }
);

function filter_changed()
{
    loadButtonDisabled = $('#button-id-loadstudentsbutton').attr('disabled');
    if (loadButtonDisabled){
        $('#submit-id-save').attr('disabled', (loadButtonDisabled));
        $('#button-id-loadstudentsbutton').attr('disabled', (!loadButtonDisabled));
    }
}
function disableHoliday(date) {
    var string = $.datepicker.formatDate('yy-mm-dd', date);

    var filterDate = new Date(string);
    var day = filterDate.getDay();
    return [day != 0 && day !=6]
 }


