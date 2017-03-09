
function ValidateHouseHoldNotFound()
{
     var result = true;



     return result;
}

function ValidateHouseHoldUpdate()
{
     var result = true;

     if($("#changeOption").val() == "phone")
     {
        result = ValidatePhone();
     }
      else if($("#changeOption").val() == "beneficiary")
     {
        result = validate_beneficiary();
     }
     else if($("#changeOption").val() == "twoCards")
     {
         result = ValidateTwoCard();
     }
     else if($("#changeOption").val() == "cardStatus")
     {
         result = ValidateCardPhone();
     }
     else if($("#changeOption").val() == "address")
     {
         result = validateTextBoxRequired('address','address_error',result);
     }
     else if($("#changeOption").val() == "refusedServiceBLF")
     {
         result = validateTextBoxRequired('complaint_bank_phone_used','complaint_bank_phone_used_error',result);
         result = validateTextBoxRequired('complaint_bank_service_requested','complaint_bank_service_requested_error',result);
     }

     return result;
}

function HideAllErrors()

{
    $("#address_error").hide();
    $("#complaint_bank_phone_used_error").hide();
    $("#complaint_bank_service_requested_error").hide();
    $("#complaint_error").hide();
    $("#first_card_case_number_error").hide();
    $("#first_card_case_number_confirm_error").hide();
    $("#first_card_case_equal_error").hide();
    $("#first_card_last_four_digits_error").hide();
    $("#second_card_case_number_error").hide();
    $("#second_card_case_equal_error").hide();
    $("#second_card_case_number_confirm_error").hide();
    $("#second_card_last_four_digits_error").hide();
    $("#beneficiary_phone_length_error").hide();
    $("#beneficiary_phone_confirm_length_error").hide();
    $("#beneficiary_phone_confirm_error").hide();
    $("#dob_error").hide();
    $("#beneficiary_id_number_error").hide();
    $("#first_name_error").hide();
    $("#father_name_error").hide();
    $("#last_name_error").hide();
    $("#mother_full_name_error").hide();
    $("#reason_error").hide();
    $("#reason_error").hide();
    $("#relation_to_householdhead_error").hide();
    $("#gender_error").hide();
    $("#idType_error").hide();
    $("#primary_phone_length_error").hide();
    $("#primary_phone_confirm_length_error").hide();
    $("#primary_phone_confirm_error").hide();
    $("#primary_phone_answered_error").hide();
    $("#secondary_phone_length_error").hide();
    $("#secondary_phone_confirm_length_error").hide();
    $("#secondary_phone_confirm_error").hide();
    $("#secondary_phone_answered_error").hide();
    $("#card_phone_confirm_length_error").hide();
    $("#card_phone_confirm_error").hide();
}


function ValidateComplaint()
{
     var result = true;
     result = validateTextBoxRequired('complaint','complaint_error',result);
     return result;
}

