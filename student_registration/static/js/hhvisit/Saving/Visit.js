
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
