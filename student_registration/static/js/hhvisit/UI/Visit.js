

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


  function InitialiseVisitForm(visitData)
        {
           visitDataRecord = visitData;
           visit_status = visitData.visit_status;


           $("#hhVisitName").text(visitData.first_name+' '+visitData.father_name+' '+visitData.last_name);
           $("#hhIdNumber").text(visitData.registeringadult_id_number);
           $("#hhAllvisitAttemptCount").text(visitData.all_visit_attempt_count);

           $("#household-visit-attempt-table tbody").empty();
           //AddAttemptEmptyRow();

           visitData.visit_attempt.forEach
           (
              function(entry,i)
              {
                 AddAttemptRow(entry, i==0);
              }
           );

           $("#household-visit-attempt-table tbody [name=found]").change
           (
              function()
              {
                if(this.checked)
                {
                   $("#hhSaveButton").show();
                }
                else
                {
                   $("#hhSaveButton").hide();
                }
             }
           );


           $("#household-visit-child-table tbody").empty();

           visitData.children_visits.forEach
           (
              function(entry)
              {
                 AddChildRow(entry);
              }
           );

           $("#household-visit-comment-table tbody").empty();
           AddCommentEmptyRow();
           visitData.visit_comment.forEach
           (
              function(entry)
              {
                 AddCommentRow(entry, true);
              }
           );


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
