#!/bin/bash

# Script to rename blog post files by removing the date prefix
# This script will rename files like YYYY-MM-DD-title.md to title.md

# Change to the blog directory
cd /Users/joshuapsteele/git/joshuapsteele.github.io/content/blog

# Loop through all markdown files in the directory
for file in *.md; do
  # Check if the file follows the pattern YYYY-MM-DD-*.md
  if [[ $file =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}-(.+)$ ]]; then
    # Extract the part after the date
    new_name="${BASH_REMATCH[1]}"
    
    # Rename the file
    echo "Renaming '$file' to '$new_name'"
    mv "$file" "$new_name"
  else
    echo "Skipping '$file' (doesn't match the date pattern)"
  fi
done

echo "Renaming complete!"
