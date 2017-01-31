

        function ValidateAttempts()
        {
           var attemptsValid = true;

           $("#household-visit-attempt-table tbody tr")
           .each
           (
              function(i, obj)
              {
                 trElement = $(obj);

                 attemptsValid = attemptsValid && ValidateAttempt(trElement);

              }
           );

           if(!attemptsValid)
           {
              $("#household_not_found_error").show();
           }
           else
           {
            $("#household_not_found_error").hide();
            }

           return attemptsValid;
        }

        function ValidateAttempt(trElement)
        {
           var id = trElement.find('td:nth-child(1)').html();

           var household_not_found = trElement.find('td:nth-child(3) input').is(':checked');

           var comment = trElement.find('td:nth-child(4) textarea').val();

           return !household_not_found || comment;
        }
