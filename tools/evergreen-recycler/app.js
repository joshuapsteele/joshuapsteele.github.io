'use strict';
let accessKey = ''; // Memory only; locking or refreshing discards the key.
let state;
let limit = 25;
const $ = (s) => document.querySelector(s);
function node(tag, text, className) {
  const el = document.createElement(tag);
  if (text !== undefined) el.textContent = text;
  if (className) el.className = className;
  return el;
}
function notice(text, error = false) {
  $('#notice').textContent = text;
  $('#notice').classList.toggle('error', error);
}
async function api(path, body) {
  const response = await fetch('/api/' + path, {
    method: body === undefined ? 'GET' : 'POST',
    headers: {Authorization: 'Bearer ' + accessKey, 'Content-Type': 'application/json'},
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'Request failed.');
  return result;
}
async function action(work) {
  try { await work(); } catch (error) { notice(error.message, true); }
}
async function refresh() {
  state = await api('state');
  $('#login').hidden = true;
  $('#workspace').hidden = false;
  const approved = state.articles.filter(a => a.enabled && a.present).length;
  $('#mode').textContent = state.settings.paused ? 'Queue paused' : state.live ? 'Live publishing' : 'Dry run';
  $('#counts').textContent = approved + ' approved / ' + state.articles.length + ' articles';
  $('#pause').textContent = state.settings.paused ? 'Resume queue' : 'Pause queue';
  $('#next-title').textContent = state.next.article?.title || 'No eligible article';
  $('#next-copy').textContent = state.next.content || 'Approve an article with a teaser to start the rotation. Age, expiry, and cooldown rules apply.';
  const names = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
  $('#schedule-summary').textContent = state.settings.weekdays.map(d => names[d]).join(', ') + ' at ' + state.settings.time + ' · ' + state.settings.timezone + ' · ' + state.settings.cooldown_days + '-day cooldown';
  const form = $('#settings-form');
  for (const [key, value] of Object.entries(state.settings)) {
    if (form.elements[key]) form.elements[key].value = value;
  }
  $('#days').replaceChildren();
  names.forEach((name, day) => {
    const label = node('label', name);
    const checkbox = node('input'); checkbox.type = 'checkbox'; checkbox.value = day;
    checkbox.checked = state.settings.weekdays.includes(day);
    label.prepend(checkbox); $('#days').append(label);
  });
  renderArticles(); renderHistory();
}
function renderArticles() {
  const query = $('#search').value.toLowerCase();
  const filter = $('#filter').value;
  const articles = state.articles.filter(a => (a.title + ' ' + a.url).toLowerCase().includes(query) &&
    (filter === 'all' || (filter === 'approved' ? a.enabled : !a.enabled)));
  $('#articles').replaceChildren();
  articles.slice(0, limit).forEach(a => {
    const article = node('article', undefined, 'article');
    const head = node('div', undefined, 'article-head');
    const text = node('div'); text.append(node('h3', a.title));
    const link = node('a', a.url); link.href = a.url; link.target = '_blank'; link.rel = 'noopener noreferrer';
    text.append(link, node('p', new Date(a.published).getFullYear() + ' · ' + a.shares + ' shares' + (a.last_shared ? ' · Last shared ' + a.last_shared.slice(0, 10) : ''), 'muted'));
    head.append(text, node('span', !a.present ? 'Removed from archive' : a.enabled ? 'Approved' : 'Needs review', 'badge'));
    article.append(head);
    const details = node('details'); details.append(node('summary', 'Edit teasers & approval'));
    const form = node('form');
    const label = node('label', 'Teaser variants · one per line');
    const variants = node('textarea'); variants.value = a.variants.join('\n'); label.append(variants);
    const count = node('p', '', 'muted');
    const updateCount = () => { count.textContent = 'Longest teaser + URL: ' + Math.max(0, ...variants.value.split('\n').filter(t => t.trim()).map(t => Array.from(t.trim() + '\n\n' + a.url).length)) + ' / 280 characters'; };
    variants.addEventListener('input', updateCount); updateCount();
    const approval = node('label', 'Approved for automatic recycling', 'approval');
    const checkbox = node('input'); checkbox.type = 'checkbox'; checkbox.checked = !!a.enabled; approval.prepend(checkbox);
    const expiresLabel = node('label', 'Stop after (optional)'); const expires = node('input'); expires.type = 'date'; expires.value = a.expires; expiresLabel.append(expires);
    form.append(label, count, approval, expiresLabel, node('button', 'Save article'));
    form.addEventListener('submit', e => { e.preventDefault(); action(async () => {
      await api('article', {id: a.id, enabled: checkbox.checked, variants: variants.value.split('\n').map(t => t.trim()).filter(Boolean), expires: expires.value});
      await refresh(); notice('Article saved.');
    }); });
    details.append(form); article.append(details); $('#articles').append(article);
  });
  if (!articles.length) $('#articles').append(node('p', 'No matching articles. Import your catalog to get started.'));
  $('#more').hidden = articles.length <= limit;
}
function renderHistory() {
  $('#attempts').replaceChildren();
  state.history.forEach(attempt => {
    const el = node('article', undefined, 'attempt');
    el.append(node('h3', attempt.status + ' · ' + attempt.created), node('pre', attempt.content), node('p', attempt.message, 'muted'));
    if (attempt.post_url && attempt.post_url.startsWith('https://')) {
      const link = node('a', 'Open published teaser'); link.href = attempt.post_url; link.target = '_blank'; link.rel = 'noopener noreferrer'; el.append(link);
    }
    if (['uncertain', 'sending'].includes(attempt.status)) {
      el.append(node('p', 'Queue blocked. Check Micro.blog’s Posts before recording the outcome.'));
      const linkLabel = node('label', 'Published teaser URL (optional)'); const postUrl = node('input'); postUrl.type = 'url'; linkLabel.append(postUrl); el.append(linkLabel);
      [['accepted', 'It was published'], ['not-delivered', 'It was not published']].forEach(([outcome, title]) => {
        const button = node('button', title, 'secondary');
        button.addEventListener('click', () => action(async () => {
          await api('resolve', {id: attempt.id, outcome, post_url: postUrl.value}); await refresh(); notice('Outcome recorded. The used slot will not be retried.');
        })); el.append(button);
      });
    }
    $('#attempts').append(el);
  });
  if (!state.history.length) $('#attempts').append(node('p', 'No publishing attempts yet. Dry runs do not change posting history.'));
}
$('#login-form').addEventListener('submit', e => { e.preventDefault(); accessKey = $('#access-key').value; action(async () => { await refresh(); $('#access-key').value = ''; notice('Queue loaded.'); }); });
$('#logout').addEventListener('click', () => { accessKey = ''; state = undefined; $('#workspace').hidden = true; $('#articles').replaceChildren(); $('#attempts').replaceChildren(); $('#login').hidden = false; notice('Dashboard locked.'); });
$('#pause').addEventListener('click', () => action(async () => { await api('settings', {...state.settings, paused: !state.settings.paused}); await refresh(); notice(state.settings.paused ? 'Queue paused. An in-flight request may still finish.' : 'Queue resumed.'); }));
$('#import').addEventListener('click', () => action(async () => { const result = await api('import', {}); await refresh(); notice('Imported ' + result.count + ' recent articles. Existing approvals and teasers were preserved.'); }));
$('#connection').addEventListener('click', () => action(async () => { const result = await api('connection', {}); $('#connection-result').textContent = result.destinations.map(d => (d.name || d.uid) + ': ' + d.uid).join('\n') || 'No hosted destinations returned. A Micro.blog-hosted blog is required for Micropub publishing.'; }));
$('#settings-form').addEventListener('submit', e => { e.preventDefault(); action(async () => {
  const form = e.currentTarget; const next = {...state.settings};
  ['timezone', 'time', 'destination'].forEach(k => { next[k] = form.elements[k].value.trim(); });
  ['cooldown_days', 'minimum_age_days', 'grace_minutes'].forEach(k => { next[k] = Number(form.elements[k].value); });
  next.weekdays = [...$('#days').querySelectorAll('input:checked')].map(el => Number(el.value));
  await api('settings', next); await refresh(); notice('Schedule saved.');
}); });
for (const id of ['search', 'filter']) $('#' + id).addEventListener('input', () => { limit = 25; renderArticles(); });
$('#more').addEventListener('click', () => { limit += 25; renderArticles(); });
for (const button of document.querySelectorAll('[data-tab]')) button.addEventListener('click', () => {
  document.querySelectorAll('.tab').forEach(el => { el.hidden = el.id !== button.dataset.tab; });
  document.querySelectorAll('[data-tab]').forEach(el => el.classList.toggle('active', el === button));
});
