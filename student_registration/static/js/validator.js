/**
 * Created by Ali on 2016-09-12.
 */

var validation_mapping = new Array();

function validateSection(frame, sectionIndex)
{
    var result = true;

    if(sectionIndex.toString() in validation_mapping)
    {
        var callback  = validation_mapping[sectionIndex];
        result = callback();
    }
    return result;
}
function validateSection0()
{
    var valid = true ;

    if($('#id_school').val() == ""){
            $('#school_error').show();
            valid = false ;
        }else{
            $('#school_error').hide();
        }
    return valid;
}

function validateSection5()
{
    var valid = true ;
    var selectedOption = $("#id_id_type").val();

    valid = validateTextBoxRequired('id_nationality','nationality_error',valid);
    valid = validateTextBoxRequired('id_id_type','id_type_error',valid)

    if(selectedOption == 1) {
         valid = validateTextBoxRequired('id_id_number','id_number_UNHCR_Other_error',valid);
         valid = validateUNCHRFormat(valid);
    }else if (selectedOption == 2 || selectedOption == 3 || selectedOption == 4|| selectedOption == 5) {
        valid = validateTextBoxRequired('id_id_number','id_number_UNHCR_Other_error',valid);
    }else if (selectedOption == 6) {
    }
    valid = validateTextBoxRequired('id_first_name','first_name_error',valid);
    valid = validateTextBoxRequired('id_father_name','father_name_error',valid);
    valid = validateTextBoxRequired('id_last_name','last_name_error',valid);
    valid = validateTextBoxRequired('id_mother_fullname','mother_fullname_error',valid);
    valid = validateTextBoxRequired('id_age','age_error',valid);
    valid = validateTextBoxRequired('id_sex','gender_error',valid);
    valid = validateTextBoxRequired('id_relation_to_householdhead','relationship_householdhead_error',valid);
    return valid;
}
function validateSection13()
{
    var valid = true ;
        valid = validateTextBoxRequired('id_address','address_error',valid);
        valid = validateTextBoxRequired('id_primary_phone','primary_phone_error',valid);
        valid = validateTextBoxRequired('id_primary_phone_answered','primary_phone_answered_error',valid);
    return valid;
}

function validateUNCHRFormat( isValid)
{
    return validateCondition('id_number_UNHCR_Other_format_error', isValid, validateUNHCRNumber());
}

function validateChildUNCHRFormat(form,id, errorID, isValid)
{
    // return validateCondition( form.find('#'+errorID), isValid, validate_child_UNHCRNumber(form.find('#'+id)));
    var valid = isValid;
    if(!validate_child_UNHCRNumber(form.find('#'+id))){
            form.find('#'+errorID).show();
            valid = false ;
        }else{
            form.find('#'+errorID).hide();
    }
    return valid;

}

function validate_waiting_list()
{
    var valid = true ;
        valid = validateTextBoxRequired('id_address','address_error',valid);
        valid = validateTextBoxRequired('id_primary_phone','primary_phone_error',valid);
        valid = validateTextBoxRequired('id_primary_phone_answered','primary_phone_answered_error',valid);
    return valid;
}


function validateCondition(errorID, isValid, validationResult)
{
    var valid = isValid;
    if(!validationResult){
            $('#'+errorID).show();
            valid = false ;
        }else{
            $('#'+errorID).hide();
    }
    return valid;
}
function validateUNHCRNumber()
{
    var validrecorded =  /^LEB-1[5-7][C]\d{5}$/i.test($('#id_id_number').val());
    var validregistered = /^[0-9]{3}-1[1-6][C]\d{5}$/i.test($('#id_id_number').val());

    // for recorded: LEB-1[5-7][C]\d{5}
    // for registered: \d{3}-1[1-5][C]\d{5}
    // return /^[0-9]{3}-1[1-5][C]\d{5}$/i.test($('#id_id_number').val());
    return validrecorded || validregistered;
}
function validate_child_UNHCRNumber(id)
{
    return /^[0-9]{3}-[0-9]{8}$/i.test(id.val());
}

function validateTextBoxRequired(id, errorID, isValid)
{
    return validateCondition(errorID, isValid, $('#'+id).val() != "");
}

function validate_add_child_noid()
{
    var valid = true ;
    var selectedOption = $("#id_id_type").val();
    var form = $('.bootbox-body').find('#add_child_noid_form');
    if(selectedOption == 1) {
        valid = validateTextBox(form,'id_id_number','id_number_error',valid);
        valid = validateChildUNCHRFormat(form,'id_id_number','number_UNHCR_format_error', valid);
    }
    valid = validateTextBox(form,'id_first_name','first_name_error',valid);
    valid = validateTextBox(form,'id_father_name','father_name_error',valid);
    valid = validateTextBox(form,'id_last_name','last_name_error',valid);
    valid = validateTextBox(form,'id_mother_fullname','mother_fullname_error',valid);
    valid = validateTextBox(form,'id_age','age_error',valid);
    valid = validateTextBox(form,'id_sex','gender_error',valid);
    valid = validateTextBox(form,'id_relation_to_adult','relation_to_adult_error',valid);
    return valid;
 }

function validate_add_child_withid()
{
    var valid = true ;
    var form = $('.bootbox-body').find('#add_child_withid_form');

    valid = validateTextBox(form,'id_id_number','id_number_error',valid);
    valid = validateTextBox(form,'id_relation_to_adult','relation_to_household_reprentative_error',valid);
    return valid;
}

function validateTextBox(form,id, errorID, isValid)
{
    var valid = isValid;
    if(form.find('#'+id).val() == ""){
            form.find('#'+errorID).show();
            valid = false ;
        }else{
            form.find('#'+errorID).hide();
    }
    return valid;
}


function checkArabicOnly(field)
{
    checkFieldCharacters
    (
        field,
        function(ch)
        {
            var c = ch.charCodeAt(0);
            return !((c < 1536 || c > 1791) && ch != " ");
        }
    );
}


function checkFieldCharacters(field,characterCheck)
{
    var sNewVal = "";

    var sFieldVal = field.val();

    for(var i = 0; i < sFieldVal.length; i++) {

        var ch = sFieldVal.charAt(i);

        if(!characterCheck(ch)) {
            // Discard
        }

        else {
            sNewVal += ch;
        }
    }

    if(field.val() != sNewVal) {
        field.val(sNewVal);
    }
}
function checkIsNumber(field)
{
    checkFieldCharacters
    (
        field,
        function(ch)
        {
            return checkCharacterIsNumber(ch);
        }
    );
}

function checkCharacterIsNumber(fieldValue)
{
    return /^[0-9]+$/.test(fieldValue);


}



