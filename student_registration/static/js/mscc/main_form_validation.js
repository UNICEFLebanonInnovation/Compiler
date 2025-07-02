// Client-side validation for MSCC MainForm with realtime feedback

function clearErrors() {
    $('.error-field').removeClass('error-field');
    $('.field-error').remove();
}

function showError(selector, message) {
    var field = $(selector);
    field.addClass('error-field');
    var errorEl = field.next('.field-error');
    if (!errorEl.length) {
        errorEl = $('<div class="help-block field-error"></div>');
        errorEl.insertAfter(field);
    }
    errorEl.text(message);
}

function validateMainForm(showModal) {
    if (showModal === undefined) showModal = true;
    var valid = true;
    clearErrors();

    // Date validation
    var year = parseInt($('#id_child_birthday_year').val()) || 0;
    var month = parseInt($('#id_child_birthday_month').val()) || 0;
    var day = parseInt($('#id_child_birthday_day').val()) || 0;
    if (year && month && day) {
        var dt = new Date(year, month - 1, day);
        if (dt.getFullYear() !== year || dt.getMonth() !== month - 1 || dt.getDate() !== day) {
            showError('#id_child_birthday_year', 'The date is not valid.');
            valid = false;
        }
    } else {
        showError('#id_child_birthday_year', 'The date is not valid.');
        valid = false;
    }

    // Child nationality other
    if ($('#id_child_nationality').val() == '6' && $('#id_child_nationality_other').val() === '') {
        showError('#id_child_nationality_other', 'This field is required');
        valid = false;
    }

    // Child have children
    if ($('#id_child_have_children').val() == 'Yes' && $('#id_child_children_number').val() === '') {
        showError('#id_child_children_number', 'This field is required');
        valid = false;
    }

    // Child have sibling
    if ($('#id_child_have_sibling').val() == 'Yes' && $('#id_child_siblings_have_disability').val() === '') {
        showError('#id_child_siblings_have_disability', 'This field is required');
        valid = false;
    }

    // Source of identification
    if ($('#id_source_of_identification').val() == 'Other Sources' && $('#id_source_of_identification_specify').val() === '') {
        showError('#id_source_of_identification_specify', 'This field is required');
        valid = false;
    }

    var package_type = $('#id_type').val();
    if (package_type == 'Core-Package') {
        if ($('#id_father_educational_level').val() === '') {
            showError('#id_father_educational_level', 'This field is required');
            valid = false;
        }
        if ($('#id_mother_educational_level').val() === '') {
            showError('#id_mother_educational_level', 'This field is required');
            valid = false;
        }
        var first_phone = $('#id_first_phone_number').val();
        var first_phone_confirm = $('#id_first_phone_number_confirm').val();
        if ($('#id_first_phone_owner').val() === '') {
            showError('#id_first_phone_owner', 'This field is required');
            valid = false;
        }
        if (first_phone !== first_phone_confirm) {
            showError('#id_first_phone_number_confirm', 'The phone numbers are not matched');
            valid = false;
        }
        var second_phone = $('#id_second_phone_number').val();
        var second_phone_confirm = $('#id_second_phone_number_confirm').val();
        if (second_phone !== second_phone_confirm) {
            showError('#id_second_phone_number_confirm', 'The phone numbers are not matched');
            valid = false;
        }
        var main_caregiver = $('#id_main_caregiver').val();
        if (main_caregiver === '') {
            showError('#id_main_caregiver', 'This field is required');
            valid = false;
        }
        if (main_caregiver == 'Other' && $('#id_main_caregiver_other').val() === '') {
            showError('#id_main_caregiver_other', 'This field is required');
            valid = false;
        }
        if ($('#id_main_caregiver_nationality').val() == '6' && $('#id_main_caregiver_nationality_other').val() === '') {
            showError('#id_main_caregiver_nationality_other', 'This field is required');
            valid = false;
        }
        if ($('#id_children_number_under18').val() === '') {
            showError('#id_children_number_under18', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_first_name').val() === '') {
            showError('#id_caregiver_first_name', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_middle_name').val() === '') {
            showError('#id_caregiver_middle_name', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_last_name').val() === '') {
            showError('#id_caregiver_last_name', 'This field is required');
            valid = false;
        }
        if ($('#id_caregiver_mother_name').val() === '') {
            showError('#id_caregiver_mother_name', 'This field is required');
            valid = false;
        }
        var have_labour = $('#id_have_labour').val();
        if (have_labour === '') {
            showError('#id_have_labour', 'This field is required');
            valid = false;
        }
        if (have_labour != 'No') {
            if ($('#id_labour_type').val() === '') {
                showError('#id_labour_type', 'This field is required');
                valid = false;
            } else if ($('#id_labour_type').val() == 'Other services' && $('#id_labour_type_specify').val() === '') {
                showError('#id_labour_type_specify', 'This field is required');
                valid = false;
            }
            if ($('#id_labour_hours').val() === '') {
                showError('#id_labour_hours', 'This field is required');
                valid = false;
            }
            if ($('#id_labour_weekly_income').val() === '') {
                showError('#id_labour_weekly_income', 'This field is required');
                valid = false;
            }
            if ($('#labour_condition').val() === '') {
                showError('#labour_condition', 'This field is required');
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
                showError('#id_case_number', 'This field is required');
                valid = false;
            }
            if (case_number !== case_confirm) {
                showError('#id_case_number_confirm', 'The case numbers are not matched');
                valid = false;
            }
            if (parent_case !== parent_case_confirm) {
                showError('#id_parent_individual_case_number_confirm', 'The individual case numbers are not matched');
                valid = false;
            }
            if (individual_case !== individual_case_confirm) {
                showError('#id_individual_case_number_confirm', 'The individual case numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '2') {
            if (recorded === '') {
                showError('#id_recorded_number', 'This field is required');
                valid = false;
            }
            if (recorded !== recorded_confirm) {
                showError('#id_recorded_number_confirm', 'The recorded numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '3') {
            if (parent_syrian === '' || parent_syrian.length !== 11) {
                showError('#id_parent_syrian_national_number', 'Please enter a valid number (11 digits)');
                valid = false;
            }
            if (parent_syrian_confirm === '' || parent_syrian_confirm.length !== 11) {
                showError('#id_parent_syrian_national_number_confirm', 'Please enter a valid number (11 digits)');
                valid = false;
            }
            if (parent_syrian !== parent_syrian_confirm) {
                showError('#id_parent_syrian_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
            if (syrian !== syrian_confirm) {
                showError('#id_syrian_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '4') {
            if (parent_sop === '') {
                showError('#id_parent_sop_national_number', 'This field is required');
                valid = false;
            }
            if (parent_sop_confirm === '') {
                showError('#id_parent_sop_national_number_confirm', 'This field is required');
                valid = false;
            }
            if (parent_sop !== parent_sop_confirm) {
                showError('#id_parent_sop_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
            if (sop !== sop_confirm) {
                showError('#id_sop_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '5') {
            if (parent_nat && parent_nat.length !== 12) {
                showError('#id_parent_national_number', 'Please enter a valid number (12 digits)');
                valid = false;
            }
            if (parent_nat_confirm && parent_nat_confirm.length !== 12) {
                showError('#id_parent_national_number_confirm', 'Please enter a valid number (12 digits)');
                valid = false;
            }
            if (parent_nat !== parent_nat_confirm) {
                showError('#id_parent_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
            if (nat !== nat_confirm) {
                showError('#id_national_number_confirm', 'The national numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '6') {
            if (parent_other === '') {
                showError('#id_parent_other_number', 'This field is required');
                valid = false;
            }
            if (parent_other_confirm === '') {
                showError('#id_parent_other_number_confirm', 'This field is required');
                valid = false;
            }
            if (parent_other !== parent_other_confirm) {
                showError('#id_parent_other_number_confirm', 'The ID numbers are not matched');
                valid = false;
            }
            if (other !== other_confirm) {
                showError('#id_other_number_confirm', 'The ID numbers are not matched');
                valid = false;
            }
        }
        if (id_type == '9') {
            if (parent_extract !== parent_extract_confirm) {
                showError('#id_parent_extract_record_confirm', 'The Parent Extract Record are not matched');
                valid = false;
            }
        }

        if ($('#id_caregiver_mother_name').val() === '') {
            showError('#id_child_living_arrangement', 'This field is required');
            showError('#id_cash_support_programmes', 'This field is required');
            valid = false;
        }
    }
    return valid;
}

$(document).ready(function() {
    $('form').on('submit', function(e) {
        if (!validateMainForm(true)) {
            e.preventDefault();
        }
    });

    $('input, select').on('change input blur', function() {
        validateMainForm(false);
    });
});
