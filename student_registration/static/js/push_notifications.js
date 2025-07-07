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
            var file = payload.data.file;
            var link = '/MSCC/export-download/' + file + '/';
            $('#downloadLink').attr('href', link);
            var message = 'Your export file is ready.';
            if(payload.notification && payload.notification.body){
                message = payload.notification.body;
                $('#downloadModalMessage').text(message);
            }
            $('#downloadModal').modal('show');

            var itemHtml = '<div class="vertical-timeline-item dot-success vertical-timeline-element">' +
                '<div><span class="vertical-timeline-element-icon bounce-in"></span>' +
                '<div class="vertical-timeline-element-content bounce-in">' +
                '<h4 class="timeline-title"><a href="' + link + '" target="_blank">' + message + '</a></h4>' +
                '</div></div></div>';
            $('#notificationList').prepend(itemHtml);
        }
    });
})();
