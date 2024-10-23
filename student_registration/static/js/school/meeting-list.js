
$(document).ready(function() {

    $( ".delete-meeting" ).on( "click", function(e) {

        e.preventDefault();

        var buttonId = $(this).attr("id");
        var meetingId = $(this).data("meeting-id");
        var parentTR = $(this).closest('tr');

        var confirmed = confirm("Are you sure you want to delete this meeting?");
        requestHeaders = getHeader();
        requestHeaders["content-type"] = 'application/json';

        if (confirmed) {
            $.ajax({
                url: "/schools/meeting-delete/" + meetingId + "/",
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
            console.log("User canceled deleting for meeting with ID: " + meetingId);
        }
    } );

});

