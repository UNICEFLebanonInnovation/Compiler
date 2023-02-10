

$(document).ready(function() {

    $(document).on('click', '.download-report', function(e){
        e.preventDefault();

        var nationality = $("#id_child__nationality").val();
        var first_name = $("#id_child__first_name__contains").val();
        var last_name = $("#id_child__last_name__contains").val();
        var father_name = $("#id_child__father_name__contains").val();
        var mother_fullname = $("#id_child__mother_fullname__contains").val();

        window.open("/MSCC/export/?nationality=" + nationality
                                + "&first_name=" + first_name
                                + "&last_name=" + last_name
                                + "&father_name=" + father_name
                               + "&mother_fullname=" + mother_fullname,
            "_blank")
    });

});
