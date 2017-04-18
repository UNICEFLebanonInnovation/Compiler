  function ValidateReasons(editForm)
        {
           var reasonsValid = true;
           var rowCount =  0;

           editForm.find("[name=childReasons] tbody tr")
           .each
           (
              function(i, obj) {
                  trElement = $(obj);

                  var childReasonRecordID = trElement.find('td:nth-child(1)').html();

                  if (childReasonRecordID == '')
                  {
                      reasonsValid = reasonsValid && ValidateReason(trElement);
                      rowCount += 1;
                  }
              }
           );
           if(reasonsValid && rowCount>0)
           {
               editForm.find("#reasons_error").hide();
           }
           else
           {
               editForm.find("#reasons_error").show();
           }

           return reasonsValid && rowCount>0;
        }

        function ValidateReason(trElement)
        {
           childReasonRecord = new Object();

           mainReasonDropDownElement = trElement.find('td:nth-child(2) select');


           subReasonDropDownElement = trElement.find('td:nth-child(3) select');

           childReasonRecord.main_reason_id = mainReasonDropDownElement.val();

           childReasonRecord.sub_reason_id = subReasonDropDownElement.val();

           //console.log(childReasonRecord);
           return childReasonRecord.main_reason_id && childReasonRecord.sub_reason_id;
        }
