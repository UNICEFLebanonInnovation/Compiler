/**
 * Created by Ali on 2016-09-12.
 */

var validation_mapping = new Array();

function validateSection(frame, sectionIndex)
{
    var result = true;
    //$('.error').hide();

    if(sectionIndex in validation_mapping)
    {
        console.log(validation_mapping[sectionIndex]);
        var callback  = validation_mapping[sectionIndex];
        result = callback();
    }

    //frame.next();

    //return result;
    return false;
}

function validateSection6()
{
    var selectedOption = $("#id_id_type").val();

    if(selectedOption == 1) {

    }else if (selectedOption == 2 || selectedOption == 3 || selectedOption == 4|| selectedOption == 5) {
        $('#first_name_error').show();
        $('#father_name_error').show();
        return false;

    }else if (selectedOption == 6) { }

    return true;
}


function ValidateTextBoxMaximumSize(validationResult, message, id, size)
{
    return ValidateField
    (
            validationResult,
            message,
            id,
            function(id)
            {
                return $('#'+id).val().length <= size
            }
    );

    return validationResult;
}

function ValidateTextBoxRequired(validationResult, message, id)
{
    return ValidateField
    (
            validationResult,
            message,
            id,
            function(id)
            {
                return $('#'+id).val()!=""
            }
    );

    return validationResult;
}

function ValidateField(validationResult, message, id, isValidFunction)
{
    var isFieldValid = isValidFunction(id);

    if(!isFieldValid)
    {
        validationResult.ValidationMessage += message+"<br/>";
    }

    validationResult.IsValid = validationResult.IsValid && isFieldValid;

    return validationResult;
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
