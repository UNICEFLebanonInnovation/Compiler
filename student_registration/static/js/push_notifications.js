(function(){
    if(!window.firebaseConfig){
        return;
    }
    firebase.initializeApp(window.firebaseConfig);
    const messaging = firebase.messaging();

    function saveToken(token){
        $.ajax({
            method: 'POST',
            url: '/users/save-fcm-token/',
            headers: { 'X-CSRFToken': getCookie('csrftoken') },
            data: { token: token }
        });
    }

    messaging.getToken({vapidKey: window.firebaseVapidKey}).then(function(token){
        if(token){
            saveToken(token);
        }
    }).catch(function(err){
        console.log('FCM token error', err);
    });

    messaging.onMessage(function(payload){
        if(payload.data && payload.data.file){
            $('#downloadLink').attr('href', '/MSCC/export-download/' + payload.data.file + '/');
            if(payload.notification && payload.notification.body){
                $('#downloadModalMessage').text(payload.notification.body);
            }
            $('#downloadModal').modal('show');
        }
    });
})();
