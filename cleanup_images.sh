#!/bin/bash

# Hugo Site Image Cleanup Script
# This script removes unused legacy WordPress images and external downloads
# while preserving actually used images and core infrastructure

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

STATIC_DIR="/Users/joshuapsteele/git/joshuapsteele.github.io/static"
BACKUP_DIR="/Users/joshuapsteele/git/joshuapsteele.github.io/image_backup_$(date +%Y%m%d_%H%M%S)"

echo -e "${YELLOW}Hugo Site Image Cleanup Script${NC}"
echo "=================================="

# Check if static directory exists
if [ ! -d "$STATIC_DIR" ]; then
    echo -e "${RED}Error: Static directory not found: $STATIC_DIR${NC}"
    exit 1
fi

# Show current size
echo -e "${YELLOW}Current static directory size:${NC}"
du -sh "$STATIC_DIR"

# Calculate sizes to be removed
echo -e "\n${YELLOW}Analyzing directories to remove...${NC}"

if [ -d "$STATIC_DIR/wp-content" ]; then
    WP_SIZE=$(du -sh "$STATIC_DIR/wp-content" | cut -f1)
    echo "WordPress uploads: $WP_SIZE"
fi

if [ -d "$STATIC_DIR/http:" ]; then
    HTTP_SIZE=$(du -sh "$STATIC_DIR/http:" | cut -f1)
    echo "HTTP downloads: $HTTP_SIZE"
fi

if [ -d "$STATIC_DIR/https:" ]; then
    HTTPS_SIZE=$(du -sh "$STATIC_DIR/https:" | cut -f1)
    echo "HTTPS downloads: $HTTPS_SIZE"
fi

# Confirm deletion
echo -e "\n${YELLOW}This script will:${NC}"
echo "1. Create a backup at: $BACKUP_DIR"
echo "2. Remove the following directories:"
echo "   - wp-content/ (legacy WordPress uploads)"
echo "   - http:/ (downloaded external images)"
echo "   - https:/ (downloaded external images)"
echo ""
echo -e "${GREEN}Files that will be PRESERVED:${NC}"
echo "- All favicons and app icons"
echo "- Logo files (RevDev)"
echo "- Core theme images (/images/)"
echo "- Actually used images:"
echo "  - craftsman_table_saw_manual_*.jpg"
echo "  - new-rip-fence-handle*.jpeg"
echo "  - refurbished-table-saw.jpeg"
echo "  - rip-fence-handle-epoxy.jpeg"
echo "  - ibrahim-rifath-OApHds2yEGQ-unsplash.jpg"

echo -e "\n${RED}WARNING: This will permanently delete the specified directories!${NC}"
read -p "Do you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Create backup
echo -e "\n${YELLOW}Creating backup...${NC}"
mkdir -p "$BACKUP_DIR"

if [ -d "$STATIC_DIR/wp-content" ]; then
    echo "Backing up wp-content..."
    cp -r "$STATIC_DIR/wp-content" "$BACKUP_DIR/"
fi

if [ -d "$STATIC_DIR/http:" ]; then
    echo "Backing up http: directory..."
    cp -r "$STATIC_DIR/http:" "$BACKUP_DIR/"
fi

if [ -d "$STATIC_DIR/https:" ]; then
    echo "Backing up https: directory..."
    cp -r "$STATIC_DIR/https:" "$BACKUP_DIR/"
fi

echo -e "${GREEN}Backup created successfully!${NC}"

# Perform cleanup
echo -e "\n${YELLOW}Performing cleanup...${NC}"

if [ -d "$STATIC_DIR/wp-content" ]; then
    echo "Removing wp-content directory..."
    rm -rf "$STATIC_DIR/wp-content"
fi

if [ -d "$STATIC_DIR/http:" ]; then
    echo "Removing http: directory..."
    rm -rf "$STATIC_DIR/http:"
fi

if [ -d "$STATIC_DIR/https:" ]; then
    echo "Removing https: directory..."
    rm -rf "$STATIC_DIR/https:"
fi

# Show results
echo -e "\n${GREEN}Cleanup completed!${NC}"
echo -e "${YELLOW}New static directory size:${NC}"
du -sh "$STATIC_DIR"

echo -e "\n${YELLOW}Summary:${NC}"
echo "- Backup created at: $BACKUP_DIR"
echo "- Removed legacy WordPress uploads"
echo "- Removed downloaded external images"
echo "- Preserved all actually used images and core files"

echo -e "\n${GREEN}Your site's image footprint has been significantly reduced!${NC}"
echo -e "${YELLOW}Next steps:${NC}"
echo "1. Test your site to ensure everything still works"
echo "2. If everything looks good, you can delete the backup directory"
echo "3. Consider implementing Hugo's image processing for future images"