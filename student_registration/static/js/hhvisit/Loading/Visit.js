

        function LoadVisit(visitID)
        {
           $(".loader").show();

        <!--alert(hhVisitURL+visitID);-->
           $.ajax({
                     type: "GET",
                     url: hhVisitURL+visitID,
                     data: [],
                     cache: false,
                     async: false,
                     headers: getHeader(),
                     dataType: 'json',
                     success: function (response) {
                        InitialiseVisitForm(response);
                        HideLoader();
                     },
                     error: function (response) {
                        HideLoader();
                        var required_fields = JSON.parse(response.responseText);
                        console.log(response);
                     }
                 });

        }
