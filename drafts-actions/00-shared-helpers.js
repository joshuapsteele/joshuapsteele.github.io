// Shared helpers for the Publish action group.
//
// Drafts actions do not support real module imports, so these helpers are
// duplicated inline at the top of each destination-specific action script.
// This file is the canonical source — if you change something here, update
// the copies at the top of 02–05.
//
// No side effects; no `return` at top level (Drafts runs scripts in a function
// context, but these helpers do not call anything on load).

// ---------------------------------------------------------------
// Credential: fetch a named credential + field, prompt on first use.
// Throws via context.fail if missing.
// ---------------------------------------------------------------
function getCred(name, fieldKey, fieldLabel, isPassword) {
    const c = Credential.create(name, "Enter your " + fieldLabel);
    if (isPassword) c.addPasswordField(fieldKey, fieldLabel);
    else c.addTextField(fieldKey, fieldLabel);
    c.authorize();
    const v = c.getValue(fieldKey);
    if (!v) {
        app.displayErrorMessage("Credential '" + name + "' field '" + fieldKey + "' is empty.");
        context.fail();
        return null;
    }
    return v;
}

// ---------------------------------------------------------------
// YAML-safe string quoting. Picks the safest scalar form based on content.
// ---------------------------------------------------------------
function yamlEscape(s) {
    if (s === null || s === undefined) return '""';
    const str = String(s);
    // Empty
    if (str.length === 0) return '""';
    // If it contains a double quote, use block scalar |- so nothing needs escaping.
    if (str.indexOf('"') !== -1) {
        // Escape ends-with-newline edge case is fine; block keeps it.
        return "|-\n  " + str.replace(/\n/g, "\n  ");
    }
    // If it contains a colon+space, apostrophe, or starts with special char: use double quotes.
    if (/[:]\s|['`&*!|>%@]/.test(str) || /^[-?:,\[\]{}#&*!|>'"%@`]/.test(str.trim())) {
        return '"' + str + '"';
    }
    // Otherwise plain scalar (no quotes).
    return '"' + str + '"'; // always double-quote for safety
}

// ---------------------------------------------------------------
// Slugify: kebab-case, truncate at last hyphen before maxLen, strip leading/trailing hyphens.
// ---------------------------------------------------------------
function slugify(s, maxLen) {
    if (!maxLen) maxLen = 60;
    let slug = String(s).toLowerCase()
        .replace(/[^a-z0-9]+/g, "-")
        .replace(/^-+|-+$/g, "");
    if (slug.length <= maxLen) return slug;
    const truncated = slug.substring(0, maxLen);
    const lastHyphen = truncated.lastIndexOf("-");
    if (lastHyphen > maxLen * 0.5) return truncated.substring(0, lastHyphen);
    return truncated.replace(/-+$/g, "");
}

// ---------------------------------------------------------------
// Tag normalization: lowercase, hyphenate whitespace, dedupe. Accepts array or CSV string.
// ---------------------------------------------------------------
function normalizeTags(input) {
    let arr;
    if (Array.isArray(input)) arr = input;
    else if (typeof input === "string") arr = input.split(",");
    else return [];
    const seen = {};
    const out = [];
    arr.forEach(function (t) {
        if (!t) return;
        const norm = String(t).trim().toLowerCase().replace(/^#/, "").replace(/\s+/g, "-");
        if (norm && !seen[norm]) { seen[norm] = true; out.push(norm); }
    });
    return out;
}

// ---------------------------------------------------------------
// Extract inline #hashtags from body text. Returns {tags: [...], stripped: text}.
// Leaves inline #hashtag mentions in place but collects them for routing.
// Pass stripTrailing=true to remove a trailing "Tags: #a #b" line if present.
// ---------------------------------------------------------------
function extractHashtags(text) {
    const tags = [];
    const re = /(?:^|\s)#([a-z0-9][a-z0-9-]*)/gi;
    let m;
    while ((m = re.exec(text)) !== null) tags.push(m[1]);
    return { tags: normalizeTags(tags), stripped: text };
}

// ---------------------------------------------------------------
// Parse optional YAML frontmatter block from top of content.
// Returns {frontmatter: {...}, body: string}. Fields are parsed as strings;
// values in [a, b, c] form are split into arrays.
// ---------------------------------------------------------------
function parseFrontmatter(content) {
    const lines = content.split("\n");
    if (lines[0].trim() !== "---") return { frontmatter: {}, body: content };
    let closingIdx = -1;
    for (let i = 1; i < lines.length; i++) {
        if (lines[i].trim() === "---") { closingIdx = i; break; }
    }
    if (closingIdx === -1) return { frontmatter: {}, body: content };
    const fm = {};
    for (let i = 1; i < closingIdx; i++) {
        const m = lines[i].match(/^(\w+)\s*:\s*(.*)$/);
        if (!m) continue;
        let val = m[2].trim();
        // Array form: [a, b, c]
        if (val.startsWith("[") && val.endsWith("]")) {
            val = val.slice(1, -1).split(",").map(function (x) {
                return x.trim().replace(/^["']|["']$/g, "");
            }).filter(Boolean);
        } else {
            val = val.replace(/^["']|["']$/g, "");
        }
        fm[m[1]] = val;
    }
    const body = lines.slice(closingIdx + 1).join("\n").replace(/^\n+/, "");
    return { frontmatter: fm, body: body };
}

// ---------------------------------------------------------------
// HTTP with retry on 5xx / network failures. Returns {success, statusCode, responseText, headers}.
// ---------------------------------------------------------------
function httpWithRetry(req, maxAttempts) {
    maxAttempts = maxAttempts || 3;
    let last = null;
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        const http = HTTP.create();
        http.timeout = 30;
        const resp = http.request(req);
        last = resp;
        if (resp.success) return resp;
        // Retry only on 5xx or network error (statusCode 0)
        if (resp.statusCode >= 500 || resp.statusCode === 0) {
            if (attempt < maxAttempts) continue;
        }
        return resp; // 4xx or final failure
    }
    return last;
}

// ---------------------------------------------------------------
// Success display with copy-to-clipboard.
// ---------------------------------------------------------------
function displayResultAndCopy(title, url, extra) {
    if (url) app.setClipboard(url);
    const msg = (title || "Published") +
        (url ? "\n\n" + url + "\n(copied to clipboard)" : "") +
        (extra ? "\n\n" + extra : "");
    app.displaySuccessMessage(msg);
}

// ---------------------------------------------------------------
// Mark draft as published: add tag, archive, update.
// ---------------------------------------------------------------
function markPublished(d) {
    if (!d.hasTag("published")) d.addTag("published");
    d.isArchived = true;
    d.update();
}
