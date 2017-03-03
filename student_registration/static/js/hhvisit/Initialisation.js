
var oTable = null;
var  visit_status = null;

        $(document).ready(function(){

            oTable = $('#registrations-table').DataTable({
                fixedHeader: false,
                paging:   true,
                ordering: true,
                info:     true,
                autoWidth: false,
                scrollY: '50vh',
                scrollX: true,
                scrollCollapse: true,
                "language": {
                    "url": "/static/locale/"+language+".json"
                },
                "fnInitComplete": function(oSettings, json) {
                    $('[data-toggle="tooltip"]').tooltip();
                }
            });


            $(document).on
            (
               'click',
               '.row-class',
               function()
               {
                  block = $(this);

                  var visitID = block.attr('visitID')

                  $("#hhList").hide();

                  LoadVisit(visitID);

                  $("#hhForm").show();

                  CheckInitialiseSly();

               }
             );


            $(document).on
            (
               'click',
               '#hhCloseButton',
               function()
               {
                  $("#hhForm").hide();

                  $("#hhList").show();
               }
             );

            $(document).on
            (
               'click',
               '#hhSaveButton',
               function()
               {
                   if(ValidateAttempts())
                   {
                       SaveVisit();
                   }

               }
             );


            $(document).on
            (
               'click',
               '.child-row-class',
               function()
               {
                  block = $(this);

                  ShowChildForm(block);
               }
            );
        });
