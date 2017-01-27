


        function AddServiceEmptyRow(editForm)
        {
           AddServiceRow(editForm,{id:'',service_type_id:null,service_provider:'',service_provider_followup:false});
        }

        function AddServiceRow(editForm, entry)
        {
           var serviceIDCell = "<td style = \"display:none\">"+(entry.id)+"</td>";

           var serviceTypeCell = "<td>"+editForm.find("[name=childServiceType]").html()+"</td>";

           var serviceProvideCell = "<td><input type=\"text\" value=\""+entry.service_provider+"\" style = \"width:100%;\" /></td>";

           var serviceProvideFollowUpCell = "<td><input type=\"checkbox\" name=\"followup\" value=\"followup\" "+(entry.service_provider_followup?"checked":"")+"/></td>";

           var deleteServiceCell = "<td><button class=\"btn btn-danger delete-service-row\" type=\"button\" ><i class=\"icon-trash icon-white\"></i></button></td>";

           editForm.find("[name=childServices] tbody").append
           (
              "<tr>"+serviceIDCell+serviceTypeCell+serviceProvideCell+serviceProvideFollowUpCell+deleteServiceCell+"</tr>"
           );

           updateDropDownValue(editForm.find("tr:last-child td:nth-child(2) select"), entry.service_type_id );
        }

        function InitialiseServiceDeleting(editForm)
        {
          editForm.on('click', '.delete-service-row', function(){

              var block = $(this);

              block.parent().parent().remove();

          });
        }