function ValidateTwoCard()
{
    var result = true;

    var first_card_case_number = $("#first_card_case_number").val();
    var first_card_case_number_confirm = $("#first_card_case_number_confirm").val();
    var first_card_last_four = $("#first_card_last_four_digits").val();

    var second_card_case_number = $("#second_card_case_number").val();
    var second_card_case_number_confirm = $("#second_card_case_number_confirm").val();
    var second_card_last_four = $("#secondcard_last_four_digits").val();

    var is_valid_first_card_last_four = ValidateFourDigits(first_card_last_four);
    var is_valid_second_card_last_four = ValidateFourDigits(second_card_last_four);



    var isFirstCardValid = ValidateCardCaseNumber(first_card_case_number)
    var isFirstCardConfirmValid = ValidateCardCaseNumber(first_card_case_number_confirm);
    var isFirstEqualValid= first_card_case_number == first_card_case_number_confirm;

    if (!isFirstCardValid)
    {
        $("#first_card_case_number_error").show();
    }
    else
    {
        $("#first_card_case_number_error").hide();
    }

    if (!isFirstCardConfirmValid)
    {
        $("#first_card_case_number_confirm_error").show();
        $("#first_card_case_equal_error").hide();
    }
    else
    {
        $("#first_card_case_number_confirm_error").hide();
        if (!isFirstEqualValid)
        {
            $("#first_card_case_equal_error").show();
        }
        else
        {
            $("#first_card_case_equal_error").hide();
        }
    }

    if (!is_valid_first_card_last_four)
    {
        $("#first_card_last_four_digits_error").show();
    }
    else
    {
        $("#first_card_last_four_digits_error").hide();
    }



    var isSecondCardValid = ValidateCardCaseNumber(second_card_case_number)
    var isSecondCardConfirmValid = ValidateCardCaseNumber(second_card_case_number_confirm);
    var isSecondEqualValid= second_card_case_number == second_card_case_number_confirm;

    if (!isSecondCardValid)
    {
        $("#second_card_case_number_error").show();
    }
    else
    {
        $("#second_card_case_number_error").hide();
    }

    if (!isSecondCardConfirmValid)
    {
        $("#second_card_case_number_confirm_error").show();
        $("#second_card_case_equal_error").hide();
    }
    else
    {
        $("#second_card_case_number_confirm_error").hide();
        if (!isSecondEqualValid)
        {
            $("#second_card_case_equal_error").show();
        }
        else
        {
            $("#second_card_case_equal_error").hide();
        }
    }


    if (!is_valid_second_card_last_four)
    {
        $("#second_card_last_four_digits_error").show();
    }
    else
    {
        $("#second_card_last_four_digits_error").hide();
    }



    result = result && isFirstCardValid;
    result = result && isFirstCardConfirmValid;
    result = result && isFirstEqualValid;
    result = result && isSecondCardValid;
    result = result && isSecondCardConfirmValid;
    result = result && isSecondEqualValid;
    result = result && is_valid_first_card_last_four;
    result = result && is_valid_second_card_last_four;

    return result;


}


function validate_beneficiary()
{
    var result = true;

    var phone = $("#beneficiary_phone").val();
    var phone_confirm = $("#beneficiary_phone_confirm").val();
    var id_number = $("#id_number").val();
    var id_type = $("#idType").val();

    var isPhoneValid = ValidatePhoneNumber(phone)
    var isPhoneConfirmValid = ValidatePhoneNumber(phone_confirm);
    var isPhoneEqualValid= phone == phone_confirm;
    if (!isPhoneValid)
    {
        $("#beneficiary_phone_length_error").show();
    }
    else
    {
        $("#beneficiary_phone_length_error").hide();
    }

    if (!isPhoneConfirmValid)
    {
        $("#beneficiary_phone_confirm_length_error").show();
        $("#beneficiary_phone_confirm_error").hide();
    }
    else
    {
        $("#beneficiary_phone_confirm_length_error").hide();
        if (!isPhoneEqualValid)
        {
            $("#beneficiary_phone_confirm_error").show();
        }
        else
            {
                $("#beneficiary_phone_confirm_error").hide();
            }
    }

    var isDOBValid = true;
    if($("#days").val() && $("#months").val() && $("#years").val())
    {

        $("#dob_error").hide();
    }
    else
    {
        isDOBValid = false;
        $("#dob_error").show();
    }

    var isNumberValid =  ValidateBeneficiaryID(id_number,id_type);

    result = validateTextBoxRequired('first_name','first_name_error',result);
    result = validateTextBoxRequired('father_name','father_name_error',result);
    result = validateTextBoxRequired('last_name','last_name_error',result);
    result = validateTextBoxRequired('mother_full_name','mother_full_name_error',result);

    var isReasonValid = true;
    if($("#reason").val()==null)
    {
        isReasonValid= false;
        $("#reason_error").show();
    }
    else
    {
        $("#reason_error").hide();
    }

    var isRelation_to_householdheadValid = true;
    if($("#relation_to_householdhead").val()==null)
    {
        isRelation_to_householdheadValid= false;
        $("#relation_to_householdhead_error").show();
    }
    else
    {
        $("#relation_to_householdhead_error").hide();
    }

    var isGenderValid = true;
    if($("#gender").val()==null)
    {
        isRelation_to_householdheadValid= false;
        $("#gender_error").show();
    }
    else
    {
        $("#gender_error").hide();
    }

    var isIdTypeValid = true;
    if($("#idType").val()==null)
    {
        isIdTypeValid= false;
        $("#idType_error").show();
    }
    else
    {
        $("#idType_error").hide();
    }

    result = result && isPhoneValid;
    result = result && isPhoneConfirmValid;
    result = result && isPhoneEqualValid;
    result = result && isNumberValid;
    result = result && isDOBValid;
    result = result && isReasonValid;
    result = result && isRelation_to_householdheadValid;
    result = result && isGenderValid;
    result = result && isIdTypeValid;
    return result;
}

