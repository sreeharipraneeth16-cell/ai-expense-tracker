/* Expenses Tracker service worker
   - Caches the app shell so the page can open offline and be installed.
   - Network-first for pages, cache-first for icons/static assets.
   - Never touches API calls or other origins.
*/

const CACHE_NAME = "expenses-tracker-v1";

function baseUrl() {
  try {
    return new URL(self.registration.scope).pathname;
  } catch (err) {
    return "/";
  }
}

self.addEventListener("install", function (event) {
  event.waitUntil(
    caches.open(CACHE_NAME).then(function (cache) {
      const base = baseUrl();
      const assets = [base, base + "index.html", base + "manifest.webmanifest"];
      return cache.addAll(assets.map(function (path) { return new URL(path, self.location.href).href; })).catch(function () {});
    }).then(function () { return self.skipWaiting(); })
  );
});

self.addEventListener("activate", function (event) {
  event.waitUntil(
    caches.keys().then(function (keys) {
      return Promise.all(keys.filter(function (key) { return key !== CACHE_NAME; }).map(function (key) { return caches.delete(key); }));
    }).then(function () { return self.clients.claim(); })
  );
});

self.addEventListener("fetch", function (event) {
  const request = event.request;
  const url = new URL(request.url);

  // Only handle plain GETs from this origin, and never the AI API.
  if (request.method !== "GET") return;
  if (url.origin !== self.location.origin) return;
  if (url.pathname.indexOf("/api/") === 0) return;

  if (request.mode === "navigate") {
    event.respondWith(
      fetch(request)
        .then(function (response) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(request, copy);
          });
          return response;
        })
        .catch(function () {
          return caches.match(request);
        })
    );
    return;
  }

  event.respondWith(
    caches.match(request).then(function (cached) {
      const fetched = fetch(request).then(function (response) {
        if (response && response.ok) {
          const copy = response.clone();
          caches.open(CACHE_NAME).then(function (cache) {
            cache.put(request, copy);
          });
        }
        return response;
      });
      return cached || fetched;
    })
  );
});
