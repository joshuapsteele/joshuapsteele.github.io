# Obsidian Blog Post Templates

These templates are designed for use with Obsidian to create blog posts for this Hugo site.

## Available Templates

### 1. Full Blog Post (`blog-post-full.md`)
**Use for**: Complete articles with full metadata and structure

**Contains**:
- Title
- Date (auto-filled)
- Description field
- Tags and categories arrays
- Basic heading structure

**Best for**: Long-form articles, tutorials, detailed posts

---

### 2. Quick Blog Post (`blog-post-quick.md`)
**Use for**: Simple posts with minimal structure

**Contains**:
- Title
- Date (auto-filled)
- Empty tags/categories
- Minimal content area

**Best for**: Short thoughts, announcements, simple posts

---

### 3. Micro Post (`blog-post-micro.md`)
**Use for**: Twitter-style quick notes without titles

**Contains**:
- Full ISO timestamp (date + time)
- Auto-tagged as "micro"
- Auto-categorized as "Notes"
- No title field

**Best for**: Quick thoughts, links, brief observations

---

### 4. Reply Post (`blog-post-reply.md`)
**Use for**: Responding to others' blog posts

**Contains**:
- Title prefixed with "Re:"
- `in_reply_to` field for the original post URL
- Space for quoting original
- Date (auto-filled)

**Best for**: IndieWeb replies, responding to other blogs

**Note**: The reply context will automatically display on your published post using the `in_reply_to` URL.

---

### 5. Draft Post (`blog-post-draft.md`)
**Use for**: Work-in-progress posts

