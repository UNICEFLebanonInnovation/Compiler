
        function FormatJSONDate(dateString)
        {
           var date;

           if(isDate(dateString, "dd/mm/yyyy") )
           {
              date = new Date(getDateFromFormat(dateString, "dd/mm/yyyy"));
           }
           else
           {
              date = new Date(dateString);
           }

           return date;
        }



        function GetChildVisitServiceData(childID)
        {
           var result = null;

           var childVisits = visitDataRecord.children_visits.filter
           (
              function(childVisit)
              {
                 return childVisit.id == childID;
              }
           );

           if(childVisits.length > 0)
           {
              childVisitRecord = childVisits[0];

              result = childVisitRecord.child_visit_service;
           }

           return result;
        }

        function UpdateChildVisitServiceData(childID, data)
        {
           var childVisitRecord = null;

           var childVisits = visitDataRecord.children_visits.filter
           (
              function(childVisit)
              {
                 return childVisit.id == childID;
              }
           );

           if(childVisits.length > 0)
           {
              var childVisitRecord = childVisits[0];
              childVisitRecord.child_visit_service = data;
           }

        }

        function updateDropDownValue(dropDownElement, value)
        {
            dropDownElement.find('option:selected').removeAttr('selected');
            dropDownElement.find('option[value="'+value+'"]').attr("selected",true);
            dropDownElement.val(value);
        }


        function SaveVisit()
        {
           var data =
           {

              visit_attempt : CreateVisitAttemptsData(),

              children_visits : CreateChildData(),

              visit_comment : CreateVisitCommentData()

           };

           <!--if(data.visit_attempt.length > 0)-->
           <!--{-->
              <!--data.visit_status = data.visit_attempt[0].household_not_found ? "pending" : "completed";-->
           <!--}-->
           data.visit_status = data.visit_attempt[0].household_not_found ? "pending" : "completed";

           SaveVisitRecord(visitDataRecord.id, data);
        }

        function SaveVisitAttempts()
        {
           var visitAttemptsData = CreateVisitAttemptsData();

           alert(JSON.stringify(visitAttemptsData));

           visitAttemptsData.forEach
           (
              function(entry)
              {
                 SaveVisitAttemptRecord(entry.id,entry);
              }
           );
        }

        function CreateVisitAttemptsData()
        {
           visitAttemptsData = [];

           $("#household-visit-attempt-table tbody tr")
           .each
           (
              function(i, obj)
              {
                 trElement = $(obj);

                 visitAttemptRecord = new Object();

                 visitAttemptRecord.id = trElement.find('td:nth-child(1)').html();

                 visitAttemptRecord.date = FormatJSONDate((trElement.find('td:nth-child(2)').html()) );

                 visitAttemptRecord.household_not_found = trElement.find('td:nth-child(3) input').is(':checked');

                 visitAttemptRecord.comment = trElement.find('td:nth-child(4) textarea').val();

                 visitAttemptRecord.household_visit_id = visitDataRecord.id;

                 //alert(JSON.stringify(visitAttemptRecord));

                 if(!visitAttemptRecord.id )
                 {
                    visitAttemptsData.push(visitAttemptRecord);
                 }

              }
           );

           return visitAttemptsData;
        }


        function CreateVisitCommentData()
        {
           visitCommentData = [];

           $("#household-visit-comment-table tbody tr")
           .each
           (
              function(i, obj)
              {
                 trElement = $(obj);

                 visitCommentRecord = new Object();

                 visitCommentRecord.id = trElement.find('td:nth-child(1)').html();

                 visitCommentRecord.date = FormatJSONDate((trElement.find('td:nth-child(2)').html()) );

                 visitCommentRecord.comment = trElement.find('td:nth-child(3) textarea').val();

                 visitCommentRecord.household_visit_id = visitDataRecord.id;

                 if( visitCommentRecord.comment && !visitCommentRecord.id )
                 {
                    visitCommentData.push(visitCommentRecord);
                 }
              }
           );

           <!--alert(JSON.stringify(visitCommentData));-->
           return visitCommentData;
        }

        function CreateChildData()
        {
           childData = [];

           $("#household-visit-child-table tbody tr")
           .each
           (
              function(i, obj)
              {
                 trElement = $(obj);

                 childRecord = CreateChildDataRecord(trElement);

                 childData.push(childRecord);
              }
           );

           return childData;
        }

        function CreateChildDataRecord(trElement)
        {
             childRecord = new Object();

             childRecord.id = trElement.find('td:nth-child(1)').html();

             childRecord.main_reason_id = trElement.find('td:nth-child(6)').html();

             childRecord.specific_reason_id = trElement.find('td:nth-child(7)').html();

             childRecord.household_visit_id = visitDataRecord.id;

             childRecord.child_enrolled_in_another_school = trElement.find('td:nth-child(8)').html()=="true";

             childRecord.child_visit_service = GetChildVisitServiceData(childRecord.id);

             return childRecord;
        }


        function CreateChildServiceData(childVisitID,editForm)
        {
           childServiceData = [];

           editForm.find("[name=childServices] tbody tr")
           .each
           (
              function(i, obj)
              {
                 trElement = $(obj);

                 childServiceRecord = new Object();

                 childServiceRecord.id = trElement.find('td:nth-child(1)').html();

                 dropDownElement = trElement.find('td:nth-child(2) select');

                 childServiceRecord.service_type_id = dropDownElement.val();
                 childServiceRecord.service_type = dropDownElement.find('option[value="'+childServiceRecord.service_type_id+'"]').text().trim();

                 childServiceRecord.service_provider = trElement.find('td:nth-child(3) input').val();

                 childServiceRecord.child_visit_id = childVisitID;

                 childServiceData.push(childServiceRecord);

              }
           );

           return childServiceData;
        }

        function SaveVisitRecord(id, data)
        {
            SaveRelatedRecord(id,data,hhVisitURL);
        }

        function SaveVisitAttemptRecord(id, data)
        {
            SaveRelatedRecord(id,data,hhVisitAttemptURL);
        }

        function SaveChildVisitRecord(id, data)
        {
            SaveRelatedRecordCallback
            (
                id,
                data,
                hhVisitChildVisitURL,
                function(result)
                {
                    data.child_visit_service.forEach
                    (
                      function(entry)
                      {
                          entry.child_visit_id = result.id;
                          SaveChildVisitServiceRecord(entry.id,entry);
                      }
                    );
                }
            );
        }

        function SaveChildVisitServiceRecord(id, data)
        {
            SaveRelatedRecord
            (
                id,
                data,
                hhVisitServiceURL
            );
        }

        function SaveChildVisitCommentRecord(id, data)
        {
            SaveRelatedRecord
            (
                id,
                data,
                hhVisitCommentURL
            );
        }

        function SaveRelatedRecord(id, data, url)
        {
            SaveRelatedRecordCallback(id,data,url, function(x){});
        }

        function SaveRelatedRecordCallback(id, data, url, callback)
        {
           $(".loader").show();

           <!--alert(JSON.stringify(data));-->

           $.ajax
           (
              {
                   type: id != null ? "PUT":"POST",
                   url: url+ (id != null ? id+"/" : ""),
                   contentType: 'application/json; charset=utf-8',
                   data: JSON.stringify(data),
                   cache: false,
                   headers: getHeader(),
                   dataType: 'json',
                   success: function (response, result, jqXHR)
                   {
                      HideLoader();

                      if(jqXHR.status == 200)
                      {
                         alert("Success");
                      }

                      <!--alert(response);-->

                      $("#hhForm").hide();

                      $("#hhList").show();
                   },
                   error:
                   function (response)
                   {
                      HideLoader();
                      alert("Failure");
                   }
              }
            );
        }
