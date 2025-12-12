# Drafts Actions for Hugo Blog Publishing

This directory contains JavaScript files for Drafts app actions that publish directly to this Hugo blog via the GitHub API.

## Prerequisites

1. **GitHub Personal Access Token** with `repo` scope
   - Create at: https://github.com/settings/tokens
   - Select: `repo` (Full control of private repositories)
   - Copy the token and save it securely

2. **Drafts app** (iOS/Mac)
   - Download from: https://getdrafts.com/

## Available Actions

### 1. Quick Blog Post (`drafts-action-final.js`)

**Purpose**: Fast publishing with minimal metadata

**Format**:
```
Post Title Goes Here
First line is the title, everything else is the body.

You can use markdown formatting.
```

**Features**:
- Auto-generates filename from title (kebab-case)
- Sets date automatically
- Creates empty tags/categories arrays
- Sets `draft: false`

**Best for**: Quick posts when you'll add tags/categories later via web interface or local editing

---

### 2. Full Blog Post (`drafts-action-full-post.js`)

**Purpose**: Complete post with all metadata

**Format**:
```
Post Title Goes Here
The body of your post starts here.
```

**Features**:
- Prompts for:
  - Description (optional)
  - Tags (comma-separated)
  - Categories (comma-separated)
  - Draft status (checkbox)
- Auto-generates filename from title
- Sets date automatically

**Example prompt input**:
- Description: `A guide to publishing Hugo posts from Drafts`
- Tags: `hugo, drafts, automation, blogging`
- Categories: `Tech, Writing`
- Save as draft: ☐ (unchecked)

**Best for**: Polished posts where you want to set all metadata upfront

**Note**: For quick micro-blog style posts, use [Micro.blog](https://micro.blog/) instead - it's designed for that workflow and cross-posts to social media automatically.

---

## Setup Instructions

### First Time Setup

1. **Create the GitHub credential in Drafts**:
   - Open Drafts app
   - Go to Settings → Credentials
   - Tap "+" to add new credential
   - Name it: `GitHub Blog Token`
   - Add a password field named: `token`
   - Paste your GitHub Personal Access Token
   - Save

2. **Create a Drafts action for each script**:

   **For Quick Blog Post**:
   - Tap action menu (⚡️ icon) → "+"
   - Name: `Quick Blog Post`
   - Add "Script" step
   - Copy contents of `drafts-action-final.js`
   - Paste into script editor
   - Save

   **For Full Blog Post**:
   - Tap action menu (⚡️ icon) → "+"
   - Name: `Full Blog Post`
   - Add "Script" step
   - Copy contents of `drafts-action-full-post.js`
   - Paste into script editor
   - Save

### Using the Actions

1. Create a new draft in Drafts app
2. Write your content following the format for the action you want
3. Tap the action menu (⚡️)
4. Select the appropriate action
5. If prompted (Full Blog Post), enter metadata
6. Wait for success message
7. Check GitHub Actions build status: https://github.com/joshuapsteele/joshuapsteele.github.io/actions
8. Post will be live in 2-3 minutes

## How It Works

1. **Validation**: Checks that draft has content and (for titled posts) a valid title
2. **Filename Generation**: Creates kebab-case filename from title or content
3. **Front Matter Creation**: Builds YAML front matter with appropriate fields
4. **Base64 Encoding**: Encodes post content for GitHub API
5. **Existence Check**: Checks if file exists (returns 404 if new)
6. **Upload**: Creates or updates file via GitHub API
7. **GitHub Actions**: Automatically builds and deploys site

## Troubleshooting

### "GitHub token not found"
- Go to Drafts Settings → Credentials
- Ensure credential is named exactly: `GitHub Blog Token`
- Ensure password field is named exactly: `token`
- Re-authorize if needed

### "Could not generate filename"
- First line must contain alphanumeric characters to generate a valid filename

### "Failed to publish" (403)
- Token may have expired - generate new one at https://github.com/settings/tokens
- Ensure token has `repo` scope

### "Failed to publish" (422)
- Content may have invalid YAML in front matter
- Check for unescaped quotes in title/description

### Post not appearing on site
- Check GitHub Actions: https://github.com/joshuapsteele/joshuapsteele.github.io/actions
- Look for failed builds
- Wait 2-3 minutes for build to complete

## Customization

You can modify these scripts to:
- Change default tags/categories
- Add custom front matter fields
- Change filename patterns
- Add different validation rules
- Post to different directories

Just edit the `.js` files and update the script in your Drafts action.

## File Locations

After publishing, files are created in:
```
content/blog/your-post-filename.md
```

## Editing Published Posts

To edit a post after publishing:

1. Use Drafts action on content with same title
   - Script will detect existing file and update it
   - OR use GitHub web interface to edit
   - OR pull repo locally, edit, and push

## Notes

- These files are kept in the repo for reference only
- The actual actions live in your Drafts app
- Update the Drafts action if you modify these files
- The `drafts-action-debug.js` version has been removed (no longer needed)

## License

These scripts are part of the website repository and are licensed under the MIT License (see LICENSE-CODE).
