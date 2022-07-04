
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
            }
            else {
                $('div#div_id_close_reason').addClass('d-none');
            }
        });

          $("#button-id-loadstudentsbutton").click
          (
             function ()
             {
                schoolID = $("#id_school").val();
                registrationLevel = $("#id_registration_level").val();
                day_off = $("#id_day_off").val();
                if (schoolID>0 && registrationLevel!='' )
                {
                    if(day_off=='yes')
                    {
                        close_reason = $("#id_close_reason").val();
                        if (close_reason!='')
                        {
                            window.location = window.location.origin
                            + "/attendances/main-attendance/?school="+schoolID.toString()
                            +"&registration_level="+registrationLevel.toString()
                            +"&day_off="+day_off.toString()
                            +"&close_reason="+close_reason.toString();
                        }
                        else
                        {
                            alert("Please specify the reason for day off");
                        }
                    }
                    else
                    {
                        window.location = window.location.origin + "/attendances/main-attendance/?school="+schoolID.toString()
                        +"&registration_level="+registrationLevel.toString()
                        +"&day_off="+day_off.toString();
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
