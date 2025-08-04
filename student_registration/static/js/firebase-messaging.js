import { initializeApp } from "https://www.gstatic.com/firebasejs/12.0.0/firebase-app.js";
import { getMessaging, getToken, onMessage } from "https://www.gstatic.com/firebasejs/12.0.0/firebase-messaging.js";

const firebaseConfig = {
  apiKey: "AIzaSyAL2iS7YCesCURrxFViKUzH8LOrDzDIPHg",
  authDomain: "leb-bma.firebaseapp.com",
  projectId: "leb-bma",
  storageBucket: "leb-bma.firebasestorage.app",
  messagingSenderId: "455115377412",
  appId: "1:455115377412:web:1e39a332cd97f98e009e51",
  measurementId: "G-1QPVEZK990",
};

const app = initializeApp(firebaseConfig);
const messaging = getMessaging(app);
window.firebaseMessaging = messaging;

navigator.serviceWorker
  .register("/static/firebase-messaging-sw.js")
  .then((registration) => {
    Notification.requestPermission().then((permission) => {
      if (permission === "granted") {
        getToken(messaging, {
          vapidKey: "BAwRHhzYusFpd-Z_CTfU3AE1w_LuOgCJ2LpTQMPbIUNZQv343yQwd2fF49XxGj09AwArLcZ7icVMTlgxcaX53nE",
          serviceWorkerRegistration: registration,
        }).then((token) => {
          fetch("/api/save-fcm-token/", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ token }),
          });
        });
      }
    });
  });

onMessage(messaging, (payload) => {
  if (payload.data && payload.data.type === "mscc_export_ready") {
    $('#downloadReadyModal .download-link').attr('href', payload.data.url);
    $('#downloadReadyModal').modal('show');
    const list = $('#mscc-notification-list');
    if (list.length) {
      list.find('span:contains("No notifications")').closest('li').remove();
      const timestamp = new Date().toISOString().slice(0, 16).replace('T', ' ');
      const li = $('<li/>', { class: 'nav-item' });
      $('<a/>', {
        class: 'nav-link',
        href: payload.data.url,
        target: '_blank',
        text: 'MSCC export ' + timestamp,
      }).appendTo(li);
      list.prepend(li);
      if (list.children('li').length > 5) {
        list.children('li:last-child').remove();
      }
    }
  }
});
