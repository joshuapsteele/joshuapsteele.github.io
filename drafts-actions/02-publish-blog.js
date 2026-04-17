// Publish: Blog — creates a Hugo post at content/blog/{slug}.md in
// joshuapsteele/joshuapsteele.github.io via the GitHub contents API.
//
// Draft format (simplest):
//   Post Title on Line 1
//
//   Body of the post. Markdown supported.
//
// Draft format with frontmatter overrides:
//   ---
//   title: Override Title
//   slug: custom-slug
//   tags: [theology, grief]
//   categories: [personal]
//   draft: true
//   description: A short summary
//   in_reply_to: https://example.com/original-post
//   ---
//   # Optional H1 ignored if title in frontmatter
//
//   Body.
//
// Any frontmatter field in the draft wins over prompt defaults.
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
    // Escape backslashes and double quotes for YAML double-quoted scalar.
    return '"' + String(s).replace(/\\/g, "\\\\").replace(/"/g, '\\"') + '"';
}
function yamlEscape(s) {
    if (s === null || s === undefined) return '""';
    const str = String(s);
    if (str.length === 0) return '""';
    // Block scalar if it has a double quote AND content is multi-line-ish; otherwise escape.
    if (str.indexOf("\n") !== -1) {
        return "|-\n  " + str.replace(/\n/g, "\n  ");
    }
    return yamlDoubleQuote(str);
}
function slugify(s, maxLen) {
    if (!maxLen) maxLen = 60;
    let slug = String(s).toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "");
    if (slug.length <= maxLen) return slug;
    const truncated = slug.substring(0, maxLen);
    const lastHyphen = truncated.lastIndexOf("-");
    if (lastHyphen > maxLen * 0.5) return truncated.substring(0, lastHyphen);
    return truncated.replace(/-+$/g, "");
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
// -----------------------------------------------------------------------------

const raw = draft.content.trim();
if (!raw) { app.displayErrorMessage("Draft is empty."); context.cancel(); }
else {
    const parsed = parseFrontmatter(raw);
    const fm = parsed.frontmatter;
    const afterFM = parsed.body;
    const lines = afterFM.split("\n");

    // Title: fm.title > first line (stripped of H1 #)
    let title = fm.title;
    let bodyLines;
    if (title) {
        bodyLines = lines;
    } else {
        title = (lines[0] || "").replace(/^#+\s*/, "").trim();
        bodyLines = lines.slice(1);
    }
    if (!title) { app.displayErrorMessage("Title required (first line or frontmatter)."); context.cancel(); }
    else {
        const body = bodyLines.join("\n").trim();

        // Prompt for anything fm didn't provide.
        const needsPrompt = !fm.tags || !fm.categories || !fm.description || (fm.draft === undefined);
        let tags = fm.tags, categories = fm.categories, description = fm.description, isDraft = fm.draft;

        if (needsPrompt) {
            const p = Prompt.create();
            p.title = "Publish: Blog";
            p.message = "Metadata for “" + title + "”";
            if (!fm.description) p.addTextField("description", "Description", "", { placeholder: "Short summary (optional)" });
            if (!fm.tags)        p.addTextField("tags", "Tags", "", { placeholder: "theology, grief, anglican" });
            if (!fm.categories)  p.addTextField("categories", "Categories", "", { placeholder: "personal, theology" });
            if (fm.draft === undefined) p.addSwitch("isDraft", "Save as draft?", false);
            p.addButton("Publish");
            p.addButton("Cancel", "cancel", true);
            if (!p.show() || p.buttonPressed === "cancel") {
                context.cancel();
            } else {
                if (!fm.description)       description = (p.fieldValues.description || "").trim();
                if (!fm.tags)              tags        = p.fieldValues.tags || "";
                if (!fm.categories)        categories  = p.fieldValues.categories || "";
                if (fm.draft === undefined) isDraft    = !!p.fieldValues.isDraft;
            }
        }

        // If prompt was cancelled, variables stay undefined/null — skip build.
        if (title && (description !== undefined || !needsPrompt)) {
            const tagsArr       = normalizeTags(tags);
            const categoriesArr = normalizeTags(categories);
            const slug          = fm.slug ? slugify(fm.slug) : slugify(title);
            const inReplyTo     = fm.in_reply_to || fm.reply_to || "";
            if (!slug) { app.displayErrorMessage("Could not derive a slug."); context.cancel(); }
            else {
                const filename = slug + ".md";
                const path     = "content/blog/" + filename;
                const dateISO  = (new Date()).toISOString().replace(/\.\d{3}Z$/, "Z");

                // Assemble frontmatter in the shape of recent posts:
                // title, date, draft, tags, categories, url  (description only if present)
                let fmOut = "---\n";
                fmOut += "title: "      + yamlEscape(title) + "\n";
                fmOut += "date: "       + dateISO + "\n";
                fmOut += "draft: "      + (isDraft ? "true" : "false") + "\n";
                if (description)        fmOut += "description: " + yamlEscape(description) + "\n";
                if (inReplyTo)          fmOut += "in_reply_to: " + yamlEscape(inReplyTo) + "\n";
                fmOut += "tags: ["       + tagsArr.map(yamlDoubleQuote).join(", ") + "]\n";
                fmOut += "categories: [" + categoriesArr.map(yamlDoubleQuote).join(", ") + "]\n";
                fmOut += "url: /"        + slug + "/\n";
                fmOut += "---\n\n";
                const postContent = fmOut + body + "\n";

                const token  = getCred("GitHub Blog Token", "token", "GitHub Personal Access Token", true);
                if (token) {
                    const repo       = "joshuapsteele/joshuapsteele.github.io";
                    const apiBase    = "https://api.github.com/repos/" + repo + "/contents/" + path;
                    const b64        = Base64.encode(postContent);

                    // Check for existing file to get sha.
                    const headResp = httpWithRetry({
                        url: apiBase, method: "GET",
                        headers: { "Authorization": "Bearer " + token, "Accept": "application/vnd.github.v3+json" }
                    });
                    let sha = null;
                    if (headResp.statusCode === 200) {
                        try { sha = JSON.parse(headResp.responseText).sha; } catch (_) {}
                    }

                    const putReq = {
                        url: apiBase, method: "PUT",
                        headers: {
                            "Authorization": "Bearer " + token,
                            "Accept":        "application/vnd.github.v3+json",
                            "Content-Type":  "application/json"
                        },
                        data: {
                            message: (sha ? "Update: " : "Add: ") + title,
                            content: b64,
                            branch:  "main"
                        }
                    };
                    if (sha) putReq.data.sha = sha;

                    const resp = httpWithRetry(putReq);
                    if (resp.statusCode === 200 || resp.statusCode === 201) {
                        const postURL = "https://joshuapsteele.com/" + slug + "/";
                        app.setClipboard(postURL);
                        app.displaySuccessMessage(
                            (sha ? "Updated" : "Published") + ": " + title + "\n\n" +
                            postURL + "\n(copied to clipboard)\n\n" +
                            "Build: https://github.com/" + repo + "/actions"
                        );
                        if (!draft.hasTag("published")) draft.addTag("published");
                        draft.isArchived = true;
                        draft.update();
                    } else {
                        app.displayErrorMessage("GitHub " + resp.statusCode + ":\n" + (resp.responseText || "").substring(0, 500));
                        context.fail();
                    }
                }
            }
        }
    }
}
