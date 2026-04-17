// Publish: Newsletter — creates a DRAFT issue in Buttondown.
//
// Safe by design: always posts with status="draft". Never queues a send from
// Drafts. You review and schedule/send from the Buttondown dashboard.
//
// Draft format (simple):
//   Subject Line on Line 1
//
//   Body of the newsletter. Markdown supported.
//
// With frontmatter overrides:
//   ---
//   subject: Override Subject
//   ---
//   First line of the body…
//
// On success: draft is tagged `published` and archived; Buttondown edit URL
// is copied to clipboard.

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
// -------------------------------------

const raw = draft.content.trim();
if (!raw) { app.displayErrorMessage("Draft is empty."); context.cancel(); }
else {
    const parsed  = parseFrontmatter(raw);
    const fm      = parsed.frontmatter;
    const afterFM = parsed.body;

    // Derive subject from frontmatter > first non-blank line.
    let subject = fm.subject || "";
    let body    = afterFM;
    if (!subject) {
        const lines = afterFM.split("\n");
        let idx = 0;
        while (idx < lines.length && !lines[idx].trim()) idx++;
        subject = (lines[idx] || "").replace(/^#+\s*/, "").trim();
        body = lines.slice(idx + 1).join("\n").trim();
    }

    // Confirm subject with the user.
    const p = Prompt.create();
    p.title   = "Publish: Newsletter (Buttondown draft)";
    p.message = "This will create a DRAFT in Buttondown — nothing is sent.";
    p.addTextField("subject", "Subject", subject);
    p.addButton("Create draft");
    p.addButton("Cancel", "cancel", true);
    if (!p.show() || p.buttonPressed === "cancel") {
        context.cancel();
    } else {
        subject = (p.fieldValues.subject || subject).trim();
        if (!subject) {
            app.displayErrorMessage("Subject is required.");
            context.fail();
        } else {
            const token = getCred("Buttondown", "token", "Buttondown API Token", true);
            if (token) {
                const resp = httpWithRetry({
                    url:     "https://api.buttondown.com/v1/emails",
                    method:  "POST",
                    headers: {
                        "Authorization": "Token " + token,
                        "Content-Type":  "application/json",
                        "Accept":        "application/json"
                    },
                    data: {
                        subject: subject,
                        body:    body,
                        status:  "draft"
                    }
                });

                let payload = {};
                try { payload = JSON.parse(resp.responseText || "{}"); } catch (_) {}

                if (resp.statusCode === 200 || resp.statusCode === 201) {
                    // Buttondown returns an `id` and `absolute_url` (or slug).
                    const editURL =
                        payload.absolute_url
                        || (payload.id ? "https://buttondown.com/emails/" + payload.id : "https://buttondown.com/emails");
                    app.setClipboard(editURL);
                    app.displaySuccessMessage(
                        "Buttondown draft created.\n\n" +
                        editURL + "\n(copied to clipboard)\n\n" +
                        "Review and schedule from the Buttondown dashboard."
                    );
                    if (!draft.hasTag("published")) draft.addTag("published");
                    draft.isArchived = true;
                    draft.update();
                } else {
                    const err =
                        (payload && (payload.detail || payload.error))
                        || (resp.responseText || "").substring(0, 400);
                    app.displayErrorMessage("Buttondown " + resp.statusCode + ":\n" + err);
                    context.fail();
                }
            }
        }
    }
}
