#!/bin/bash
# Review auto-generated description changes

echo "================================"
echo "REVIEWING AUTO-GENERATED CHANGES"
echo "================================"
echo ""

# Function to show before/after for a file
review_file() {
    local file=$1
    local basename=$(basename "$file")

    echo "📄 $basename"
    echo "   Path: $file"

    # Get old description
    local old_desc=$(git show HEAD:"$file" 2>/dev/null | grep "^description:" | head -1 | sed 's/^description: //')
    # Get new description
    local new_desc=$(grep "^description:" "$file" 2>/dev/null | head -1 | sed 's/^description: //')

    if [ -n "$old_desc" ] || [ -n "$new_desc" ]; then
        echo "   OLD: $old_desc"
        echo "   NEW: $new_desc"
    else
        echo "   (No description change detected)"
    fi
    echo ""
}

# Review pages
echo "=== PAGES (41 files) ==="
echo ""
for file in content/pages/*.md; do
    if git status --short "$file" 2>/dev/null | grep -q "^ M"; then
        review_file "$file"
    fi
done

# Review other files
echo "=== OTHER FILES ==="
echo ""
if git status --short content/files.md 2>/dev/null | grep -q "^ M"; then
    review_file content/files.md
fi
