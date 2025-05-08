
$(document).ready(function() {
    $("#submit-id-save").click(function(e){
        $(this).prop('disabled', true);
        $('form').submit();
    });

    $(document).on('click', '#next-page', function(e){
        $(this).removeClass('error-field');
        var error_fields = false;
        $('input, select').filter('[required]:visible').each(function(){
            e.preventDefault();
            if($(this).val() == null || $(this).val() == ''){
                $(this).addClass('error-field');
                error_fields = true;
            }
        });
        if(!error_fields){
            $('#next-btn22').trigger('click');
            $(this).removeClass('error-field');
         }else{
            $('#formErrorModal').modal('show');
         }
    });
});

