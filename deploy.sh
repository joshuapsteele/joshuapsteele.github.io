#!/bin/bash

# 1. Build the Hugo site, outputting to the /docs directory
echo "Building Hugo site..."
hugo --gc --cleanDestinationDir

# 2. Add changes to git
echo "Adding changes to git..."
git add .

# 3. Commit changes
msg="Update site on $(date)"
if [ -n "$*" ]; then
    msg="$*"
fi
echo "Committing changes with message: '$msg'"
git commit -m "$msg"

# 4. Push the changes to the main branch
echo "Pushing to GitHub..."
git push origin main

echo "Deployment complete!"
