

$(document).ready(function() {


    $( ".delete-student" ).on( "click", function(e) {

        e.preventDefault();

        var buttonId = $(this).attr("id");
        var registrationId = $(this).data("registration-id");
        var parentTR = $(this).closest('tr');

        var confirmed = confirm("Are you sure you want to delete this student?");
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        if (confirmed) {
            $.ajax({
                url: "/MSCC/Child-Mark-Delete/" + registrationId + "/",
                type: "GET",
                headers: requestHeaders,
                success: function(data) {
                    console.log(parentTR.html());
                    parentTR.remove();
                },
                error: function(error) {
                    // Handle error if needed
                }
            });
        } else {
            console.log("User canceled marking as deleted for student with ID: " + studentId);
        }
    } );


    $(document).on('click', '.download-center-report', function(e){
        e.preventDefault();

        var center_name = $("#id_name").val();
        var center_type = $("#id_type").val();
        var center_governorate = $("#id_governorate").val();

        requestHeaders = getHeader();

        $(".downloading-message").show();
        $('.download-center-report').addClass('disabled');

        $.ajax({
            url: "/locations/export-center-background/?center_name=" + center_name
                                + "&center_type=" + center_type
                                + "&center_governorate=" + center_governorate ,
            type: "GET",
            headers: requestHeaders,
            success: function(data) {

               $(".downloading-message").hide();
               $('.download-center-report').removeClass('disabled');
               window.open("/MSCC/export-download/" + data,
                           "_blank");

            },
            error: function(error) {
                // Handle error if needed
            }
        });

    });

    $(document).on('click', '.download-report', function(e){
        e.preventDefault();

        var nationality = $("#id_child__nationality").val();
        var first_name = $("#id_child__first_name").val();
        var last_name = $("#id_child__last_name").val();
        var father_name = $("#id_child__father_name").val();
        var mother_fullname = $("#id_child__mother_fullname").val();
        var round = $("#id_round").val();
        if(!round){
            alert("Cycle is not selected. Please select a cycle before exporting data.");
            return;
        }

        requestHeaders = getHeader();

        $(".downloading-message").show();
        $('.download-report').addClass('disabled');




        $.ajax({
            url: "/MSCC/export-list-background/?nationality=" + nationality
                                + "&first_name=" + first_name
                                + "&last_name=" + last_name
                                + "&father_name=" + father_name
                               + "&mother_fullname=" + mother_fullname
                               + "&round=" + round,
            type: "GET",
            headers: requestHeaders,
            success: function(data) {

               $(".downloading-message").hide();
               $('.download-report').removeClass('disabled');
               window.open("/MSCC/export-download/" + data,
                           "_blank");

            },
            error: function(error) {
                // Handle error if needed
            }
        });

    });

});

