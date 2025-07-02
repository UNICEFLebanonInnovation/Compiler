// Client-side validation for MSCC MainForm

function validateMainForm() {
    var valid = true;
    $('.error-field').removeClass('error-field');

    // Date validation
    var year = parseInt($('#id_child_birthday_year').val()) || 0;
    var month = parseInt($('#id_child_birthday_month').val()) || 0;
    var day = parseInt($('#id_child_birthday_day').val()) || 0;
    if (year && month && day) {
        var dt = new Date(year, month - 1, day);
        if (dt.getFullYear() !== year || dt.getMonth() !== month - 1 || dt.getDate() !== day) {
            $('#id_child_birthday_year').addClass('error-field');
            valid = false;
        }
    } else {
        $('#id_child_birthday_year').addClass('error-field');
        valid = false;
    }

    // Child nationality other
    if ($('#id_child_nationality').val() == '6' && $('#id_child_nationality_other').val() === '') {
        $('#id_child_nationality_other').addClass('error-field');
        valid = false;
    }

    // Child have children
    if ($('#id_child_have_children').val() == 'Yes' && $('#id_child_children_number').val() === '') {
        $('#id_child_children_number').addClass('error-field');
        valid = false;
    }

    // Child have sibling
    if ($('#id_child_have_sibling').val() == 'Yes' && $('#id_child_siblings_have_disability').val() === '') {
        $('#id_child_siblings_have_disability').addClass('error-field');
        valid = false;
    }

    // Source of identification
    if ($('#id_source_of_identification').val() == 'Other Sources' && $('#id_source_of_identification_specify').val() === '') {
        $('#id_source_of_identification_specify').addClass('error-field');
        valid = false;
    }

    var package_type = $('#id_type').val();
    if (package_type == 'Core-Package') {
        if ($('#id_father_educational_level').val() === '') {
            $('#id_father_educational_level').addClass('error-field');
            valid = false;
        }
        if ($('#id_mother_educational_level').val() === '') {
            $('#id_mother_educational_level').addClass('error-field');
            valid = false;
        }
        var first_phone = $('#id_first_phone_number').val();
        var first_phone_confirm = $('#id_first_phone_number_confirm').val();
        if ($('#id_first_phone_owner').val() === '') {
            $('#id_first_phone_owner').addClass('error-field');
            valid = false;
        }
        if (first_phone !== first_phone_confirm) {
            $('#id_first_phone_number_confirm').addClass('error-field');
            valid = false;
        }
        var second_phone = $('#id_second_phone_number').val();
        var second_phone_confirm = $('#id_second_phone_number_confirm').val();
        if (second_phone !== second_phone_confirm) {
            $('#id_second_phone_number_confirm').addClass('error-field');
            valid = false;
        }
        var main_caregiver = $('#id_main_caregiver').val();
        if (main_caregiver === '') {
            $('#id_main_caregiver').addClass('error-field');
            valid = false;
        }
        if (main_caregiver == 'Other' && $('#id_main_caregiver_other').val() === '') {
            $('#id_main_caregiver_other').addClass('error-field');
            valid = false;
        }
        if ($('#id_main_caregiver_nationality').val() == '6' && $('#id_main_caregiver_nationality_other').val() === '') {
            $('#id_main_caregiver_nationality_other').addClass('error-field');
            valid = false;
        }
        if ($('#id_children_number_under18').val() === '') {
            $('#id_children_number_under18').addClass('error-field');
            valid = false;
        }
        if ($('#id_caregiver_first_name').val() === '') {
            $('#id_caregiver_first_name').addClass('error-field');
            valid = false;
        }
        if ($('#id_caregiver_middle_name').val() === '') {
            $('#id_caregiver_middle_name').addClass('error-field');
            valid = false;
        }
        if ($('#id_caregiver_last_name').val() === '') {
            $('#id_caregiver_last_name').addClass('error-field');
            valid = false;
        }
        if ($('#id_caregiver_mother_name').val() === '') {
            $('#id_caregiver_mother_name').addClass('error-field');
            valid = false;
        }
        var have_labour = $('#id_have_labour').val();
        if (have_labour === '') {
            $('#id_have_labour').addClass('error-field');
            valid = false;
        }
        if (have_labour != 'No') {
            if ($('#id_labour_type').val() === '') {
                $('#id_labour_type').addClass('error-field');
                valid = false;
            } else if ($('#id_labour_type').val() == 'Other services' && $('#id_labour_type_specify').val() === '') {
                $('#id_labour_type_specify').addClass('error-field');
                valid = false;
            }
            if ($('#id_labour_hours').val() === '') {
                $('#id_labour_hours').addClass('error-field');
                valid = false;
            }
            if ($('#id_labour_weekly_income').val() === '') {
                $('#id_labour_weekly_income').addClass('error-field');
                valid = false;
            }
            if ($('#labour_condition').val() === '') {
                $('#labour_condition').addClass('error-field');
                valid = false;
            }
        }
        var id_type = $('#id_id_type').val();
        var case_number = $('#id_case_number').val();
        var case_confirm = $('#id_case_number_confirm').val();
        var parent_case = $('#id_parent_individual_case_number').val();
        var parent_case_confirm = $('#id_parent_individual_case_number_confirm').val();
        var individual_case = $('#id_individual_case_number').val();
        var individual_case_confirm = $('#id_individual_case_number_confirm').val();
        var recorded = $('#id_recorded_number').val();
        var recorded_confirm = $('#id_recorded_number_confirm').val();
        var parent_syrian = $('#id_parent_syrian_national_number').val();
        var parent_syrian_confirm = $('#id_parent_syrian_national_number_confirm').val();
        var syrian = $('#id_syrian_national_number').val();
        var syrian_confirm = $('#id_syrian_national_number_confirm').val();
        var parent_sop = $('#id_parent_sop_national_number').val();
        var parent_sop_confirm = $('#id_parent_sop_national_number_confirm').val();
        var sop = $('#id_sop_national_number').val();
        var sop_confirm = $('#id_sop_national_number_confirm').val();
        var parent_nat = $('#id_parent_national_number').val();
        var parent_nat_confirm = $('#id_parent_national_number_confirm').val();
        var nat = $('#id_national_number').val();
        var nat_confirm = $('#id_national_number_confirm').val();
        var parent_other = $('#id_parent_other_number').val();
        var parent_other_confirm = $('#id_parent_other_number_confirm').val();
        var other = $('#id_other_number').val();
        var other_confirm = $('#id_other_number_confirm').val();
        var parent_extract = $('#id_parent_extract_record').val();
        var parent_extract_confirm = $('#id_parent_extract_record_confirm').val();

        if (id_type == '1') {
            if (case_number === '') {
                $('#id_case_number').addClass('error-field');
                valid = false;
            }
            if (case_number !== case_confirm) {
                $('#id_case_number_confirm').addClass('error-field');
                valid = false;
            }
            if (parent_case !== parent_case_confirm) {
                $('#id_parent_individual_case_number_confirm').addClass('error-field');
                valid = false;
            }
            if (individual_case !== individual_case_confirm) {
                $('#id_individual_case_number_confirm').addClass('error-field');
                valid = false;
            }
        }
        if (id_type == '2') {
            if (recorded === '') {
                $('#id_recorded_number').addClass('error-field');
                valid = false;
            }
            if (recorded !== recorded_confirm) {
                $('#id_recorded_number_confirm').addClass('error-field');
                valid = false;
            }
        }
        if (id_type == '3') {
            if (parent_syrian === '' || parent_syrian.length !== 11) {
                $('#id_parent_syrian_national_number').addClass('error-field');
                valid = false;
            }
            if (parent_syrian_confirm === '' || parent_syrian_confirm.length !== 11) {
                $('#id_parent_syrian_national_number_confirm').addClass('error-field');
                valid = false;
            }
            if (parent_syrian !== parent_syrian_confirm) {
                $('#id_parent_syrian_national_number_confirm').addClass('error-field');
                valid = false;
            }
            if (syrian !== syrian_confirm) {
                $('#id_syrian_national_number_confirm').addClass('error-field');
                valid = false;
            }
        }
        if (id_type == '4') {
            if (parent_sop === '') {
                $('#id_parent_sop_national_number').addClass('error-field');
                valid = false;
            }
            if (parent_sop_confirm === '') {
                $('#id_parent_sop_national_number_confirm').addClass('error-field');
                valid = false;
            }
            if (parent_sop !== parent_sop_confirm) {
                $('#id_parent_sop_national_number_confirm').addClass('error-field');
                valid = false;
            }
            if (sop !== sop_confirm) {
                $('#id_sop_national_number_confirm').addClass('error-field');
                valid = false;
            }
        }
        if (id_type == '5') {
            if (parent_nat && parent_nat.length !== 12) {
                $('#id_parent_national_number').addClass('error-field');
                valid = false;
            }
            if (parent_nat_confirm && parent_nat_confirm.length !== 12) {
                $('#id_parent_national_number_confirm').addClass('error-field');
                valid = false;
            }
            if (parent_nat !== parent_nat_confirm) {
                $('#id_parent_national_number_confirm').addClass('error-field');
                valid = false;
            }
            if (nat !== nat_confirm) {
                $('#id_national_number_confirm').addClass('error-field');
                valid = false;
            }
        }
        if (id_type == '6') {
            if (parent_other === '') {
                $('#id_parent_other_number').addClass('error-field');
                valid = false;
            }
            if (parent_other_confirm === '') {
                $('#id_parent_other_number_confirm').addClass('error-field');
                valid = false;
            }
            if (parent_other !== parent_other_confirm) {
                $('#id_parent_other_number_confirm').addClass('error-field');
                valid = false;
            }
            if (other !== other_confirm) {
                $('#id_other_number_confirm').addClass('error-field');
                valid = false;
            }
        }
        if (id_type == '9') {
            if (parent_extract !== parent_extract_confirm) {
                $('#id_parent_extract_record_confirm').addClass('error-field');
                valid = false;
            }
        }

        if ($('#id_caregiver_mother_name').val() === '') {
            $('#id_child_living_arrangement').addClass('error-field');
            $('#id_cash_support_programmes').addClass('error-field');
            valid = false;
        }
    }
    return valid;
}

$(document).ready(function() {
    $('form').on('submit', function(e) {
        if (!validateMainForm()) {
            e.preventDefault();
            $('#formErrorModal').modal('show');
        }
    });
});

