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

    result = result && ValidatePhoneNumber(primary_phone);
    result = result && (ValidatePhoneNumber(secondary_phone) || secondary_phone == '' );

    result = result && (primary_phone_answered!=null);

    result = result && (secondary_phone_answered!=null || secondary_phone == ''  );

    return result;
}

function ValidatePhoneNumber(phoneNumber)
{
   return /^[0-9]{8}$/i.test(phoneNumber);
}
