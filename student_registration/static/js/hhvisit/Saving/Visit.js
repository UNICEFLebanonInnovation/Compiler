
        function FormatJSONDate(dateString)
        {
           var date;

           if(isDate(dateString, "dd/MM/yyyy") )
           {
              date = new Date(getDateFromFormat(dateString, "d/MM/yyyy"));
           }
           else if(isDate(dateString, "d/MM/yyyy") )
           {
              date = new Date(getDateFromFormat(dateString, "d/MM/yyyy"));
           }
           else if(isDate(dateString, "dd/M/yyyy") )
           {
              date = new Date(getDateFromFormat(dateString, "dd/M/yyyy"));
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
        function GetChildVisitReasonData(childID)
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

              result = childVisitRecord.child_visit_reason;
           }

           return result;
        }

        function UpdateChildVisitReasonData(childID, data)
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
              childVisitRecord.child_visit_reason = data;
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

           //var allVisitAttempts = CreateVisitAttemptsDataAll(true);

           data.visit_status = "completed";

           SaveVisitRecord(visitDataRecord.id, data);
        }

        function SaveVisitAttempts()
        {
           var visitAttemptsData = CreateVisitAttemptsData();


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
            return CreateVisitAttemptsDataAll(false);
        }

        function CreateVisitAttemptsDataAll(addAll)
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

                 if( (i==0) || addAll )
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

             // var main_reason_id = trElement.find('td:nth-child(6)').html();
             //
             // if ( main_reason_id != '')
             // {
             //    childRecord.main_reason_id = main_reason_id;
             // }
             // else
             // {
             //    childRecord.main_reason_id = null;
             // }
             //
             // var specific_reason_id = trElement.find('td:nth-child(7)').html();
             //
             // if ( specific_reason_id != '')
             // {
             //    childRecord.specific_reason_id = specific_reason_id;
             // }
             // else
             // {
             //    childRecord.specific_reason_id = null;
             // }

             childRecord.household_visit_id = visitDataRecord.id;

             childRecord.child_enrolled_in_another_school = trElement.find('td:nth-child(6)').html()=="true";
             childRecord.child_no_longer_living_in_the_pilot_area = trElement.find('td:nth-child(7)').html()=="true";


             // childRecord.specific_reason_other_specify = trElement.find('td:nth-child(9)').html();

             childRecord.child_visit_service = GetChildVisitServiceData(childRecord.id);
             childRecord.child_visit_reason = GetChildVisitReasonData(childRecord.id);

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

                 childServiceRecordID= trElement.find('td:nth-child(1)').html();

                 if(childServiceRecordID != '')
                 {
                     childServiceRecord.id = trElement.find('td:nth-child(1)').html();
                 }
                 else
                 {
                      childServiceRecord.id = null;
                 }

                 dropDownElement = trElement.find('td:nth-child(2) select');

                 childServiceRecord.service_type_id = dropDownElement.val();
                 childServiceRecord.service_type = dropDownElement.find('option[value="'+childServiceRecord.service_type_id+'"]').text().trim();

                 childServiceRecord.service_provider = trElement.find('td:nth-child(3) input').val();

                 childServiceRecord.service_provider_followup = trElement.find('td:nth-child(4) input').is(':checked')

                 childServiceRecord.child_visit_id = childVisitID;

                 childServiceData.push(childServiceRecord);

              }
           );

           return childServiceData;
        }

        function CreateChildReasonData(childVisitID,editForm)
        {
          childReasonData = [];

          editForm.find("[name=childReasons] tbody tr")
              .each
              (
                  function(i, obj)
                  {
                      trElement = $(obj);

                      childReasonRecord = new Object();

                      childReasonRecordID= trElement.find('td:nth-child(1)').html();

                      if(childReasonRecordID != '')
                      {
                          childReasonRecord.id = trElement.find('td:nth-child(1)').html();
                      }
                      else
                      {
                           childReasonRecord.id = null;
                      }

                      dropDownElementMain = trElement.find('td:nth-child(2) select');
                      childReasonRecord.main_reason_id = dropDownElementMain.val();
                      childReasonRecord.main_reason = dropDownElementMain.find('option[value="'+childReasonRecord.main_reason_id+'"]').text().trim();

                      dropDownElementSub = trElement.find('td:nth-child(3) select');

                      childReasonRecord.specific_reason_id = dropDownElementSub.val();
                      childReasonRecord.specific_reason = dropDownElementSub.find('option[value="'+childReasonRecord.specific_reason_id+'"]').text().trim();

                      childReasonRecord.specific_reason_other_specify = trElement.find('td:nth-child(4) input').val();

                      childReasonRecord.child_visit_id = childVisitID;

                      childReasonData.push(childReasonRecord);





                  }
           );

           return childReasonData;
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

                      // if(jqXHR.status == 200)
                      // {
                      //    alert("Success");
                      // }
                      $("#hhForm").hide();
                      $("#hhList").show();
                      location.reload();
                   },
                   error:
                   function (response)
                   {
                      HideLoader();
                      console.log(response);
                      // alert("Failure");
                   }
              }
            );
        }
