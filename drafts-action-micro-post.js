// Micro Post to Hugo - for quick notes without titles
// Creates a short post using the first few words as the filename

// Get and validate draft content
const content = draft.content.trim();
if (content && content.length > 0) {
  // Get current date and time for filename and front matter
  const now = new Date();
  const date = now.toISOString().split('T')[0]; // YYYY-MM-DD
  const timestamp = now.toISOString(); // Full ISO timestamp

  // Use first 50 characters for filename (cleaned up)
  let filenameBase = content.substring(0, 50)
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, '-')
    .replace(/^-|-$/g, '');

  if (!filenameBase || filenameBase.length === 0) {
    // Fallback to timestamp-based filename if content doesn't produce valid filename
    filenameBase = `micro-${now.getTime()}`;
  }

  // Truncate and add timestamp to make unique
  const shortTime = now.toISOString().substring(11, 16).replace(':', ''); // HHMM
  const filename = `${filenameBase.substring(0, 40)}-${shortTime}.md`;

  // Create post content with minimal front matter (no title)
  const postContent = `---
date: ${timestamp}
draft: false
tags: ["micro"]
categories: ["Notes"]
---

${content}`;

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

    // Check if file already exists (unlikely with timestamp, but check anyway)
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
      message: sha ? `Update micro post: ${filename}` : `Add micro post: ${filename}`,
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
        "✅ Micro post published!\n\n" +
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
  app.displayErrorMessage("❌ Draft is empty! Please add content.");
  context.cancel();
}
