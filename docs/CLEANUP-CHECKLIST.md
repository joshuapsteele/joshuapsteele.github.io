# Content Cleanup Checklist
## joshuapsteele.com Hugo Site

**Based on:** Content Audit completed October 11, 2025
**Site Health Score:** 77/100 → Target: 95/100

---

## Week 1: Critical Fixes (6-7 hours) 🔴

### Day 1-2: Broken Links (3-4 hours)
- [ ] Fix broken links in `pages/essays.md` (14 links)
- [ ] Fix broken links in `pages/sermons.md` (14 links)
- [ ] Fix broken links in top 5 blog posts:
  - [ ] `maundy-thursday-sermon-the-lasting-supper-luke-2214-30.md` (11 links)
  - [ ] `finding-a-hat-for-my-big-bald-head.md` (9 links)
  - [ ] `hate-running-try-rucking-instead.md` (9 links)
  - [ ] `let-there-be-light-my-resignation.md` (7 links)
  - [ ] `what-im-reading.md` (7 links)
- [ ] Test all fixes locally with Hugo server
- [ ] Deploy changes

### Day 3-4: Categories (2-3 hours)
- [ ] Categorize high-priority posts:
  - [ ] Immigration/Romans 13 posts → "ethics"
  - [ ] Barth/Bonhoeffer posts → "theology"
  - [ ] ACNA/women's ordination → "ministry"
  - [ ] Career/coding posts → "productivity"
  - [ ] Personal reflections → "personal"
- [ ] Verify all top 20 traffic posts have categories
- [ ] Re-run audit to confirm progress

### Day 5: Verification (1 hour)
- [ ] Run `npm run build` and check for errors
- [ ] Review site navigation locally
- [ ] Verify category pages display properly
- [ ] Check analytics for 404 errors
- [ ] Commit and deploy

**Week 1 Target:**
- Broken links in top 20 files: 0
- Posts without categories: <10
- Site health score: 82/100

---

## Weeks 2-3: Foundation Work (8-10 hours) 🟡

### Categories Consolidation (3-4 hours)
- [ ] Create `taxonomy_map.yaml` with mapping rules
- [ ] Test category consolidation script
- [ ] Consolidate categories:
  - [ ] bible + religion + discipleship → theology
  - [ ] politics + justice + law → ethics
  - [ ] anglicanism + some sermons → ministry
  - [ ] Tools + tools + technology + software engineering → productivity
- [ ] Update Hugo config if needed
- [ ] Verify all category pages work

### Tags Addition (3-4 hours)
- [ ] Add tags to top 50 posts by traffic:
  - [ ] Immigration posts: add "immigration", "christian ethics", "romans 13"
  - [ ] Barth posts: add "barth", "theology", "church dogmatics"
  - [ ] Bonhoeffer posts: add "bonhoeffer", "theology", "ethics"
  - [ ] Career posts: add "career", "software", "ministry"
- [ ] Standardize existing tags (capitalization, duplicates)
- [ ] Create tag guidelines document

### Remaining Broken Links (2 hours)
- [ ] Fix remaining files with 1-3 broken links
- [ ] Set up automated link checking (optional)
- [ ] Document common link patterns to avoid

**Weeks 2-3 Target:**
- Categories: 6 core categories
- Top 50 posts tagged
- All broken links fixed
- Site health score: 88/100

---

## Month 2: Enhancement (10-15 hours) 🟢

### Hub Pages Creation (5-6 hours)
- [ ] Create Romans 13 hub page (`content/pages/romans-13-hub.md`)
  - [ ] Comprehensive guide
  - [ ] Link to all related posts
  - [ ] Add study questions
  - [ ] Include theologian quotes
- [ ] Create Immigration Ethics hub (`content/pages/christian-immigration-ethics.md`)
  - [ ] Link to top posts
  - [ ] Biblical framework
  - [ ] Resources section
- [ ] Create Barth/Bonhoeffer resources hub
  - [ ] Reading guides
  - [ ] Link to dissertation content
  - [ ] Beginner-friendly intros

### Internal Linking (3-4 hours)
- [ ] Add 3-5 internal links to top 20 posts
- [ ] Link theology posts to each other
- [ ] Link political theology posts together
- [ ] Create "related posts" sections

### SEO Enhancement (2-3 hours)
- [ ] Add FAQ sections to top 10 posts:
  - [ ] Immigration post
  - [ ] Romans 13 post
  - [ ] Flower Petal Exercise post
  - [ ] Fascism post
  - [ ] Top theology posts
- [ ] Add schema markup for FAQs
- [ ] Optimize for "People Also Ask" keywords

### Automation Setup (1-2 hours)
- [ ] Create pre-commit hook for link checking (optional)
- [ ] Set up GitHub Actions for link validation (optional)
- [ ] Create new post template with required fields

**Month 2 Target:**
- Hub pages: 3 created
- Internal links per post: 3-5 average
- FAQs on top 10 posts
- Site health score: 95/100

---

## Ongoing Maintenance

### Weekly (15 minutes)
- [ ] Check new posts have categories
- [ ] Verify new posts have 3-5 tags
- [ ] Review for broken links

### Monthly (1 hour)
- [ ] Run link checker script
- [ ] Review analytics for 404s
- [ ] Update hub pages with new content
- [ ] Check tag consistency

### Quarterly (2-3 hours)
- [ ] Full taxonomy review
- [ ] Update FAQs based on search queries
- [ ] Review internal linking strategy
- [ ] Update hub pages

### Annually (1 day)
- [ ] Complete content audit
- [ ] Review category effectiveness
- [ ] Evaluate site structure
- [ ] Plan next year's content strategy

---

## Quick Commands

```bash
# Check for uncategorized posts
python3 audit-frontmatter.py

# Run link checker
python3 check-internal-links.py

# Build and check for errors
npm run build

# Test locally
npm run dev

# Deploy changes
git add . && git commit -m "Content cleanup: [describe changes]" && git push
```

---

## Success Metrics Tracking

| Metric | Before | Week 1 Target | Month 1 Target | Month 2 Target |
|--------|--------|---------------|----------------|----------------|
| Health Score | 77/100 | 82/100 | 90/100 | 95/100 |
| Posts without categories | 53 | <10 | 0 | 0 |
| Posts without tags | 197 | 197 | <100 | <50 |
| Broken link files | 118 | <20 | 0 | 0 |
| Number of categories | 24 | 24 | 6 | 6 |
| Hub pages | 0 | 0 | 1 | 3 |
| FAQs on top posts | 0 | 0 | 5 | 10 |

---

## Notes

- Always test changes locally before deploying
- Commit frequently with clear messages
- Back up before bulk operations
- Focus on high-traffic content first
- Use analytics to guide priorities

---

*Generated: October 11, 2025*
*See AUDIT-MASTER-REPORT.md for full details*
