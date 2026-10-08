/* TarotAnuncia - Notificaciones para Android */

self.addEventListener('install', () => {
  self.skipWaiting();
});

self.addEventListener('activate', event => {
  event.waitUntil(self.clients.claim());
});

self.addEventListener('push', event => {
  let data = {};

  try {
    data = event.data ? event.data.json() : {};
  } catch (e) {
    data = {
      title: 'TarotAnuncia',
      body: event.data ? event.data.text() : 'Nueva notificación'
    };
  }

  const title = data.title || 'TarotAnuncia';

  const options = {
    body: data.body || 'Tienes una nueva notificación.',
    icon: '/ta-icon-192.png',
    badge: '/ta-icon-192.png',
    tag: data.tag || 'tarotanuncia-aviso',
    renotify: true,
    data: {
      url: data.url || '/admin.html'
    }
  };

  event.waitUntil(
    self.registration.showNotification(title, options)
  );
});

self.addEventListener('notificationclick', event => {
  event.notification.close();

  const url = new URL(
    event.notification.data?.url || '/admin.html',
    self.location.origin
  );

  if (url.origin !== self.location.origin) return;

  event.waitUntil(
    self.clients.matchAll({
      type: 'window',
      includeUncontrolled: true
    }).then(async clients => {
      for (const client of clients) {
        if (client.url.startsWith(url.origin)) {
          await client.focus();
          return client.navigate(url.href);
        }
      }

      return self.clients.openWindow(url.href);
    })
  );
});
