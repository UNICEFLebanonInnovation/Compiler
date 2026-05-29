
var protocol = window.location.protocol;
var host = protocol+window.location.host;

$(document).ready(function() {

    var ABSENCE_REASON_OTHER_MAX_LENGTH = 500;
    var DEFAULT_FORM_ERROR_MESSAGE = 'Please check the form mandatory fields.';
    var ABSENCE_REASON_OTHER_TOO_LONG_MESSAGE = 'The absence other reason text is too long. Please enter 500 characters or fewer.';

    function showAttendanceWarning(message) {
        $('#formErrorModal #swal2-content').text(message);
        $('#formErrorModal').modal('show');
    }

    $('#formErrorModal').on('hidden.bs.modal', function() {
        $('#formErrorModal #swal2-content').text(DEFAULT_FORM_ERROR_MESSAGE);
    });

    $('.attendance_day_off label').click(function(e) {
        setTimeout(
          function()
          {
                console.log($('input[name=attendance_day_off]:checked').val());
                var attendance_day_off = $('input[name=attendance_day_off]:checked').val();

                if (attendance_day_off == 'Yes') {
                    $('#close_reason').removeClass('hidden');
                    $('#load_attendance_children').addClass('disabled');
                    $('#save_attendance_children').removeClass('disabled');
                    $('#attendance_children').empty("");
                }else {
                    $('#close_reason').addClass('hidden');
                    $('#load_attendance_children').removeClass('disabled');
                }
          }, 500);

    });

    $(document).on('click', '#save_attendance_children', function(e){
    e.preventDefault();

    let isValid = true;
    $('.is-invalid').removeClass('is-invalid'); // reset styles

    var attendance_day_off = $("input[name='attendance_day_off']:checked").val();
    var attendance_date = $("#attendance_date").val();
    var education_program = $("#education_program").val();
    var class_section = $("#class_section").val();
    var close_reason = $("#close_reason").val();
    var round_id = $("#round").val();
    children_attendance = [];

    $(".list-group-item").each(function () {
        var $item = $(this);
        var child_id = $item.find(".child_id").val();
        var registration_id = $item.find(".registration_id").val();
        var attended = $item.find("input.status:checked").val() || "Yes";
        var absence_reason = $item.find(".absence_reason").val();
        var absence_reason_other = $item.find(".absence_reason_other").val();

        // Validation logic
        if (absence_reason_other.length > ABSENCE_REASON_OTHER_MAX_LENGTH) {
            $item.find(".absence_reason_other").addClass("is-invalid");
            isValid = false;
        }

        if (attended === 'No') {
            if (!absence_reason) {
                $item.find(".absence_reason").addClass("is-invalid");
                isValid = false;
            } else if (absence_reason === 'Other' && !absence_reason_other.trim()) {
                $item.find(".absence_reason_other").addClass("is-invalid");
                isValid = false;
            }
        }

        children_attendance.push({
            "child_id": child_id,
            "registration_id": registration_id,
            "attended": attended,
            "absence_reason": absence_reason,
            "absence_reason_other": absence_reason_other
        });
    });

    if (!isValid) {
        var hasLongAbsenceReason = $('.absence_reason_other.is-invalid').filter(function() {
            return $(this).val().length > ABSENCE_REASON_OTHER_MAX_LENGTH;
        }).length > 0;
        showAttendanceWarning(hasLongAbsenceReason ? ABSENCE_REASON_OTHER_TOO_LONG_MESSAGE : DEFAULT_FORM_ERROR_MESSAGE);
        return;
    }

    $('.app-drawer-overlay').removeClass('d-none');
    $('#save_attendance_children').addClass('disabled');

    var attendance_information = {
       "attendance_date": attendance_date,
       "attendance_day_off": attendance_day_off,
       "close_reason": close_reason,
       "education_program": education_program,
       "class_section": class_section,
       "round_id": round_id,
       "children_attendance": children_attendance
    };

    $.ajax({
        type: "POST",
        url: $(this).attr('href'),
        cache: false,
        headers: getHeader(),
        data: JSON.stringify(attendance_information),
        async: true,
        dataType: 'json',
        success: function (response) {
            if (response.result) {
                $('.app-drawer-overlay').addClass('d-none');
                $('#formSuccessModal').modal('show');
            }
            console.log(response);
        },
        error: function(response) {
            console.log(response);
            var errorMessage = response.responseJSON && response.responseJSON.error ? response.responseJSON.error : DEFAULT_FORM_ERROR_MESSAGE;
            showAttendanceWarning(errorMessage);
            $('.app-drawer-overlay').addClass('d-none');
        },
        complete: function() {
            $('#save_attendance_children').removeClass('disabled');
            $('.app-drawer-overlay').addClass('d-none');
        }
    });
});

    $(document).on('click', '#load_attendance_children', function(e){
        e.preventDefault();

        var education_program = $('#education_program').val();
        var round_id = $('#round').val();
        var class_section = $('#class_section').val();

        if (!education_program || !round_id || !class_section) {
             showModal("Please fill: Attendance Date, Round, School, and Registration Level.");
             return false;
        }

        $('#attendance_children').empty().append("Loading...");

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            data: {
                'attendance_date': $("#attendance_date").val(),
                'center_id': $('#center_id').val(),
                'round_id': round_id,
                'education_program': education_program,
                'class_section': class_section
            },
            dataType: 'html',
            success: function (response) {
                $('#attendance_children').empty().append(response);

                var childrenCount = $(".list-group-item").length;
                $('#children_count').text(childrenCount);

                $('#save_attendance_children').removeClass('disabled');
                $('.app-drawer-overlay').addClass('d-none');
            },
            error: function(response) {
                console.log(response);
                $('.app-drawer-overlay').addClass('d-none');
            }
        });
    });

    $(document).on('click', '.show-child-details', function(e){
        e.preventDefault();

        $('#child-content').empty("");
        $('#child-content').append("Loading...");
        $('#childModal').modal('show');

        $.ajax({
            type: "GET",
            url: $(this).attr('href'),
            cache: false,
            async: true,
            dataType: 'html',
            success: function (response) {
                $('#child-content').empty("");
                $('#child-content').append(response);
            },
            error: function(response) {
                console.log(response);
            }
        });
    });

    $('#attendance_date ').click(function(e) {
        setTimeout(
          function()
          {
            $('#attendance_children').empty("");
            $('#load_attendance_children').removeClass('disabled');
            $('#save_attendance_children').addClass('disabled');
            $('#load_attendance_children').removeClass('disabled');
          }, 500);

    });


        function resetAttendanceUI() {
            $('#attendance_children').empty("");
            $('#children_count').text(0);
            $('#save_attendance_children').addClass('disabled');
            $('#load_attendance_children').removeClass('disabled');
        }

        // Trigger on all critical field changes
        $('#round, #education_program, #class_section').on('change', function() {
            resetAttendanceUI();
        });

});
