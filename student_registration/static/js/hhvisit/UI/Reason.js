


        function AddReasonEmptyRow(editForm)
        {
           AddReasonRow(editForm,{id:'',main_reason_id:null,specific_reason_id:null,Reason_provider:'',Reason_provider_followup:false});
        }

        function AddReasonRow(editForm, entry)
        {
           var ReasonIDCell = "<td style = \"display:none\">"+(entry.id!=null?entry.id:'')+"</td>";

           var MainReasonCell = "<td>"+editForm.find("[name=childMainReasons]").html()+"</td>";
           var SpecificReasonCell = "<td>"+editForm.find("[name=childSpecificReasons]").html()+"</td>";

           var SpecifyOtherReasonCell = "<td><input type=\"text\" value=\""+entry.specific_reason_other_specify+"\" style = \"width:100%;\" /></td>";

           var deleteReasonCell = "<td><button class=\"btn btn-danger delete-Reason-row\" type=\"button\" ><i class=\"icon-trash icon-white\"></i></button></td>";

           editForm.find("[name=childReasons] tbody").append
           (
              "<tr>"+ReasonIDCell+MainReasonCell+SpecificReasonCell+SpecifyOtherReasonCell+deleteReasonCell+"</tr>"
           );

           updateDropDownValue(editForm.find("tr:last-child td:nth-child(2) select"), entry.main_reason_id );
           updateDropDownValue(editForm.find("tr:last-child td:nth-child(3) select"), entry.specific_reason_id );
        }

        function InitialiseReasonDeleting(editForm)
        {
          editForm.on('click', '.delete-Reason-row', function(){

              var block = $(this);

              block.parent().parent().remove();

          });
        }


