# Static wp-content Audit

**Updated:** 2026-05-21

This is a non-destructive audit of legacy WordPress media under `static/wp-content/`. It does not run `scripts/cleanup_images.sh` and does not delete files.

## Summary

| Metric | Count |
| --- | ---: |
| Files in `static/wp-content/` | 151 |
| Total size | 391.7 MiB |
| Referenced by site sources | 119 |
| Orphan candidates | 32 |
| Source files scanned | 434 |

Site sources scanned: `content/`, `layouts/`, `assets/`, `data/`, `archetypes/`, `templates/`, and Hugo/config files when present. Generated audit files and docs are intentionally excluded so they do not count as live site references.

## By Extension

| Extension | Files | Referenced | Orphan candidates | Size |
| --- | ---: | ---: | ---: | ---: |
| `csv` | 2 | 2 | 0 | 424.8 KiB |
| `docx` | 7 | 2 | 5 | 621.4 KiB |
| `jpeg` | 4 | 4 | 0 | 45.4 KiB |
| `jpg` | 52 | 52 | 0 | 2.2 MiB |
| `m4a` | 4 | 0 | 4 | 37.4 MiB |
| `mp3` | 16 | 9 | 7 | 318.3 MiB |
| `pdf` | 53 | 37 | 16 | 27.4 MiB |
| `png` | 13 | 13 | 0 | 5.3 MiB |

## Referenced Sources

- `content/blog/12-prayers-for-tough-days.md` (1 media reference)
- `content/blog/3-confessions-expectant-father.md` (1 media reference)
- `content/blog/an-outline-of-karl-barths-church-dogmatics.md` (2 media references)
- `content/blog/anti-racism-letter-to-fellow-acna-clergy.md` (2 media references)
- `content/blog/barth-timeline-a-chronology-of-karl-barths-life.md` (5 media references)
- `content/blog/dangerous-beauty-phoenix-grand-canyon-trip-2018.md` (4 media references)
- `content/blog/death-in-his-grave.md` (1 media reference)
- `content/blog/eva-joy-steele-a-birth-story.md` (3 media references)
- `content/blog/finding-a-hat-for-my-big-bald-head.md` (9 media references)
- `content/blog/getting-ahead-in-gods-upside-down-kingdom.md` (2 media references)
- `content/blog/hate-running-try-rucking-instead.md` (7 media references)
- `content/blog/here-are-all-of-william-witts-essays-on-womens-ordination-in-a-single-pdf-with-bookmarks.md` (1 media reference)
- `content/blog/hermeneutical-implications-scriptures-theological-location.md` (1 media reference)
- `content/blog/home-gym-upgrades.md` (3 media references)
- `content/blog/honors-grace-and-generosity.md` (2 media references)
- `content/blog/inductive-bible-study-7-steps-amy-chase-ashley.md` (1 media reference)
- `content/blog/into-the-far-country.md` (1 media reference)
- `content/blog/it-is-finished-so-get-to-work-an-ascension-sermon.md` (1 media reference)
- `content/blog/justification-and-sanctification.md` (2 media references)
- `content/blog/kettlebell-swings-back-balm-for-the-sedentary-seminarian.md` (1 media reference)
- `content/blog/lets-take-seth-godin-to-church.md` (2 media references)
- `content/blog/maundy-thursday-sermon-the-lasting-supper-luke-2214-30.md` (12 media references)
- `content/blog/my-2014-regional-ets-paper-reconciliation-and-the-lack-thereof.md` (1 media reference)
- `content/blog/my-karl-barth-software-drama-continues-inaccurate-page-numbers-in-logos.md` (2 media references)
- `content/blog/my-regional-ets-presentation-reconciliation-and-the-lack-thereof.md` (1 media reference)
- `content/blog/my-uncle-timothy-steele.md` (1 media reference)
- `content/blog/only-the-suffering-god-can-help.md` (1 media reference)
- `content/blog/presenting-on-barth-at-2015-southeastern-ets.md` (1 media reference)
- `content/blog/psalm-2-quare-fremuerunt-gentes.md` (1 media reference)
- `content/blog/reconciliation-and-the-lack-thereof-atonement-ecclesiology-and-the-unity-of-god.md` (1 media reference)
- `content/blog/sermon-the-challenge-of-christmas-light.md` (1 media reference)
- `content/blog/thank-god-i-went-to-cedarville.md` (1 media reference)
- `content/blog/the-feast-of-st-james-the-apostle-a-homily-for-ministers.md` (1 media reference)
- `content/blog/the-hope-of-the-holy-innocents.md` (1 media reference)
- `content/blog/the-tree-of-religion-karl-barth-and-dietrich-bonhoeffer-on-the-tree-of-knowledge-in-genesis-24-324.md` (1 media reference)
- `content/blog/to-be-or-not-to-be-religious-a-clarification-of-karl-barths-and-dietrich-bonhoeffers-divergence-and-convergence-regarding-religion.md` (1 media reference)
- `content/blog/true-christianity-cannot-be-a-private-christianity-barth.md` (1 media reference)
- `content/blog/unrighteous-anger-yoda-jonah-nahum-and-us.md` (1 media reference)
- `content/blog/want-a-taste-of-what-my-dissertation-is-about-read-these-two-passages-dissertation-dispatch-2020-04-03.md` (2 media references)
- `content/blog/what-im-reading.md` (7 media references)
- `content/blog/when-will-thy-kingdom-come-the-timing-and-agency-of-the-kingdom-of-god-in-the-lords-prayer.md` (1 media reference)
- `content/blog/white-noise-bhopal-and-the-hyperreal-fear-of-death.md` (1 media reference)
- `content/blog/why-havent-you-torn-the-sky-open-yet-sermon-first-sunday-of-advent-2020.md` (1 media reference)
- `content/blog/with-baby-2-on-the-way-im-looking-for-work.md` (1 media reference)
- `content/pages/cv.md` (2 media references)
- `content/pages/essays.md` (14 media references)
- `content/pages/sermons.md` (18 media references)

