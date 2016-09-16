/**
 * Created by Ali on 2016-09-12.
 */

var validation_mapping = new Array();

function validateSection(frame, sectionIndex)
{
    var result = true;

    if(sectionIndex.toString() in validation_mapping)
    {
        console.log(validation_mapping[sectionIndex]);
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
    }else if (selectedOption == 2 || selectedOption == 3 || selectedOption == 4|| selectedOption == 5) {
        valid = validateTextBoxRequired('id_id_number','id_number_UNHCR_Other_error',valid);
        valid = validateTextBoxRequired('id_first_name','first_name_error',valid);
        valid = validateTextBoxRequired('id_father_name','father_name_error',valid);
        valid = validateTextBoxRequired('id_last_name','last_name_error',valid);
        valid = validateTextBoxRequired('id_mother_fullname','mother_fullname_error',valid);
        valid = validateTextBoxRequired('id_age','age_error',valid);
        valid = validateTextBoxRequired('id_sex','gender_error',valid);
        valid = validateTextBoxRequired('id_relation_to_householdhead','relationship_householdhead_error',valid);
    }else if (selectedOption == 6) {
        valid = validateTextBoxRequired('id_first_name','first_name_error',valid);
        valid = validateTextBoxRequired('id_father_name','father_name_error',valid);
        valid = validateTextBoxRequired('id_last_name','last_name_error',valid);
        valid = validateTextBoxRequired('id_mother_fullname','mother_fullname_error',valid);
        valid = validateTextBoxRequired('id_age','age_error',valid);
        valid = validateTextBoxRequired('id_sex','gender_error',valid);
        valid = validateTextBoxRequired('id_relation_to_householdhead','relationship_householdhead_error',valid);
    }
    return valid;
}

function validateTextBoxRequired(id, errorID, isValid)
{
    var valid = isValid;
    if($('#'+id).val() == ""){
            $('#'+errorID).show();
            valid = false ;
        }else{
            $('#'+errorID).hide();
    }
    return valid;
}

function validate_add_child_noid()
{
    var valid = true ;
    var form = $('.bootbox-body').find('#add_child_noid_form');
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
    var sNewVal = "";

    var sFieldVal = field.val();

    for(var i = 0; i < sFieldVal.length; i++) {

        var ch = sFieldVal.charAt(i);

        var c = ch.charCodeAt(0);

        if((c < 1536 || c > 1791) && ch != " ") {
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
