
        function AddAttemptEmptyRow()
        {
           AddAttemptRow({id:'', date:(new Date()).toString(),household_not_found:false,comment:''}, false);
        }

        function AddAttemptRow(entry, isFirst)
        {
           var attemptIDCell = "<td style = \"display:none\">"+(entry.id)+"</td>";

           var dateCell = "<td>"+FormatDate(entry.date)+"</td>";

           var checkBoxCell;

           var noteCell;

           if(isFirst && visitDataRecord.visit_status != "completed")
           {
             checkBoxCell = "<td><input type=\"checkbox\" name=\"found\" value=\"found\" "+(entry.household_not_found?"checked":"")+" /></td>";
             noteCell = "<td><textarea name=\"comment\" style=\"width:100%;height:100%\" >"+(entry.comment)+"</textarea></td>";
           }
           else
           {
             checkBoxCell = "<td><input disabled type=\"checkbox\" name=\"found\" value=\"found\" "+(entry.household_not_found?"checked":"")+" /></td>";
             noteCell = "<td>"+(entry.comment)+"</td>";
           }

           $("#household-visit-attempt-table tbody").append
           (
              "<tr>"+attemptIDCell+dateCell+checkBoxCell+noteCell+"</tr>"
           );
        }
