// Publish: Link — creates a link post at links.joshuapsteele.com.
//
// Accepted draft formats:
//
//   Simple:
//     https://example.com/article
//
//     This is a sharp take on #webdev and #indieweb principles.
//
//   With explicit frontmatter:
//     ---
//     url: https://example.com/article
//     tags: [webdev, indieweb]
//     pinned: true
//     ---
//     My commentary.
//
//   Legacy (still works for continuity with the current action):
//     https://example.com/article
//     tag1, tag2
//     Commentary on line 3+
//
// Tags are collected from three sources and merged (deduped, normalized):
//   1. Frontmatter `tags:`
//   2. Legacy line 2 (only if it contains commas and no spaces-except-between-tags)
//   3. Inline #hashtags in the commentary
//
// On success: permalink is copied to clipboard; draft is tagged `published` and archived.
// On duplicate: offers to open the admin URL to edit.

// ---------- Inline helpers ----------
function getCred(name, fieldKey, fieldLabel, isPassword) {
    const c = Credential.create(name, "Enter your " + fieldLabel);
    if (isPassword) c.addPasswordField(fieldKey, fieldLabel);
    else c.addTextField(fieldKey, fieldLabel);
    c.authorize();
    const v = c.getValue(fieldKey);
    if (!v) { app.displayErrorMessage("Credential '" + name + "' missing."); context.fail(); return null; }
    return v;
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
function extractHashtags(text) {
    const tags = [];
    const re = /(?:^|\s)#([a-z0-9][a-z0-9-]*)/gi;
    let m;
    while ((m = re.exec(text)) !== null) tags.push(m[1]);
    return normalizeTags(tags);
}
// -------------------------------------

const raw = draft.content.trim();
if (!raw) { app.displayErrorMessage("Draft is empty."); context.cancel(); }
else {
    const parsed = parseFrontmatter(raw);
    const fm     = parsed.frontmatter;
    const afterFM = parsed.body;

    // Determine URL and commentary.
    let url = fm.url || "";
    let commentary = "";
    let fmTags = fm.tags ? normalizeTags(fm.tags) : [];
    let pinned = !!fm.pinned;

    if (!url) {
        // First non-blank line is URL.
        const lines = afterFM.split("\n");
        url = (lines[0] || "").trim();

        // Detect legacy format: line 2 is a bare comma-list that isn't a sentence.
        // Heuristic: contains a comma AND no period AND is short (< 120 chars) AND doesn't contain a space in any "tag" segment.
        let rest;
        if (lines.length >= 2) {
            const l2 = lines[1].trim();
            const looksLikeTagLine =
                l2.length > 0 &&
                l2.length < 120 &&
                l2.indexOf(",") !== -1 &&
                !/[.!?]/.test(l2) &&
                l2.split(",").every(function (t) { return t.trim().split(/\s+/).length <= 2; });
            if (looksLikeTagLine) {
                fmTags = normalizeTags(fmTags.concat(l2.split(",")));
                rest = lines.slice(2).join("\n").trim();
            } else {
                // Blank line separator expected between URL and commentary.
                rest = lines.slice(1).join("\n").replace(/^\n+/, "");
            }
        } else {
            rest = "";
        }
        commentary = rest.trim();
    } else {
        commentary = afterFM.trim();
    }

    if (!url || !(url.indexOf("http://") === 0 || url.indexOf("https://") === 0)) {
        app.displayErrorMessage("First line must be a URL starting with http(s)://");
        context.fail();
    } else {
        // Merge inline #hashtags from commentary.
        const inlineTags = extractHashtags(commentary);
        const allTags = normalizeTags(fmTags.concat(inlineTags));

        const token = getCred("LinkLog", "token", "LinkLog API Token", true);
        if (token) {
            const resp = httpWithRetry({
                url: "https://links.joshuapsteele.com/api/links",
                method: "POST",
                headers: {
                    "Content-Type":  "application/json",
                    "Authorization": "Bearer " + token
                },
                data: {
                    url:        url,
                    commentary: commentary,
                    tags:       allTags.join(","),
                    pinned:     pinned
                }
            });

            let payload = {};
            try { payload = JSON.parse(resp.responseText || "{}"); } catch (_) {}

            if (resp.success) {
                const isDup = (resp.headers && resp.headers["X-LinkLog-Duplicate"]) === "true" || payload.duplicate;
                const permalink = payload.permalink || "";
                const adminURL  = payload.admin_url || "";

                if (isDup) {
                    const p = Prompt.create();
                    p.title   = "Already saved";
                    p.message = payload.message || "This URL is already in LinkLog.";
                    if (adminURL) p.addButton("Open admin to edit", "admin");
                    if (permalink) p.addButton("Copy permalink", "copy");
                    p.addButton("Dismiss", "dismiss", true);
                    if (p.show()) {
                        if (p.buttonPressed === "admin" && adminURL) app.openURL(adminURL);
                        else if (p.buttonPressed === "copy" && permalink) app.setClipboard(permalink);
                    }
                    // Don't archive — user may want to rewrite commentary.
                } else {
                    if (permalink) app.setClipboard(permalink);
                    app.displaySuccessMessage(
                        (payload.message || "Saved") +
                        (permalink ? "\n\n" + permalink + "\n(copied to clipboard)" : "")
                    );
                    if (!draft.hasTag("published")) draft.addTag("published");
                    draft.isArchived = true;
                    draft.update();
                }
            } else {
                app.displayErrorMessage("LinkLog " + resp.statusCode + ": " + (payload.error || (resp.responseText || "").substring(0, 300)));
                context.fail();
            }
        }
    }
}
