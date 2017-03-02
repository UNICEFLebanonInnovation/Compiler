  function ValidateServices(editForm)
        {
           var servicesValid = true;

           editForm.find("[name=childServices] tbody tr")
           .each
           (
              function(i, obj)
              {
                 trElement = $(obj);

                 servicesValid = servicesValid && ValidateService(trElement);

              }
           );

           return servicesValid;
        }

        function ValidateService(trElement)
        {
           childServiceRecord = new Object();

           dropDownElement = trElement.find('td:nth-child(2) select');

           childServiceRecord.service_type_id = dropDownElement.val();

           childServiceRecord.service_provider = trElement.find('td:nth-child(3) input').val();

           return childServiceRecord.service_type_id && childServiceRecord.service_provider;
        }