## Largest Orphan Candidates

| Size | Served path |
| ---: | --- |
| 44.9 MiB | `/wp-content/uploads/2015/12/12-28-14JoshSteeleHolyInnocents.mp3` |
| 26.3 MiB | `/wp-content/uploads/2015/12/11-15-15JSHebrews10.mp3` |
| 23.4 MiB | `/wp-content/uploads/2015/12/12-27-15JSTheChallengeofChristmasLight.mp3` |
| 22.6 MiB | `/wp-content/uploads/2015/12/03-29-15_JS_TheCrossShapedGod.mp3` |
| 21.2 MiB | `/wp-content/uploads/2015/12/03-16-14JoshSteele.mp3` |
| 18.7 MiB | `/wp-content/uploads/2015/12/07-05-15JS-Jesusisnotjustoneofus.mp3` |
| 15.1 MiB | `/wp-content/uploads/2015/12/Joshua-Steele-Psalm-32-Sermon-Exegesis-of-Psalms-Dr.-Ross.m4a` |
| 11.2 MiB | `/wp-content/uploads/2015/12/Crisis-Sermon-Psalm-13.m4a` |
| 8.8 MiB | `/wp-content/uploads/2015/12/09-18-16JSTheShrewdManager.mp3` |
| 7.0 MiB | `/wp-content/uploads/2015/12/Psalm-32.m4a` |
| 4.1 MiB | `/wp-content/uploads/2024/05/Corinthians-Chapters_Discovering-Biblical-Equality-Third-Edition.pdf` |
| 4.1 MiB | `/wp-content/uploads/2015/12/Wedding-Sermon-Audio.m4a` |
| 1.1 MiB | `/wp-content/uploads/2016/12/STEELE-Ecclesiology-and-Worship-Final-Project.pdf` |
| 679.5 KiB | `/wp-content/uploads/2013/02/a-contextual-reading-of-romans-13-1-7.pdf` |
| 626.4 KiB | `/wp-content/uploads/2016/12/HANDOUT-Class-Presentation-OUR-TRANSFORMATION-AND-WORSHIP-IN-GLORY.pdf` |
| 612.5 KiB | `/wp-content/uploads/2011/03/sola-diversity.pdf` |
| 560.1 KiB | `/wp-content/uploads/2017/02/STEELE-Anglican-History-and-Doctrine-Midterm-Middle-Way-is-Still-a-Way.pdf` |
| 439.8 KiB | `/wp-content/uploads/2013/12/philemon.pdf` |
| 429.1 KiB | `/wp-content/uploads/2016/12/Disunity_as_Ecclesiological_Impossibilit-2.pdf` |
| 419.5 KiB | `/wp-content/uploads/2016/12/STEELE-Anglican-History-and-Doctrine-Final-Faithful-Anglican-Developments-LATEST-DRAFT.pdf` |
| 260.7 KiB | `/wp-content/uploads/2013/01/reconciliation-and-the-lack-thereof.pdf` |
| 148.8 KiB | `/wp-content/uploads/2013/02/deuteronomy-6-1-15.pdf` |
| 147.3 KiB | `/wp-content/uploads/2020/02/Pages-from-Delgado-Doody-and-Paffenroth-–-Augustine-and-Social-Justice.pdf` |
| 141.6 KiB | `/wp-content/uploads/2016/12/ASCENSION-SERMON-MANUSCRIPT-2017-05-28.docx` |
| 136.3 KiB | `/wp-content/uploads/2016/12/ASCENSION-SERMON-MANUSCRIPT-PDF-2017-05-28.pdf` |

