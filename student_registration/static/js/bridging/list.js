$(document).ready(function(){
    $('#select-all-bridging').on('change', function(){
        $('.bridging-select').prop('checked', $(this).is(':checked'));
    });

    $('#register-new-round').on('click', function(e){
        e.preventDefault();
        var ids = [];
        $('.bridging-select:checked').each(function(){
            ids.push($(this).val());
        });
        if(ids.length === 0){
            alert('No children selected');
            return;
        }
        if(!confirm('Register selected children in new round?')){
            return;
        }
        requestHeaders = getHeader();
        requestHeaders['content-type'] = 'application/json';
        $.ajax({
            url: '/clm/bridging-new-round/',
            type: 'POST',
            data: JSON.stringify({ids: ids}),
            headers: requestHeaders,
            success: function(){
                location.reload();
            },
            error: function(){
                alert('Error registering students');
            }
        });
    });
});
