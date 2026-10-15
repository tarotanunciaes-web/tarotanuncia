// Solo navegación del panel. No almacenar datos privados ni respuestas de Supabase.
self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', event => event.waitUntil(self.clients.claim()));
self.addEventListener('fetch', event => {
  const req = event.request;
  const url = new URL(req.url);
  if (req.mode !== 'navigate' || url.origin !== self.location.origin || !url.pathname.endsWith('/profesionales.html')) return;
  event.respondWith(fetch(req));
});
