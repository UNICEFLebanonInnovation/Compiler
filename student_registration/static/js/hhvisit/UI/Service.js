


        function AddServiceEmptyRow(editForm)
        {
           AddServiceRow(editForm,{id:'',service_type_id:null,service_provider:'',service_provider_followup:false});
        }

        function AddServiceRow(editForm, entry)
        {
           var serviceIDCell = "<td style = \"display:none\">"+(entry.id!=null?entry.id:'')+"</td>";

           var serviceTypeCell = "<td>"+editForm.find("[name=childServiceType]").html()+"</td>";

           var serviceProvideCell = "<td><input type=\"text\" value=\""+entry.service_provider+"\" style = \"width:100%;\" /></td>";

           var serviceProvideFollowUpCell = "<td><input type=\"checkbox\" name=\"followup\" value=\"followup\" "+(entry.service_provider_followup?"checked":"")+"/></td>";

           var deleteServiceCell = "<td><button class=\"btn btn-danger delete-service-row\" type=\"button\" ><i class=\"icon-trash icon-white\"></i></button></td>";

           var dateCell = "<td>"+FormatDate((new Date()).toString())+"</td>";

           editForm.find("[name=childServices] tbody").append
           (
              "<tr>"+serviceIDCell+serviceTypeCell+serviceProvideCell+serviceProvideFollowUpCell+dateCell+deleteServiceCell+"</tr>"
           );

           updateDropDownValue(editForm.find("[name=childServices] tr:last-child td:nth-child(2) select"), entry.service_type_id );
        }

        function AddReadonlyServiceRow(editForm, entry)
        {
            alert('test');
           var serviceIDCell = "<td style = \"display:none\">"+(entry.id!=null?entry.id:'')+"</td>";

           var serviceTypeCell = "<td>"+entry.id+"</td>";

           var serviceProvideCell = "<td>"+entry.service_provider+"</td>";

           var serviceProvideFollowUpCell = "<td>"+(entry.service_provider_followup?"Yes":"No")+"</td>";

           var deleteServiceCell = "<td></td>";

           var dateCell = "<td>"+FormatDate(entry.service_date)+"</td>";

           editForm.find("[name=childServices] tbody").append
           (
              "<tr>"+serviceIDCell+serviceTypeCell+serviceProvideCell+serviceProvideFollowUpCell+dateCell+deleteServiceCell+"</tr>"
           );

        }

        function InitialiseServiceDeleting(editForm)
        {
          editForm.on('click', '.delete-service-row', function(){

              var block = $(this);

              block.parent().parent().remove();

          });
        }
