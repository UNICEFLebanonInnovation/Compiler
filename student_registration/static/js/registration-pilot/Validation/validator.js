function ValidateHouseHoldUpdate()
{
     var result = true;

     if($("#changeOption").val() == "phone")
     {
        result = ValidatePhone();
     }

     return result;
}

function ValidatePhone()
{
    var result = true;

    var primary_phone = $("#primary_phone").val();
    var secondary_phone = $("#secondary_phone").val();

    var primary_phone_answered = $("#primary_phone_answered").val();
    var secondary_phone_answered  = $("#secondary_phone_answered").val();

    var isPrimaryValid = ValidatePhoneNumber(primary_phone);
    if (!isPrimaryValid)
    {
        $("#primary_phone_length_error").show();
    }
    else
    {
        $("#primary_phone_length_error").hide();
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


    var isSecondaryValid = ValidatePhoneNumber(secondary_phone) || secondary_phone == '' ;
    if (!isSecondaryValid)
    {
        $("#secondary_phone_length_error").show();
    }
    else
    {
        $("#secondary_phone_length_error").hide();
    }

    var is_secondary_answered_valid =secondary_phone_answered!=null || secondary_phone == ''
    if (!is_secondary_answered_valid)
    {
        $("#secondary_phone_answered_error").show();
    }
    else
    {
        $("#secondary_phone_answered_error").hide();
    }


    result = result && isPrimaryValid;
    result = result && is_primary_answered_valid;
    result = result && isSecondaryValid;
    result = result && is_secondary_answered_valid ;

    return result;
}

function ValidatePhoneNumber(phoneNumber)
{
   return /^[0-9]{8}$/i.test(phoneNumber);
}
