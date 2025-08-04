// firebase-messaging.js
// Replace 'YOUR_VAPID_KEY_HERE' with your VAPID key from Firebase Console → Project Settings → Cloud Messaging
import { initializeApp } from "https://www.gstatic.com/firebasejs/12.0.0/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/12.0.0/firebase-messaging.js";

// Firebase config (same as the one you posted)
const firebaseConfig = {
  apiKey: "AIzaSyAL2iS7YCesCURrxFViKUzH8LOrDzDIPHg",
  authDomain: "leb-bma.firebaseapp.com",
  projectId: "leb-bma",
  storageBucket: "leb-bma.firebasestorage.app",
  messagingSenderId: "455115377412",
  appId: "1:455115377412:web:1e39a332cd97f98e009e51",
  measurementId: "G-1QPVEZK990"
};

// Initialize Firebase
const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);

// Request permission and get FCM token
Notification.requestPermission().then(permission => {
  if (permission === "granted") {
    getToken(messaging, { vapidKey: 'YOUR_VAPID_KEY_HERE' }).then((token) => {
      // Send token to Django backend
      fetch('/api/save-fcm-token/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ token: token })
      });
    }).catch(err => {
      console.error("Token error:", err);
    });
  }
});


// firebase-messaging-sw.js
importScripts("https://www.gstatic.com/firebasejs/12.0.0/firebase-app-compat.js");
importScripts("https://www.gstatic.com/firebasejs/12.0.0/firebase-messaging-compat.js");

// Initialize Firebase in the Service Worker
firebase.initializeApp({
  apiKey: "AIzaSyAL2iS7YCesCURrxFViKUzH8LOrDzDIPHg",
  authDomain: "leb-bma.firebaseapp.com",
  projectId: "leb-bma",
  storageBucket: "leb-bma.firebasestorage.app",
  messagingSenderId: "455115377412",
  appId: "1:455115377412:web:1e39a332cd97f98e009e51",
  measurementId: "G-1QPVEZK990"
});

const messaging = firebase.messaging();

messaging.onBackgroundMessage((payload) => {
  console.log('[firebase-messaging-sw.js] Received background message ', payload);
  const notificationTitle = payload.notification.title;
  const notificationOptions = {
    body: payload.notification.body,
    icon: '/static/images/logo.png'  // Optional icon
  };

  self.registration.showNotification(notificationTitle, notificationOptions);
});


// Listen to foreground messages
onMessage(messaging, (payload) => {
  console.log("Message received in foreground:", payload);
  const { title, body } = payload.notification;
  new Notification(title, {
    body: body,
    icon: '/static/images/logo.png'
  });
});


getToken(messaging, { vapidKey: 'YOUR_VAPID_KEY' }).then((token) => {
  fetch('/api/save-fcm-token/', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ token })
  });
});