**Contains**:
- `draft: true` flag (won't publish)
- Built-in checklist for completion
- Full metadata fields

**Best for**: Posts you want to work on over time before publishing

---

## Setup in Obsidian

### Method 1: Obsidian Core Templates Plugin

1. **Enable Templates Plugin**:
   - Settings → Core plugins → Templates → Enable
   - Settings → Templates → Template folder location → Set to `templates`

2. **Use a Template**:
   - Create new note in `content/blog/`
   - Press Cmd+P (Mac) or Ctrl+P (Windows/Linux)
   - Type "Insert template"
   - Choose your template

### Method 2: Templater Plugin (More Powerful)

1. **Install Templater**:
   - Settings → Community plugins → Browse
   - Search "Templater" → Install → Enable
   - Settings → Templater → Template folder location → `templates`

2. **Use a Template**:
   - Create new note in `content/blog/`
   - Press Alt+E (or your configured hotkey)
   - Choose your template
   - Templater will fill in dates automatically

**Templater advantages**:
- Better date formatting
- Custom prompts for fields
- Can auto-generate filenames
- More powerful template syntax

### Method 3: Manual Copy-Paste

1. Open a template file from `templates/`
2. Copy the content
3. Create new file in `content/blog/`
4. Paste and fill in details

---

## Template Syntax Explained

### Obsidian Template Variables

- `{{title}}` - Prompts for title (Obsidian core) or uses note title
- `{{date:YYYY-MM-DD}}` - Inserts current date in Hugo format
- `{{date:YYYY-MM-DDTHH:mm:ssZ}}` - Inserts full ISO timestamp

### Hugo Front Matter Fields

- `title:` - Post title (appears as H1, used in SEO)
- `date:` - Publication date (YYYY-MM-DD format)
- `description:` - SEO description, post summary
- `tags:` - Array of tags (e.g., `["hugo", "blogging"]`)
- `categories:` - Array of categories (e.g., `["Tech", "Writing"]`)
- `draft:` - If `true`, post won't be published
- `in_reply_to:` - URL of post you're replying to (for reply posts)

---

## Filename Conventions

**For titled posts**: Use kebab-case matching the title
- Example: `my-awesome-post.md`

**For micro posts**: Use first few words + timestamp
- Example: `thinking-about-indieweb-1430.md`

**Hugo will generate URLs** from filenames:
- `my-awesome-post.md` → `joshuapsteele.com/blog/my-awesome-post`

---

## Workflow: Obsidian Vault Setup

### Option A: Vault = Blog Repo (Recommended)

1. Open Obsidian
2. "Open folder as vault" → Choose `/Users/joshuapsteele/git/joshuapsteele.github.io`
3. Now you can edit blog posts directly in Obsidian
4. Use Git for version control

**Pros**: One location, seamless workflow
**Cons**: Blog files mixed with Obsidian config

### Option B: Separate Vault with Folder Link

1. Create a new Obsidian vault for blog drafts
2. Write posts in vault
3. When ready to publish, move to `content/blog/` in repo
4. Use Git to commit and push

**Pros**: Clean separation between drafts and published
**Cons**: Extra step to move files

### Option C: Symbolic Link

1. Create symlink from Obsidian vault to `content/blog/`:
   ```bash
   ln -s /Users/joshuapsteele/git/joshuapsteele.github.io/content/blog ~/Documents/ObsidianVault/blog
   ```
2. Write in Obsidian vault's `blog/` folder
3. Files appear in both locations

**Pros**: Best of both worlds
**Cons**: Slightly more complex setup

---

## Publishing Workflow

### With Obsidian Git Plugin (Desktop)

1. Settings → Community plugins → Obsidian Git → Install
2. Configure auto-commit settings
3. Write in Obsidian
4. Plugin auto-commits and pushes
5. GitHub Actions builds automatically

### With Working Copy (Mobile)

1. Install Working Copy app
2. Clone blog repo
3. Link Working Copy to Obsidian (Working Copy has this feature)
4. Write in Obsidian
5. Switch to Working Copy to commit/push

### With Git Command Line

1. Write in Obsidian
2. Terminal:
   ```bash
   cd ~/git/joshuapsteele.github.io
   git add content/blog/your-post.md
   git commit -m "Add: Your Post Title"
   git push
   ```

---

## Tips & Best Practices

### Tags
Maintain consistency - check existing tags before creating new ones:
- Common tags: `hugo`, `blogging`, `tech`, `theology`, `writing`
- Use lowercase for tags
- Be specific but not too granular

### Categories
Keep categories broad:
- Tech
- Writing
- Theology
- Personal
- Notes (for micro posts)

### Descriptions
- Keep to 1-2 sentences
- Include key terms for SEO
- Make it compelling - shows in search results

### Images
1. Place images in `static/images/`
2. Reference in posts: `![Alt text](/images/my-image.jpg)`

### Drafts
- Use `draft: true` for work-in-progress
- Drafts won't appear on live site
- Preview locally with `npm run dev`

---

## Keyboard Shortcuts (Recommended)

Set these in Obsidian Settings → Hotkeys:

- **Templates: Insert template**: `Cmd+T` (Mac) / `Ctrl+T` (Windows)
- **Command palette**: `Cmd+P` (Mac) / `Ctrl+P` (Windows)
- **Open daily note**: `Cmd+D` (for daily posting habits)

---

## Troubleshooting

### Template variables not working
- Check that Templates core plugin is enabled
- Or install Templater for more features
- Verify template folder location in settings

### Posts not publishing
- Check `draft:` is set to `false`
- Verify front matter YAML syntax (no tabs, proper indentation)
- Check file is in `content/blog/` directory
- Verify GitHub Actions build succeeded

### Dates in wrong format
- Hugo requires: `YYYY-MM-DD` (e.g., `2025-12-12`)
- For timestamps: `YYYY-MM-DDTHH:mm:ssZ`
- Templater handles this automatically

### Tags/categories not appearing
- Ensure proper YAML array syntax: `["tag1", "tag2"]`
- No spaces after colons unless quoted
- Rebuild site with `npm run build`

---

## Related Documentation

- **Drafts Actions**: See `DRAFTS-ACTIONS.md` for mobile publishing
- **Hugo Guide**: See `CLAUDE.md` for full site documentation
- **Obsidian Docs**: https://help.obsidian.md/

---

## Template Customization

Feel free to modify these templates for your needs:
1. Edit template files in this directory
2. Add custom front matter fields
3. Change default tags/categories
4. Add boilerplate content sections

Templates are just starting points - customize them to fit your workflow!
