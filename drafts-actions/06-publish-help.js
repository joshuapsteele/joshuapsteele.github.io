// Publish: Help - creates starter drafts and copies a publishing cheat sheet.
//
// Optional convenience action. It does not publish anything. It either:
//   - fills the current empty draft with a starter template, or
//   - creates a new draft if the current draft already has content.
//
// Install as a Drafts action named "Publish: Help".

const cheatSheet = [
    "Publish format cheat sheet",
    "",
    "Default: use the Publish action. It guesses and prompts unless the draft has a destination tag/frontmatter.",
    "",
    "Note -> joshuapsteele.com/notes/",
    "Just write the note. Inline #tags become Hugo tags.",
    "",
    "Reply note -> joshuapsteele.com/notes/",
    "---",
    "destination: note",
    "in_reply_to: \"https://example.com/original-post\"",
    "tags: []",
    "---",
    "",
    "Write your reply here.",
    "",
    "Link -> links.joshuapsteele.com",
    "https://example.com/article",
    "",
    "Why this is worth saving. Inline #tags become LinkLog tags.",
    "",
    "Blog -> joshuapsteele.com/blog/",
    "Title on the first line",
    "",
    "Markdown body here.",
    "",
    "Safer blog template:",
    "---",
    "destination: post",
    "title: \"Working title\"",
    "draft: true",
    "tags: []",
    "categories: []",
    "---",
    "",
    "Newsletter -> Buttondown draft",
    "---",
    "destination: newsletter",
    "subject: \"Subject line\"",
    "---",
    "",
    "Newsletter body here.",
    "",
    "Direct destination tags: post, link, note, newsletter. The old micro tag aliases to note."
].join("\n");

const templates = {
    note: {
        label: "Note",
        tags: ["note", "drafting"],
        content: [
            "Write the note here. #tag",
            "",
            "<!-- Run Publish or Publish: Note when ready. -->"
        ].join("\n")
    },
    reply: {
        label: "Reply Note",
        tags: ["note", "drafting"],
        content: [
            "---",
            "destination: note",
            "in_reply_to: \"https://example.com/original-post\"",
            "tags: []",
            "---",
            "",
            "Write your reply here.",
            "",
            "<!-- Run Publish or Publish: Note when ready. The in_reply_to URL is preserved in Hugo and the feed. -->"
        ].join("\n")
    },
    link: {
        label: "Link",
        tags: ["link", "drafting"],
        content: [
            "https://example.com/article",
            "",
            "Why this is worth saving. #tag",
            "",
            "<!-- Run Publish or Publish: Link when ready. -->"
        ].join("\n")
    },
    post: {
        label: "Blog",
        tags: ["post", "drafting"],
        content: [
            "---",
            "destination: post",
            "title: \"Working title\"",
            "draft: true",
            "tags: []",
            "categories: []",
            "---",
            "",
            "Write the post here.",
            "",
            "<!-- Run Publish or Publish: Blog when ready. draft: true keeps it out of the live site. -->"
        ].join("\n")
    },
    newsletter: {
        label: "Newsletter",
        tags: ["newsletter", "drafting"],
        content: [
            "---",
            "destination: newsletter",
            "subject: \"Subject line\"",
            "---",
            "",
            "Write the newsletter here.",
            "",
            "<!-- Run Publish or Publish: Newsletter when ready. Buttondown receives a draft, not a send. -->"
        ].join("\n")
    }
};

function prepareDraft(kind) {
    const template = templates[kind];
    if (!template) return;

    const currentIsEmpty = !draft.content || draft.content.trim().length === 0;
    const target = currentIsEmpty ? draft : Draft.create();
    target.content = template.content;

    template.tags.forEach(function (tag) {
        if (!target.hasTag(tag)) target.addTag(tag);
    });

    target.update();

    if (typeof editor !== "undefined" && editor.load) {
        editor.load(target);
    }

    app.displaySuccessMessage(template.label + " starter draft ready.");
}

const p = Prompt.create();
p.title = "Publish: Help";
p.message = "Create a starter draft, or copy the quick format cheat sheet.";
p.addButton("New note", "note");
p.addButton("New reply note", "reply");
p.addButton("New link", "link");
p.addButton("New blog draft", "post");
p.addButton("New newsletter draft", "newsletter");
p.addButton("Copy cheat sheet", "cheatsheet");
p.addButton("Cancel", "cancel", true);

if (!p.show() || p.buttonPressed === "cancel") {
    context.cancel();
} else if (p.buttonPressed === "cheatsheet") {
    app.setClipboard(cheatSheet);
    app.displaySuccessMessage("Publishing cheat sheet copied.");
} else {
    prepareDraft(p.buttonPressed);
}
