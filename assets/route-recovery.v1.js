/* Freedom Book GitHub Pages route recovery v1 — recover only known public aliases. */
(function (root, factory) {
  var api = factory();
  if (typeof module === 'object' && module.exports) module.exports = api;
  if (!root || !root.location) return;
  var target = api.resolve(root.location.pathname);
  if (target && target !== root.location.pathname) {
    root.location.replace(target + root.location.search + root.location.hash);
  }
})(typeof window !== 'undefined' ? window : null, function () {
  'use strict';

  var canonical = new Set([
    '/autor-arthur-magnus',
    '/a-vida-que-voce-adiou',
    '/codigo-da-vida-inabalavel',
    '/disciplina-e-liberdade',
    '/foco-que-gera-resultados',
    '/mente-forte-vida-leve',
    '/o-cansaco-invisivel',
    '/o-metodo-da-vida-mais-leve',
    '/o-peso-de-ser-forte-o-tempo-todo',
    '/privacidade',
    '/proposito-maior',
    '/quando-sua-vida-virou-sobrevivencia',
    '/recomecos-sao-escolhas',
    '/termos',
    '/kit-3-pares',
    '/kit-sandalias-infantil'
  ]);

  var aliases = Object.freeze({
    '/freedom-book': '/',
    '/freedom-book.html': '/',
    '/conteudo': '/',
    '/conteudo.html': '/',
    '/ebook-gratuito-o-cansaco-invisivel': '/o-cansaco-invisivel',
    '/ebook-gratuito-o-cansaco-invisivel.html': '/o-cansaco-invisivel',
    '/leitor': '/o-cansaco-invisivel',
    '/leitor.html': '/o-cansaco-invisivel',
    '/kit-tenis-sandalia': '/kit-3-pares',
    '/kit-tenis-sandalia.html': '/kit-3-pares',
    '/locked/the_select': '/',
    '/locked/the_select.html': '/'
  });

  function normalize(pathname) {
    if (typeof pathname !== 'string' || pathname.charAt(0) !== '/') return '';
    if (pathname.indexOf('\\') !== -1 || pathname.indexOf('//') === 0) return '';
    return pathname;
  }

  function resolve(pathname) {
    var path = normalize(pathname);
    if (!path) return null;
    if (Object.prototype.hasOwnProperty.call(aliases, path)) return aliases[path];
    if (path.length > 1 && path.charAt(path.length - 1) === '/') {
      var clean = path.replace(/\/+$/, '');
      if (canonical.has(clean)) return clean;
      if (Object.prototype.hasOwnProperty.call(aliases, clean)) return aliases[clean];
    }
    return null;
  }

  return { resolve: resolve };
});
