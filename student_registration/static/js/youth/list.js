

$(document).ready(function() {

    $(document).on('click', '.download-report', function(e){
        e.preventDefault();

        var nationality = $("#id_child__nationality").val();
        var first_name = $("#id_child__first_name").val();
        var last_name = $("#id_child__last_name").val();
        var father_name = $("#id_child__father_name").val();
        var mother_fullname = $("#id_child__mother_fullname").val();

        window.open("/youth/export/?nationality=" + nationality
                                + "&first_name=" + first_name
                                + "&last_name=" + last_name
                                + "&father_name=" + father_name
                               + "&mother_fullname=" + mother_fullname,
            "_blank")
    });

    $( ".delete-student" ).on( "click", function(e) {

        e.preventDefault();

        var buttonId = $(this).attr("id");
        var registrationId = $(this).data("registration-id");
        var parentTR = $(this).closest('tr');

        var confirmed = confirm("Are you sure you want to disable this student?");
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        if (confirmed) {
            $.ajax({
                url: "/youth/Child-Mark-Delete/" + registrationId + "/",
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
            console.log("User canceled disabling student with ID: " + studentId);
        }
    } );

    $(document).on('click', '.download-center-report', function(e){
        e.preventDefault();

        var center_name = $("#id_name").val();
        var center_type = $("#id_type").val();
        var center_governorate = $("#id_governorate").val();

        window.open("/locations/export/?center_name=" + center_name
                                + "&center_type=" + center_type
                                + "&center_governorate=" + center_governorate ,
            "_blank")
    });
});

