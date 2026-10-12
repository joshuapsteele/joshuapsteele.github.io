const {test} = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');

function element() {
  return {style: {}, children: [], textContent: '', classList: {add() {}}, appendChild(child) {this.children.push(child);}, replaceChildren() {this.children = [];}};
}

test('one request per source, canonical URL without quotes, shared deduplicated counter', async () => {
  const elements = new Map();
  const urls = [];
  const canonical = 'https://joshuapsteele.com/example/';
  const document = {
    querySelector: () => ({href: canonical}),
    getElementById: id => {if (!elements.has(id)) elements.set(id, element()); return elements.get(id);},
    createElement: element,
  };
  vm.runInNewContext(fs.readFileSync('assets/js/webmentions.js', 'utf8'), {
    document, window: {location: {href: canonical}}, URL, console,
    fetch: async url => {urls.push(url); return {ok: true, status: 200, json: async () => ({children: [{url: 'https://example.org/like', 'wm-property': 'like-of'}]})};},
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.equal(urls.length, 2);
  for (const url of urls) assert.equal(new URL(url).searchParams.get('target'), canonical);
  assert.equal(elements.get('webmention-counter-text').textContent, '❤️ 1');
  assert.equal(elements.get('webmentions-heading').textContent, '💬 Conversations (1)');
});

test('reply context fetches the unquoted data attribute and gracefully falls back', async () => {
  const urls = [];
  const container = {...element(), dataset: {replyUrl: 'https://example.org/post?a=1&b=2'}};
  vm.runInNewContext(fs.readFileSync('assets/js/reply-context.js', 'utf8'), {
    document: {querySelector: () => container, createElement: element, createTextNode: text => ({textContent: text})},
    fetch: async url => {urls.push(url); throw new Error('CORS');},
  });
  await new Promise(resolve => setImmediate(resolve));
  assert.deepEqual(urls, [container.dataset.replyUrl]);
});
