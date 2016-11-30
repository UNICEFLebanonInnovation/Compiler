
        function AddCommentEmptyRow(entry)
        {
           AddCommentRow({id:'',date:(new Date()).toString() ,comment:''}, false);
        }

        function AddCommentRow(entry, disabled)
        {
           var attemptIDCell = "<td style = \"display:none\">"+(entry.id)+"</td>";
           var dateCell = "<td>"+FormatDate(entry.date)+"</td>";
           var noteCell ;
           if(disabled)
           {
              noteCell = "<td>"+(entry.comment)+"</td>";
           }
           else
           {
              noteCell = "<td><textarea name=\"comment\" style=\"width:100%;height:100%\" >"+(entry.comment)+"</textarea></td>";
           }

           $("#household-visit-comment-table tbody").append
           (
              "<tr>"+attemptIDCell+dateCell+noteCell+"</tr>"
           );
        }
