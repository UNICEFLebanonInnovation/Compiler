
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

function checkCharacterIsNumber(fieldValue)
{
    return /^[0-9]+$/.test(fieldValue);
}
function check_unhcr_number(id_number)
{
    return /^((245)|(380)|(568)|(705)|(781)|(909)|(947)|(LEB))-1[1-7][C]\d{5}$/i.text(id_number);
}
function check_national_id(id_number)
{
    return /^[0-9]{11}$/i.test(id_number);
}
