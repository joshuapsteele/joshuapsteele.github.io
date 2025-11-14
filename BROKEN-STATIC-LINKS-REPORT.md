# Broken Static File Links Report

**Generated:** 2025-11-14
**Script:** `check-static-files.py`

## Executive Summary

This report catalogs all broken links to images and files in your `/content` directory that reference missing files in your `/static` directory. At some point in this repository's history, files were removed from `/static` that are still referenced in content.

### Summary Statistics

- **Total content files scanned:** 352
- **Files with file references:** 69
- **Working local links:** 49
- **Broken local links:** 60
- **External links (not checked):** 71

## Broken Links by File Type

### DOCX Files (2 broken)

1. **content/blog/justification-and-sanctification.md**
   - Missing: `wp-content/uploads/2018/11/19.-Justification-and-Sanctification.docx`
   - Reference: `[Justification and Sanctification Handout (Word)](https://joshuapsteele.com/wp-content/uploads/2018/11/19.-Justification-and-Sanctification.docx)`

2. **content/blog/12-prayers-for-tough-days.md**
   - Missing: `wp-content/uploads/2020/03/56-Occasional-Prayers.docx`
   - Reference: `[download a Word document containing all of the Occasional Prayers here](https://joshuapsteele.com/wp-content/uploads/2020/03/56-Occasional-Prayers.docx)`

### MP3 Files (1 broken)

1. **content/blog/getting-ahead-in-gods-upside-down-kingdom.md**
   - Missing: `wp-content/uploads/2017/01/01-29-17JSGeetingAheadinGodsUpsideDownKingdom.mp3`
   - Reference: `[[MP3: Getting Ahead in God's Upside-Down Kingdom](https://joshuapsteele.com/wp-content/uploads/2017/01/01-29-17JSGeetingAheadinGodsUpsideDownKingdom.mp3)`

### JPEG Files (4 broken)

1. **content/blog/with-baby-2-on-the-way-im-looking-for-work.md**
   - Missing: `wp-content/uploads/2019/11/624D6A25-2774-4BE3-BE83-61358C989530_1_105_c.jpeg`

2. **content/blog/home-gym-upgrades.md** (3 images)
   - Missing: `wp-content/uploads/2024/03/88604851-219F-4B94-9407-A6F57BA76469_1_105_c-225x300.jpeg`
   - Missing: `wp-content/uploads/2024/03/1875C5E6-A076-47DC-B938-7E3BF3CCB14F_1_105_c-225x300.jpeg`
   - Missing: `wp-content/uploads/2024/03/335E5B22-71CB-4002-B957-128C0EBE0BBA_1_105_c-225x300.jpeg`

### PNG Files (11 broken)

1. **content/blog/thank-god-i-went-to-cedarville.md**
   - Missing: `wp-content/uploads/2016/05/pablo-10-300x300.png`

2. **content/blog/an-outline-of-karl-barths-church-dogmatics.md**
   - Missing: `wp-content/uploads/2019/09/BarthTimeline-2-1024x536-1024x536.png`

3. **content/blog/inductive-bible-study-7-steps-amy-chase-ashley.md**
   - Missing: `wp-content/uploads/2013/06/this-is-not-a-bag-of-trail-mix-you-cant-just-pick-out-the-p.png`

4. **content/blog/barth-timeline-a-chronology-of-karl-barths-life.md** (5 screenshots)
   - Missing: `wp-content/uploads/2019/11/Screen-Shot-2019-11-12-at-9.31.49-AM.png`
   - Missing: `wp-content/uploads/2019/11/Screen-Shot-2019-11-12-at-9.32.26-AM.png`
   - Missing: `wp-content/uploads/2019/11/Screen-Shot-2019-11-12-at-9.32.44-AM.png`
   - Missing: `wp-content/uploads/2019/11/Screen-Shot-2019-11-12-at-9.56.33-AM.png`
   - Missing: `wp-content/uploads/2019/11/Screen-Shot-2019-11-12-at-9.56.54-AM.png`

5. **content/blog/my-uncle-timothy-steele.md**
   - Missing: `wp-content/uploads/2015/10/image.png`

6. **content/blog/my-karl-barth-software-drama-continues-inaccurate-page-numbers-in-logos.md** (2 screenshots)
   - Missing: `wp-content/uploads/2018/12/Screen-Shot-1-2018-12-11-at-2.26.08-PM-1024x546.png`
   - Missing: `wp-content/uploads/2018/12/Screen-Shot-2-2018-12-11-at-2.28.06-PM.png`

