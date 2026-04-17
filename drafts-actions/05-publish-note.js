// Publish: Note — creates a Hugo shortform note at
// content/notes/{YYYY-MM-DD-HHMM}.md in joshuapsteele/joshuapsteele.github.io
// via the GitHub contents API.
//
// This is the CANONICAL home for shortform content. Micro.Blog subscribes
// to https://joshuapsteele.com/notes/feed.json and fans out to
// Mastodon and Threads. Crossposting is downstream of this action.
//
// Draft format (simplest — no title required):
//   Just write. #hashtags anywhere in the body become tags.
//
// Draft format with title:
//   # Optional Heading
//
//   Body.
//
// Draft format with frontmatter overrides:
//   ---
//   title: Optional title
//   slug: custom-slug
//   tags: [quotes, watching]
//   date: 2026-04-17T18:30:00-04:00
//   in_reply_to: https://example.com/original-post
//   ---
//
//   Body.
//
// Filename is ALWAYS timestamp-based: 2026-04-17-1830.md. That keeps
// untitled notes collision-free and sorts chronologically.
//
// Tags: frontmatter tags[] AND inline #hashtags are merged.
// On success: draft is tagged `published` and archived.

// ---------- Inline helpers (kept in sync with 00-shared-helpers.js) ----------
function getCred(name, fieldKey, fieldLabel, isPassword) {
    const c = Credential.create(name, "Enter your " + fieldLabel);
    if (isPassword) c.addPasswordField(fieldKey, fieldLabel);
    else c.addTextField(fieldKey, fieldLabel);
    c.authorize();
    const v = c.getValue(fieldKey);
    if (!v) { app.displayErrorMessage("Credential '" + name + "' missing."); context.fail(); return null; }
    return v;
}
function yamlDoubleQuote(s) {
    return '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
}
function yamlEscape(s) {
    if (s === null || s === undefined) return '""';
    const str = String(s);
    if (str.length === 0) return '""';
    if (str.indexOf("\n") !== -1) return "|-\n  " + str.replace(/\n/g, "\n  ");
    return yamlDoubleQuote(str);
}
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
function extractHashtags(text) {
    const out = [];
    const seen = {};
    const re = /(?:^|\s)#([A-Za-z][A-Za-z0-9_-]{1,40})/g;
    let m;
    while ((m = re.exec(text)) !== null) {
        const tag = m[1].toLowerCase();
        if (!seen[tag]) { seen[tag] = true; out.push(tag); }
    }
    return out;
}
function parseFrontmatter(content) {
    const lines = content.split("\n");
    if (lines[0].trim() !== "---") return { frontmatter: {}, body: content };
    let closingIdx = -1;
    for (let i = 1; i < lines.length; i++) if (lines[i].trim() === "---") { closingIdx = i; break; }
    if (closingIdx === -1) return { frontmatter: {}, body: content };
    const fm = {};
    for (let i = 1; i < closingIdx; i++) {
        const m = lines[i].match(/^(\w+)\s*:\s*(.*)$/);
        if (!m) continue;
        let val = m[2].trim();
        if (val.startsWith("[") && val.endsWith("]")) {
            val = val.slice(1, -1).split(",").map(function (x) { return x.trim().replace(/^["']|["']$/g, ""); }).filter(Boolean);
        } else if (val === "true" || val === "false") {
            val = (val === "true");
        } else {
            val = val.replace(/^["']|["']$/g, "");
        }
        fm[m[1]] = val;
    }
    const body = lines.slice(closingIdx + 1).join("\n").replace(/^\n+/, "");
    return { frontmatter: fm, body: body };
}
function httpWithRetry(req, maxAttempts) {
    maxAttempts = maxAttempts || 3;
    let last = null;
    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
        const http = HTTP.create();
        http.timeout = 30;
        const resp = http.request(req);
        last = resp;
        if (resp.success) return resp;
        if (resp.statusCode >= 500 || resp.statusCode === 0) {
            if (attempt < maxAttempts) continue;
        }
        return resp;
    }
    return last;
}
function pad2(n) { return (n < 10 ? "0" : "") + n; }
// -----------------------------------------------------------------------------

const raw = draft.content.trim();
if (!raw) {
    app.displayErrorMessage("Draft is empty.");
    context.cancel();
} else {
    const parsed = parseFrontmatter(raw);
    const fm = parsed.frontmatter;
    let body = parsed.body;

    // Title handling:
    // - fm.title wins if present (even empty string means "no title")
    // - Otherwise, if body starts with "# Heading", promote that to title
    // - Otherwise: no title (true shortform)
    let title = "";
    if (Object.prototype.hasOwnProperty.call(fm, "title")) {
        title = String(fm.title || "").trim();
    } else {
        const firstLineMatch = body.match(/^(#{1,3})\s+(.+?)\s*\n/);
        if (firstLineMatch) {
            title = firstLineMatch[2].trim();
            body = body.substring(firstLineMatch[0].length);
        }
    }

    // Date: fm.date if present, otherwise now
    let dateObj;
    if (fm.date) {
        const parsedDate = new Date(fm.date);
        dateObj = isNaN(parsedDate.getTime()) ? new Date() : parsedDate;
    } else {
        dateObj = new Date();
    }
    const dateISO = dateObj.toISOString().replace(/\.\d{3}Z$/, "Z");

    // Filename: YYYY-MM-DD-HHMM.md (local time so it reads naturally,
    // but the content date is still UTC ISO so Hugo sort order matches).
    const y = dateObj.getFullYear();
    const mo = pad2(dateObj.getMonth() + 1);
    const d = pad2(dateObj.getDate());
    const h = pad2(dateObj.getHours());
    const mi = pad2(dateObj.getMinutes());
    const filename = (fm.slug ? String(fm.slug).toLowerCase().replace(/[^a-z0-9-]+/g, "-").replace(/^-+|-+$/g, "") : (y + "-" + mo + "-" + d + "-" + h + mi)) + ".md";
    const path = "content/notes/" + filename;

    // Tags: merge fm.tags[] with inline #hashtags from the body.
    const fmTags = normalizeTags(fm.tags);
    const inlineTags = extractHashtags(body);
    const allTags = normalizeTags(fmTags.concat(inlineTags));
    const inReplyTo = fm.in_reply_to || fm.reply_to || "";

    body = body.trim();
    if (!body && !title) {
        app.displayErrorMessage("Note is empty.");
        context.cancel();
    } else {
        // Assemble frontmatter.
        let fmOut = "---\n";
        if (title) fmOut += "title: " + yamlEscape(title) + "\n";
        fmOut += "date: " + dateISO + "\n";
        fmOut += "draft: false\n";
        if (inReplyTo) fmOut += "in_reply_to: " + yamlEscape(inReplyTo) + "\n";
        if (fm.syndicate === false) fmOut += "syndicate: false\n";
        fmOut += "tags: [" + allTags.map(yamlDoubleQuote).join(", ") + "]\n";
        fmOut += "---\n\n";
        const noteContent = fmOut + body + "\n";

        const token = getCred("GitHub Blog Token", "token", "GitHub Personal Access Token", true);
        if (token) {
            const repo = "joshuapsteele/joshuapsteele.github.io";
            const apiBase = "https://api.github.com/repos/" + repo + "/contents/" + path;
            const b64 = Base64.encode(noteContent);

            // Notes use timestamp filenames, so collisions are rare, but handle gracefully.
            const headResp = httpWithRetry({
                url: apiBase, method: "GET",
                headers: { "Authorization": "Bearer " + token, "Accept": "application/vnd.github.v3+json" }
            });
            let sha = null;
            if (headResp.statusCode === 200) {
                try { sha = JSON.parse(headResp.responseText).sha; } catch (_) {}
            }

            const commitMsg = sha
                ? ("Update note: " + (title || filename))
                : ("Add note: " + (title || "shortform " + y + "-" + mo + "-" + d + " " + h + ":" + mi));

            const putReq = {
                url: apiBase, method: "PUT",
                headers: {
                    "Authorization": "Bearer " + token,
                    "Accept": "application/vnd.github.v3+json",
                    "Content-Type": "application/json"
                },
                data: {
                    message: commitMsg,
                    content: b64,
                    branch: "main"
                }
            };
            if (sha) putReq.data.sha = sha;

            const resp = httpWithRetry(putReq);
            if (resp.statusCode === 200 || resp.statusCode === 201) {
                // Permalink: Hugo default is /notes/{slug}/, slug = filename without .md.
                // We do NOT set `url:` in frontmatter, so Hugo generates it from the file.
                const slug = filename.replace(/\.md$/, "");
                const noteURL = "https://joshuapsteele.com/notes/" + slug + "/";
                app.setClipboard(noteURL);
                app.displaySuccessMessage(
                    (sha ? "Updated" : "Published") + " note" +
                    (title ? (": " + title) : "") + "\n\n" +
                    noteURL + "\n(copied to clipboard)\n\n" +
                    "Micro.Blog will pick it up within ~20 min and crosspost to Mastodon + Threads.\n" +
                    "Build: https://github.com/" + repo + "/actions"
                );
                if (!draft.hasTag("published")) draft.addTag("published");
                if (!draft.hasTag("note")) draft.addTag("note");
                draft.isArchived = true;
                draft.update();
            } else {
                app.displayErrorMessage("GitHub " + resp.statusCode + ":\n" + (resp.responseText || "").substring(0, 500));
                context.fail();
            }
        }
    }
}
