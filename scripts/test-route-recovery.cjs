#!/usr/bin/env node
'use strict';

const assert = require('assert');
const fs = require('fs');
const { resolve } = require('../assets/route-recovery.v1.js');

const redirects = fs.readFileSync('_redirects', 'utf8')
  .split(/\r?\n/)
  .map(line => line.trim())
  .filter(line => line && !line.startsWith('#'));

for (const line of redirects) {
  const parts = line.split(/\s+/);
  assert(parts.length >= 3, `invalid _redirects line: ${line}`);
  const [source, target, status] = parts;
  assert.strictEqual(status, '301', `unexpected redirect status: ${line}`);
  assert.strictEqual(resolve(source), target, `route recovery drift: ${source} -> ${target}`);
}

const canonicalTrailingSlashCases = [
  ['/autor-arthur-magnus/', '/autor-arthur-magnus'],
  ['/proposito-maior/', '/proposito-maior'],
  ['/o-metodo-da-vida-mais-leve/', '/o-metodo-da-vida-mais-leve'],
  ['/kit-3-pares/', '/kit-3-pares'],
  ['/kit-sandalias-infantil/', '/kit-sandalias-infantil']
];
for (const [source, target] of canonicalTrailingSlashCases) {
  assert.strictEqual(resolve(source), target, `trailing-slash recovery drift: ${source}`);
}

for (const safePath of [
  '/',
  '/proposito-maior',
  '/autor-arthur-magnus',
  '/definitely-not-a-route/',
  '//evil.example/path',
  '/https://evil.example'
]) {
  assert.strictEqual(resolve(safePath), null, `unexpected recovery for ${safePath}`);
}

const notFound = fs.readFileSync('404.html', 'utf8');
assert(notFound.includes('name="robots"') && notFound.includes('noindex,follow'), '404 must remain noindex');
assert(notFound.includes('/assets/route-recovery.v1.js'), '404 must load route recovery before rendering fallback');

console.log(`PASS: ${redirects.length} declared aliases + trailing-slash recovery are safe and deterministic`);
