// Publish — unified router.
//
// Inspects the draft and dispatches to one of four destination actions:
//   • "Publish: Blog"        → joshuapsteele.com long-form (content/blog/, Hugo via GitHub API)
//   • "Publish: Link"        → links.joshuapsteele.com (LinkLog API)
//   • "Publish: Note"        → joshuapsteele.com shortform (content/notes/, Hugo via GitHub API)
//                              Micro.Blog polls /notes/feed.json and fans out to Mastodon + Threads.
//   • "Publish: Newsletter"  → Buttondown (as draft)
//
// Routing signals — `note` is the canonical name for shortform, `micro` is kept
// as an alias for the old tag/frontmatter habit.
//
// Routing priority:
//   1. Frontmatter: `destination: post | link | note | micro | newsletter`
//   2. Tag: `post`, `link`, `note`, `micro`, or `newsletter` on the draft
//   3. Shape heuristic (first line URL, has H1, length, etc.)
//
// With #1 or #2 the router dispatches silently. With #3 the router prompts for
// confirmation. Always offers a disambiguation prompt if nothing can be guessed.
//
// The old `Post to Micro.blog` (Drafts built-in) is left installed as a manual
// fast path for when you want a near-instant Mastodon/Threads post without
// going through Hugo. Invoke it directly from the action list; the router no
// longer calls it.

const content = draft.content.trim();
if (!content) {
    app.displayErrorMessage("Draft is empty.");
    context.cancel();
} else {
    // Inline minimal frontmatter parser (full helper in 00-shared-helpers.js)
    let frontmatter = {};
    let body = content;
    const lines = content.split("\n");
    if (lines[0].trim() === "---") {
        let closingIdx = -1;
        for (let i = 1; i < lines.length; i++) {
            if (lines[i].trim() === "---") { closingIdx = i; break; }
        }
        if (closingIdx !== -1) {
            for (let i = 1; i < closingIdx; i++) {
                const m = lines[i].match(/^(\w+)\s*:\s*(.*)$/);
                if (m) frontmatter[m[1]] = m[2].trim().replace(/^["']|["']$/g, "");
            }
            body = lines.slice(closingIdx + 1).join("\n").replace(/^\n+/, "");
        }
    }

    // Canonical destinations, plus `micro` as an alias for `note`.
    const validDests = ["post", "link", "note", "micro", "newsletter"];
    let destination = null;
    let confident = false;

    // 1. Frontmatter destination
    if (frontmatter.destination && validDests.indexOf(frontmatter.destination) !== -1) {
        destination = frontmatter.destination;
        confident = true;
    }

    // 2. Draft tag (checked in priority order — note before micro)
    if (!destination) {
        for (let i = 0; i < validDests.length; i++) {
            if (draft.hasTag(validDests[i])) {
                destination = validDests[i];
                confident = true;
                break;
            }
        }
    }

    // 3. Shape heuristics
    if (!destination) {
        const bodyLines = body.split("\n");
        const firstLine = bodyLines[0] ? bodyLines[0].trim() : "";
        if (/^https?:\/\//.test(firstLine)) {
            destination = "link";
        } else if (/^#\s+/.test(firstLine) && body.length > 400) {
            destination = "post";
        } else if (body.length < 300 && !/^#\s+/.test(firstLine)) {
            destination = "note";
        }
    }

    // Normalize alias: `micro` → `note` (they route to the same place now).
    if (destination === "micro") destination = "note";

    // 4. Prompt (always, unless confident)
    let chosen = destination;
    if (!confident) {
        const p = Prompt.create();
        p.title = "Publish";
        p.message = destination
            ? "Detected: " + destination.toUpperCase() + ". Confirm or override."
            : "Could not auto-detect. Pick a destination.";

        // Present the four canonical destinations. `micro` is not offered in
        // the prompt because it's an alias that normalizes to `note` above.
        const promptDests = ["post", "link", "note", "newsletter"];
        const order = destination
            ? [destination].concat(promptDests.filter(function (d) { return d !== destination; }))
            : promptDests.slice();
        const labels = {
            post:       "Blog (joshuapsteele.com)",
            link:       "Link (linklog)",
            note:       "Note (shortform → Mastodon/Threads)",
            newsletter: "Newsletter (Buttondown draft)"
        };
        order.forEach(function (d) { p.addButton(labels[d], d); });
        p.addButton("Cancel", "cancel", true);

        if (!p.show() || p.buttonPressed === "cancel") {
            context.cancel();
            chosen = null;
        } else {
            chosen = p.buttonPressed;
        }
    }

    if (chosen) {
        const actionNames = {
            post:       "Publish: Blog",
            link:       "Publish: Link",
            note:       "Publish: Note",              // writes to content/notes/ — Micro.Blog polls the feed
            newsletter: "Publish: Newsletter"
        };
        const a = Action.find(actionNames[chosen]);
        if (!a) {
            app.displayErrorMessage("Action not found: " + actionNames[chosen]);
            context.fail();
        } else {
            // Queue the destination action against THIS draft.
            const ok = app.queueAction(a, draft);
            if (!ok) {
                app.displayErrorMessage("Could not queue: " + actionNames[chosen]);
                context.fail();
            }
            // The queued action will display its own success/failure.
        }
    }
}