## All Orphan Candidates

- `/wp-content/uploads/2015/12/12-28-14JoshSteeleHolyInnocents.mp3` (44.9 MiB)
- `/wp-content/uploads/2015/12/11-15-15JSHebrews10.mp3` (26.3 MiB)
- `/wp-content/uploads/2015/12/12-27-15JSTheChallengeofChristmasLight.mp3` (23.4 MiB)
- `/wp-content/uploads/2015/12/03-29-15_JS_TheCrossShapedGod.mp3` (22.6 MiB)
- `/wp-content/uploads/2015/12/03-16-14JoshSteele.mp3` (21.2 MiB)
- `/wp-content/uploads/2015/12/07-05-15JS-Jesusisnotjustoneofus.mp3` (18.7 MiB)
- `/wp-content/uploads/2015/12/Joshua-Steele-Psalm-32-Sermon-Exegesis-of-Psalms-Dr.-Ross.m4a` (15.1 MiB)
- `/wp-content/uploads/2015/12/Crisis-Sermon-Psalm-13.m4a` (11.2 MiB)
- `/wp-content/uploads/2015/12/09-18-16JSTheShrewdManager.mp3` (8.8 MiB)
- `/wp-content/uploads/2015/12/Psalm-32.m4a` (7.0 MiB)
- `/wp-content/uploads/2024/05/Corinthians-Chapters_Discovering-Biblical-Equality-Third-Edition.pdf` (4.1 MiB)
- `/wp-content/uploads/2015/12/Wedding-Sermon-Audio.m4a` (4.1 MiB)
- `/wp-content/uploads/2016/12/STEELE-Ecclesiology-and-Worship-Final-Project.pdf` (1.1 MiB)
- `/wp-content/uploads/2013/02/a-contextual-reading-of-romans-13-1-7.pdf` (679.5 KiB)
- `/wp-content/uploads/2016/12/HANDOUT-Class-Presentation-OUR-TRANSFORMATION-AND-WORSHIP-IN-GLORY.pdf` (626.4 KiB)
- `/wp-content/uploads/2011/03/sola-diversity.pdf` (612.5 KiB)
- `/wp-content/uploads/2017/02/STEELE-Anglican-History-and-Doctrine-Midterm-Middle-Way-is-Still-a-Way.pdf` (560.1 KiB)
- `/wp-content/uploads/2013/12/philemon.pdf` (439.8 KiB)
- `/wp-content/uploads/2016/12/Disunity_as_Ecclesiological_Impossibilit-2.pdf` (429.1 KiB)
- `/wp-content/uploads/2016/12/STEELE-Anglican-History-and-Doctrine-Final-Faithful-Anglican-Developments-LATEST-DRAFT.pdf` (419.5 KiB)
- `/wp-content/uploads/2013/01/reconciliation-and-the-lack-thereof.pdf` (260.7 KiB)
- `/wp-content/uploads/2013/02/deuteronomy-6-1-15.pdf` (148.8 KiB)
- `/wp-content/uploads/2020/02/Pages-from-Delgado-Doody-and-Paffenroth-–-Augustine-and-Social-Justice.pdf` (147.3 KiB)
- `/wp-content/uploads/2016/12/ASCENSION-SERMON-MANUSCRIPT-2017-05-28.docx` (141.6 KiB)
- `/wp-content/uploads/2016/12/ASCENSION-SERMON-MANUSCRIPT-PDF-2017-05-28.pdf` (136.3 KiB)
- `/wp-content/uploads/2018/01/HOSEA-11-Worksheet.docx` (129.1 KiB)
- `/wp-content/uploads/2016/12/ASCENSION-SERMON-2017-05-28.docx` (129.0 KiB)
- `/wp-content/uploads/2018/01/Bible-Study-Worksheet.docx` (109.3 KiB)
- `/wp-content/uploads/2013/11/steele-dogmatic-essay-on-trinity.pdf` (89.2 KiB)
- `/wp-content/uploads/2018/01/Bible-Study-Worksheet.pdf` (68.8 KiB)
- `/wp-content/uploads/2018/01/HOSEA-11-Worksheet.pdf` (46.4 KiB)
- `/wp-content/uploads/2018/10/The-Life-of-Jesus-HANDOUT.docx` (30.5 KiB)

## Cleanup Recommendation

Do not run `scripts/cleanup_images.sh` as-is. It removes the entire `static/wp-content/` directory, but this audit found live references there. Review the orphan candidates above first, then delete only confirmed-unused files in a separate, explicit cleanup pass.

Machine-readable details are in `scripts/data/audit-static-wp-content.json`.
