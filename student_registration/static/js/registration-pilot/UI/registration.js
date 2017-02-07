

        function HideLoader()
        {
           setTimeout
           (
              function()
              {
                 $(".loader").hide();
              },
              500
           )
        }


  function InitialiseRegistrationForm(RegistrationData)
        {
           //alert(JSON.stringify(RegistrationData));

           $("#hhName").text(RegistrationData.first_name+' '+RegistrationData.father_name+' '+RegistrationData.last_name);
           $("#hhIdNumber").text(RegistrationData.all_visit_attempt_count);
           $("#hhAddess").text(RegistrationData.all_visit_attempt_count);
           $("#hhDOB").text(RegistrationData.all_visit_attempt_count);

//           $("#household-visit-child-table tbody").empty();
//
//           RegistrationData.children_visits.forEach
//           (
//              function(entry)
//              {
//                 AddChildRow(entry);
//              }
//           );
        }



        function FormatDate(dateString)
        {
           var date;

           if(isDate(dateString, "yyyy-MM-ddTHH:mm:ssZ") )
           {
              date = new Date(getDateFromFormat(dateString, "yyyy-MM-ddTHH:mm:ssZ"));
           }
           else
           {
              date = new Date(dateString);
           }

           var result =
           (
              date.getDate().toString() + '/' +
              (date.getMonth() + 1).toString() + '/' +
              date.getFullYear().toString()
           );

           return result;
        }
