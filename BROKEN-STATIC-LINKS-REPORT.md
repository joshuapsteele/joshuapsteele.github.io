# Broken Static File Links Report

**Generated:** 2025-11-14 (Updated after wp-content-cleanup merge)
**Script:** `check-static-files.py`

## Executive Summary

After merging the wp-content-cleanup branch, broken links decreased from **60 to just 12** (80% improvement!). The remaining broken links are concentrated in only 2 blog posts and involve missing full-size versions of images where only thumbnails exist.

### Summary Statistics

- **Total content files scanned:** 352
- **Files with file references:** 69
- **Working local links:** 97 (was 49)
- **Broken local links:** 12 (was 60)
- **External links (not checked):** 71

## Progress Since Initial Analysis

| Metric | Before Merge | After Merge | Improvement |
|--------|--------------|-------------|-------------|
| Broken Links | 60 | 12 | 80% reduction |
| Working Links | 49 | 97 | 98% increase |
| Affected Posts | 20 | 2 | 90% reduction |

## Remaining Broken Links (12 total)

### 1. Maundy Thursday Sermon (11 broken links)

**File:** `content/blog/maundy-thursday-sermon-the-lasting-supper-luke-2214-30.md`

**Issue:** Content references full-size sermon slide images, but only thumbnail versions (`-150x150.jpg`) were restored.

Missing files (full-size versions):
- `wp-content/uploads/2017/04/Slide2.jpg`
- `wp-content/uploads/2017/04/Slide3.jpg`
- `wp-content/uploads/2017/04/Slide4.jpg`
- `wp-content/uploads/2017/04/Slide5.jpg`
- `wp-content/uploads/2017/04/Slide6.jpg`
- `wp-content/uploads/2017/04/Slide7.jpg`
- `wp-content/uploads/2017/04/Slide8.jpg`
- `wp-content/uploads/2017/04/Slide9.jpg`
- `wp-content/uploads/2017/04/Slide10.jpg`
- `wp-content/uploads/2017/04/Slide11.jpg`
- `wp-content/uploads/2017/04/Slide12.jpg`

Available (thumbnail versions):
- All slides exist as `Slide#-150x150.jpg` (150x150px thumbnails)

### 2. St. James the Apostle (1 broken link)

**File:** `content/blog/the-feast-of-st-james-the-apostle-a-homily-for-ministers.md`

**Issue:** Missing Rembrandt painting image.

Missing file:
- `wp-content/uploads/2016/07/Rembrandt_-_Sankt_Jakobus_der_Ältere-247x300.jpg`

Note: A different painting by Guido Reni exists in the same directory: `Guido_Reni_-_Saint_James_the_Greater_-_Google_Art_Project-218x300.jpg`

## Fix Options

### Option 1: Update Content to Use Thumbnail Images (Quick Fix for Slides)

For the sermon slides, update the post to reference the existing `-150x150.jpg` versions. These are small but functional.

**Pros:** Immediate fix, no file recovery needed
**Cons:** Images will be very small (150x150px), may not be legible

### Option 2: Recover Full-Size Images from WordPress Backup

If you have a WordPress backup, extract the full-size versions of:
- `Slide2.jpg` through `Slide12.jpg` (sermon slides)
- `Rembrandt_-_Sankt_Jakobus_der_Ältere-247x300.jpg` (Rembrandt painting)

**Pros:** Best quality, preserves original content
**Cons:** Requires access to WordPress backup

### Option 3: Remove or Replace Broken References

**For sermon slides:**
- Remove the individual slide images and add a note that slides are no longer available
- Or create a PDF from the slides and link to that instead

**For Rembrandt image:**
- Use the existing Guido Reni image instead (different artist but same subject - St. James)
- Find a public domain Rembrandt St. James image online
- Remove the image reference entirely

**Pros:** Clean solution, no broken links
**Cons:** Loses original visual content

### Option 4: Do Nothing (Recommended for Now)

With only 12 broken links across 2 posts (down from 60 across 20 posts), the issue is largely resolved. Consider addressing these on a case-by-case basis if/when you revisit these posts.

**Pros:** 80% of the problem is already solved
**Cons:** 2 posts still have broken image links

## Files Successfully Restored

The wp-content-cleanup merge successfully restored:
- 9 hat review photos (`finding-a-hat-for-my-big-bald-head.md`)
- 7 book photos (`what-im-reading.md`)
- 5 Barth timeline screenshots (`barth-timeline-a-chronology-of-karl-barths-life.md`)
- 4 travel photos (`dangerous-beauty-phoenix-grand-canyon-trip-2018.md`)
- 3 birth story images (`eva-joy-steele-a-birth-story.md`)
- 3 home gym photos (`home-gym-upgrades.md`)
- Multiple DOCX, MP3, and PDF files
- And many more!

## Next Steps

1. **Decide on strategy** for the remaining 12 broken links
2. **Consider Option 4** (do nothing) - 80% improvement is excellent
3. **If fixing sermon slides:** Update references to use `-150x150.jpg` thumbnails or recover full-size from backup
4. **If fixing Rembrandt image:** Update to use Guido Reni image or find alternative
5. **Re-run check:** `python3 check-static-files.py` after any fixes

## Files Generated

- `check-static-files.py` - Python script to scan for broken references
- `broken-static-links.json` - Machine-readable catalog of all issues (updated)
- `BROKEN-STATIC-LINKS-REPORT.md` - This human-readable report (updated)

---

**Conclusion:** The wp-content-cleanup merge was highly successful, resolving 48 of 60 broken links (80%). The remaining 12 broken links are isolated to 2 posts and involve missing full-size images where only thumbnails exist.
