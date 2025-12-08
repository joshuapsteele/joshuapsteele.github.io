#!/bin/bash

# 1. Add changes to git
echo "Adding changes to git..."
git add .

# 2. Commit changes
msg="Update site content $(date +"%Y-%m-%d %H:%M:%S")"
if [ -n "$*" ]; then
    msg="$*"
fi
echo "Committing changes with message: '$msg'"
git commit -m "$msg"

# 3. Push the changes to the main branch
echo "Pushing to GitHub..."
git push origin main

echo "Changes pushed to GitHub. GitHub Actions will handle the build and deployment."
