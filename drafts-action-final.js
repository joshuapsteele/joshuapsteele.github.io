// Quick Blog Post to Hugo - Production Version
// Creates a blog post from the draft and publishes to GitHub

// Get and validate draft content
const content = draft.content.trim();
if (content && content.length > 0) {
  // Extract title from first line
  const lines = content.split("\n");
  const title = lines[0].replace(/^#\s*/, '').trim();

  if (title && title.length > 0) {
    // Extract body (everything after first line)
    const body = lines.slice(1).join("\n").trim();

    // Generate filename from title (kebab-case, max 60 chars)
    let filename = title.toLowerCase()
      .replace(/[^a-z0-9]+/g, '-')
      .replace(/^-|-$/g, '');

    if (filename && filename.length > 0) {
      filename = filename.substring(0, 60) + '.md';

      // Get current date in ISO format (YYYY-MM-DD)
      const now = new Date();
      const date = now.toISOString().split('T')[0];

      // Create post content with front matter
      const postContent = `---
title: "${title}"
date: ${date}
draft: false
tags: []
categories: []
---

${body}`;

      // Get GitHub token from credential
      const credential = Credential.create("GitHub Blog Token", "Enter your GitHub Personal Access Token");
      credential.addPasswordField("token", "GitHub Token");
      credential.authorize();

      const token = credential.getValue("token");

      if (token) {
        // GitHub API configuration
        const repo = "joshuapsteele/joshuapsteele.github.io";
        const path = `content/blog/${filename}`;
        const base64Content = Base64.encode(postContent);

        // Check if file already exists
        const checkUrl = `https://api.github.com/repos/${repo}/contents/${path}`;
        const checkHttp = HTTP.create();
        const checkResponse = checkHttp.request({
          url: checkUrl,
          method: "GET",
          headers: {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github.v3+json"
          }
        });

        // Get SHA if file exists (needed for updates)
        let sha = null;
        if (checkResponse.statusCode === 200) {
          const existingData = JSON.parse(checkResponse.responseText);
          sha = existingData.sha;
        }

        // Prepare request body
        const requestBody = {
          message: sha ? `Update: ${title}` : `Add: ${title}`,
          content: base64Content,
          branch: "main"
        };

        if (sha) {
          requestBody.sha = sha;
        }

        // Create or update the file
        const putUrl = `https://api.github.com/repos/${repo}/contents/${path}`;
        const http = HTTP.create();
        const response = http.request({
          url: putUrl,
          method: "PUT",
          headers: {
            "Authorization": "Bearer " + token,
            "Accept": "application/vnd.github.v3+json",
            "Content-Type": "application/json"
          },
          data: requestBody
        });

        // Handle response
        if (response.statusCode === 200 || response.statusCode === 201) {
          const webUrl = `https://joshuapsteele.com/blog/${filename.replace('.md', '')}`;

          app.displaySuccessMessage(
            "✅ Post published!\n\n" +
            "File: " + filename + "\n\n" +
            "It will be live at:\n" + webUrl + "\n\n" +
            "(Allow a few minutes for GitHub Actions to build)"
          );
        } else {
          app.displayErrorMessage(
            "❌ Failed to publish\n\n" +
            "Status: " + response.statusCode + "\n\n" +
            response.responseText
          );
          context.fail();
        }
      } else {
        app.displayErrorMessage("❌ GitHub token not found! Please set up the credential.");
        context.cancel();
      }
    } else {
      app.displayErrorMessage("❌ Could not generate filename from title: '" + title + "'");
      context.cancel();
    }
  } else {
    app.displayErrorMessage("❌ Title is required! First line should be the title.");
    context.cancel();
  }
} else {
  app.displayErrorMessage("❌ Draft is empty! Please add content.");
  context.cancel();
}