function ValidateBeneficiaryID(id_number , id_type)
{

    var isNumberValid = true;
    if(id_type == 1)
    {
        isNumberValid=  validate_individual_UNHCRNumber(id_number);
        if (!isNumberValid)
        {
            $("#beneficiary_id_number_error").show();
        }
        else
        {
            $("#beneficiary_id_number_error").hide();
        }
    }
    else if (id_number)
    {
        $("#beneficiary_id_number_error").hide();
    }
    else
    {
        $("#beneficiary_id_number_error").show();
        isNumberValid=false;
    }
    return isNumberValid;
}



function ValidatePhone()
{
    var result = true;

    var primary_phone = $("#primary_phone").val();
    var primary_phone_confirm = $("#primary_phone_confirm").val();
    var secondary_phone = $("#secondary_phone").val();
    var secondary_phone_confirm = $("#secondary_phone_confirm").val();
    var primary_phone_answered = $("#primary_phone_answered").val();
    var secondary_phone_answered  = $("#secondary_phone_answered").val();


    var isPrimaryValid = ValidatePhoneNumber(primary_phone)

    if (!isPrimaryValid)
    {
        $("#primary_phone_length_error").show();
    }
    else
    {
        $("#primary_phone_length_error").hide();
    }


    var isPrimaryPhoneConfirmValid = ValidatePhoneNumber(primary_phone_confirm);
    var isPrimaryPhoneEqualValid = primary_phone == primary_phone_confirm;
    if (!isPrimaryPhoneConfirmValid)
    {
        $("#primary_phone_confirm_length_error").show();
         $("#primary_phone_confirm_error").hide();
    }
    else
    {
        $("#primary_phone_confirm_length_error").hide();
        if (!isPrimaryPhoneEqualValid)
        {
            $("#primary_phone_confirm_error").show();
        }
        else
            {
                $("#primary_phone_confirm_error").hide();
            }
    }

    var is_primary_answered_valid =primary_phone_answered!=null;
    if (!is_primary_answered_valid)
    {
        $("#primary_phone_answered_error").show();
    }
    else
    {
        $("#primary_phone_answered_error").hide();
    }

    var isSecondaryValid = ValidatePhoneNumber(secondary_phone) || secondary_phone=='';

    if (!isSecondaryValid)
    {
        $("#secondary_phone_length_error").show();
    }
    else
    {
        $("#secondary_phone_length_error").hide();
    }


    var isSecondaryPhoneConfirmValid = ValidatePhoneNumber(secondary_phone_confirm)  || secondary_phone=='';
    var isSecondaryPhoneEqualValid = secondary_phone == secondary_phone_confirm;
    if (!isSecondaryPhoneConfirmValid)
    {
        $("#secondary_phone_confirm_length_error").show();
        $("#secondary_phone_confirm_error").hide();
    }
    else
    {
        $("#secondary_phone_confirm_length_error").hide();
        if (!isSecondaryPhoneEqualValid)
        {
            $("#secondary_phone_confirm_error").show();
        }
        else
            {
                $("#secondary_phone_confirm_error").hide();
            }
    }

    var is_secondary_answered_valid =secondary_phone_answered!=null || secondary_phone == '';
    if (!is_secondary_answered_valid)
    {
        $("#secondary_phone_answered_error").show();
    }
    else
    {
        $("#secondary_phone_answered_error").hide();
    }


    result = result && isPrimaryValid;
    result = result && isPrimaryPhoneConfirmValid;
    result = result && isPrimaryPhoneEqualValid;
    result = result && is_primary_answered_valid;

    result = result && isSecondaryValid;
    result = result && isSecondaryPhoneConfirmValid;
    result = result && isSecondaryPhoneEqualValid;
    result = result && is_secondary_answered_valid ;

    return result;
}


