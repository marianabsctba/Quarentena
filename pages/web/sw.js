// O v86 baixa o arquivo de novo a cada abertura. Os nomes em fs/flat sao o hash do
// conteudo e o do estado leva a versao do build, entao nunca ficam velhos no cache.
var CACHE = "quarentena-v__VERSAO__";

self.addEventListener("install", function () { self.skipWaiting(); });
self.addEventListener("activate", function (e) {
  e.waitUntil(caches.keys().then(function (nomes) {
    return Promise.all(nomes.filter(function (n) { return n !== CACHE; }).map(function (n) { return caches.delete(n); }));
  }).then(function () { return self.clients.claim(); }));
});
self.addEventListener("fetch", function (e) {
  if (!/\/fs\/flat\/|\/estado-[^\/]+\.bin\.zst$/.test(new URL(e.request.url).pathname)) return;
  e.respondWith(caches.open(CACHE).then(function (c) {
    return c.match(e.request).then(function (r) {
      return r || fetch(e.request).then(function (resp) {
        if (resp.ok) c.put(e.request, resp.clone());
        return resp;
      });
    });
  }));
});
