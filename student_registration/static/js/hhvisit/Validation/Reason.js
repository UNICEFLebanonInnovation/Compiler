  function ValidateReasons(editForm)
        {
           var reasonsValid = true;

           editForm.find("[name=childReasons] tbody tr")
           .each
           (
              function(i, obj)
              {
                 trElement = $(obj);

                 reasonsValid = reasonsValid && ValidateReason(trElement);

              }
           );


           return reasonsValid;
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