### JPG Files (42 broken)

#### Most Affected Posts:

1. **content/blog/maundy-thursday-sermon-the-lasting-supper-luke-2214-30.md** (11 slide images)
   - Missing: `wp-content/uploads/2017/04/Slide2.jpg` through `Slide12.jpg`
   - These appear to be sermon slide images

2. **content/blog/finding-a-hat-for-my-big-bald-head.md** (9 images)
   - Missing: Multiple images from `wp-content/uploads/2024/04/IMG_*.jpg`
   - Hat review photos

3. **content/blog/what-im-reading.md** (7 images)
   - Missing: Multiple images from `wp-content/uploads/2016/05/IMG_*.jpg`
   - Book photos

4. **content/blog/barth-timeline-a-chronology-of-karl-barths-life.md** (included in PNG section)

5. **content/blog/dangerous-beauty-phoenix-grand-canyon-trip-2018.md** (4 images)
   - Missing: `wp-content/uploads/2018/03/IMG_3618-1024x768.jpg`
   - Missing: `wp-content/uploads/2018/03/IMG_3626-1024x768.jpg`
   - Missing: `wp-content/uploads/2018/03/IMG_3663.jpg`
   - Missing: `wp-content/uploads/2018/03/IMG_3743.jpg`

6. **content/blog/eva-joy-steele-a-birth-story.md** (3 images)
   - Missing: `wp-content/uploads/2018/08/Cook-Catheter.jpg`
   - Missing: `wp-content/uploads/2018/08/Cook-Catheter-Insertion.jpg`
   - Missing: `wp-content/uploads/2018/08/thumb_DSC_0060_1024.jpg`

7. **content/blog/the-feast-of-st-james-the-apostle-a-homily-for-ministers.md** (2 images)
   - Missing: `wp-content/uploads/2016/07/Guido_Reni_-_Saint_James_the_Greater_-_Google_Art_Project-218x300.jpg`
   - Missing: `wp-content/uploads/2016/07/Rembrandt_-_Sankt_Jakobus_der_Ältere-247x300.jpg`

8. **content/blog/my-karl-barth-software-drama-continues-inaccurate-page-numbers-in-logos.md** (2 screenshots - included in PNG section)

9. Other single-image posts:
   - **white-noise-bhopal-and-the-hyperreal-fear-of-death.md**: `wp-content/uploads/2014/04/73df8-ekg_flatline1024x682.jpg`
   - **kettlebell-swings-back-balm-for-the-sedentary-seminarian.md**: `wp-content/uploads/2016/05/IMG_0472-e1464220672909-300x225.jpg`
   - **lets-take-seth-godin-to-church.md**: `wp-content/uploads/2016/05/img_0502-225x300.jpg`
   - **death-in-his-grave.md**: `wp-content/uploads/2024/03/8386667037_5ea61844da_o.jpg`
   - **only-the-suffering-god-can-help.md**: `wp-content/uploads/2019/04/img_0297.jpg`
   - **3-confessions-expectant-father.md**: `wp-content/uploads/2018/02/IMG_3515-e1519734672450-1024x777.jpg`

## Complete List of Broken Links

All 60 broken links are documented in the `broken-static-links.json` file with:
- Source file path
- Original reference
- Normalized file path
- Context (the exact match in the file)

## Recommendations

### Option 1: Recover from Git History
Check if these files exist in your git history and can be restored:
```bash
git log --all --full-history -- "static/wp-content/uploads/**"
```

### Option 2: Remove References
For files that are no longer available or needed, remove the broken references from content files.

### Option 3: Replace with Alternatives
For important images (like those in high-traffic posts), consider:
- Finding alternative images
- Using placeholder images with appropriate attribution
- Creating new diagrams/screenshots where applicable

### Option 4: Add Missing Content Notes
For posts with multiple missing images, consider adding a note at the top:
```markdown
*Note: Some images from this post are no longer available.*
```

## Next Steps

1. **Prioritize by Impact**: Focus first on posts with multiple broken links (see "Most Affected Files" list above)
2. **Check Git History**: Attempt to recover recently deleted files
3. **Decide on Strategy**: Determine which files to recover, which to replace, and which references to remove
4. **Update Content**: Make systematic updates to affected files
5. **Re-run Check**: Run `python3 check-static-files.py` after fixes to verify

## Files Generated

- `broken-static-links.json` - Machine-readable catalog of all broken links
- `check-static-files.py` - Python script to check for broken links
- `BROKEN-STATIC-LINKS-REPORT.md` - This human-readable report