function ValidateCardPhone()
{
    var result = true;


    if($("#card_distribution_complaint").val() == 12)
     {
         var primary_phone = $("#card_phone").val();
         var primary_phone_confirm = $("#card_phone_confirm").val();


        var isPrimaryValid = ValidatePhoneNumber(primary_phone)

        if (!isPrimaryValid)
        {
            $("#card_phone_length_error").show();
        }
        else
        {
            $("#card_phone_length_error").hide();
        }


        var isPrimaryPhoneConfirmValid = ValidatePhoneNumber(primary_phone_confirm);
        var isPrimaryPhoneEqualValid = primary_phone == primary_phone_confirm;
        if (!isPrimaryPhoneConfirmValid)
        {
            $("#card_phone_confirm_length_error").show();
             $("#card_phone_confirm_error").hide();
        }
        else
        {
            $("#card_phone_confirm_length_error").hide();
            if (!isPrimaryPhoneEqualValid)
            {
                $("#card_phone_confirm_error").show();
            }
            else
                {
                    $("#card_phone_confirm_error").hide();
                }
        }

        result = result && isPrimaryValid;
        result = result && isPrimaryPhoneConfirmValid;
        result = result && isPrimaryPhoneEqualValid;



    }
    return result;
}



function ValidatePhoneNumber(phoneNumber)
{
   return /^[0-9]{8}$/i.test(phoneNumber);
}

function ValidateFourDigits(lastFourDigits)
{
   return /^[0-9]{4}$/i.test(lastFourDigits);
}

function ValidateCardCaseNumber(cardCaseNumber)
{
    var UNHCRValid = validateUNHCRNumber(cardCaseNumber);
    var MValid = /^[0-9]*[M]$/i.test(cardCaseNumber);
    var FValid = /^[0-9]*[F]$/i.test(cardCaseNumber);
   //return /^[0-9]*[M]$/i.test(cardCaseNumber);
     return UNHCRValid || MValid || FValid;

}

function validateUNHCRNumber(cardCaseNumber)
{
    var validrecorded =  /^LEB-1[5-7][C]\d{5}$/i.test(cardCaseNumber);
    var validregistered = /^[0-9]{3}-1[1-6][C]\d{5}$/i.test(cardCaseNumber);
    var validOther =  /^[0-9]{3}-00[C]\d{5}$/i.test(cardCaseNumber);
    // for recorded: LEB-1[5-7][C]\d{5}
    // for registered: \d{3}-1[1-5][C]\d{5}
    // return /^[0-9]{3}-1[1-5][C]\d{5}$/i.test($('#id_id_number').val());
    return validrecorded || validregistered || validOther;
}
function validate_individual_UNHCRNumber(Number)
{
    return /^[0-9]{3}-[0-9]{8}$/i.test(Number);
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


function validateTextBoxRequired(id, errorID, isValid)
{
    return validateCondition(errorID, isValid, $('#'+id).val() != "");
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



