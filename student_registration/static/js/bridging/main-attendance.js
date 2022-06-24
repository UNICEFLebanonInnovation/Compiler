
$(document).ready(
   function()
   {
      $("#LoadStudentsButton").click
      (
         function ()
         {
            schoolID = $("#id_school").val();
            registrationLevel = $("#id_registration_level").val();
            window.location = window.location.origin + "/attendances/main-attendance/?school="+schoolID.toString()+"&registration_level="+registrationLevel.toString();
         }
      );
   }
);
