#!/usr/bin/env python3
"""
Update blog post descriptions with manually crafted versions.
"""

import yaml
from pathlib import Path
from typing import Dict

# Manually crafted descriptions
DESCRIPTIONS = {
    "14-characteristics-of-fascism.md": "Exploring Umberto Eco's 14 characteristics of Ur-Fascism, from the cult of tradition to the impoverishment of language that limits critical thought.",

    "14-youtube-channels.md": "A curated collection of DIY, automotive, engineering, and educational YouTube channels for makers, tinkerers, and curious minds.",

    "198-ways-to-fight-tyranny.md": "Gene Sharp's comprehensive guide to nonviolent resistance, from symbolic protests and economic boycotts to political noncooperation and intervention.",

    "20-ways-to-fight-tyranny.md": "Timothy Snyder's 20 essential lessons from the twentieth century on resisting authoritarianism and defending freedom in dark times.",

    "10-things-i-love-about-my-kids.md": "A dad's heartwarming list of what makes his three kids special, from baptizing them as babies to their love of books and Bible stories.",

    "12-prayers-for-tough-days.md": "Twelve occasional prayers from the 2019 Book of Common Prayer for times of trouble, bereavement, anxiety, and spiritual struggle.",

    "25-possibly-unpopular-opinions-about-church.md": "Candid thoughts on American church culture, from worship styles and political engagement to leadership practices and theological priorities.",

    "3-confessions-expectant-father.md": "An honest reflection on fears, uncertainties, and hopes as a first-time father awaits the arrival of 'Lump' in August.",

    "5-books-every-christian-read.md": "Essential reading recommendations covering the Bible, theology, church history, ethics, and Christian living for busy believers.",

    "6-things-im-excited-about-2024-08-04.md": "Sweater weather, weight loss with Zepbound, football season, new tools, theological reading, and learning auto repair on a 1999 Dodge Ram.",

    "8-questions-to-ask-while-reading-theology.md": "Beth Felker Jones' practical framework for evaluating theological texts, from identifying key teachings to assessing practical implications.",

    "80-20-approach-christian-life-2-reasons-christians-care-pareto-principle.md": "Applying the Pareto Principle to Christian discipleship: how focusing on the vital few can transform your spiritual productivity.",

    "a-christmas-homily.md": "A Christmas homily reflecting on disappointment, shattered expectations, and finding hope when God doesn't meet our timing or plans.",

    "a-collect-for-juneteenth.md": "A collect prayer for Juneteenth 2020, remembering slavery's abolition while lamenting ongoing racism and praying for repentance and healing.",

    "a-crucicentric-credo.md": "A seminary student's theological outline centering on Christ's cross as the heart of Christian faith, from creation to consummation.",

    "a-deacons-last-day.md": "Reflections on the eve of priestly ordination, transitioning from deacon to priest in service of Christ's Church.",

    "a-farewell-to-cedarville.md": "Conversations with professors, administrators, and trustees who left or were removed as Cedarville University shifted from future vision to past agenda.",

    "a-list-of-karl-barths-sermons.md": "A comprehensive index of Karl Barth's sermons from 1913-1968, compiled from the Digital Karl Barth Library's sermon volumes.",

    "a-prayer-for-relatives-and-friends.md": "A Book of Common Prayer petition for God's grace, protection, and blessing upon relatives and friends in daily life.",

    "a-prayer-for-trustfulness-in-times-of-worry-and-anxiety.md": "A BCP prayer for trust amid anxiety, asking God to lift burdens and grant peace to troubled hearts.",

    # Batch 1 - Generic descriptions replaced
    "a-shameless-request-help-me-buy-more-books.md": "Fundraising to upgrade my Logos Bible Software library after losing access to physical books sequestered at Wheaton during COVID-19.",

    "against-christian-misanthropy.md": "Exploring Christian humanism with David Gushee: why following Jesus means affirming human flourishing, not embracing misanthropy.",

    "alabama-update.md": "Settling into Birmingham, Alabama in our first month before starting seminary at Beeson Divinity School—humidity and all.",

    "alan-jacobss-the-thinking-persons-checklist.md": "Alan Jacobs' practical checklist for critical thinking, charitable discourse, and resisting tribal reflexes in polarized times.",

    "are-the-beatitudes-renunciations-verzichte.md": "Examining Bonhoeffer's interpretation in Discipleship: Are the Beatitudes fundamentally about renunciation (Verzicht) and want?",

    "balderdash-12-suggestions-for-overcoming-writers-block-from-andrew-t-le-peaus-write-better.md": "Andrew T. Le Peau's 12 practical strategies for overcoming writer's block when dissertation progress stalls.",

    "barth-and-bonhoeffer-on-religions-false-gods.md": "How Barth and Bonhoeffer critique religion's false image of God that permits unrighteousness rather than redeeming creation.",

    "barth-bonhoeffer-the-theological-critique-of-religion-my-reading-list-this-fall.md": "My directed study reading list exploring Karl Barth and Dietrich Bonhoeffer's theological critique of religion at Beeson.",

    "barth-timeline-a-chronology-of-karl-barths-life.md": "A comprehensive chronology of Karl Barth's life, compiled from various sources in the Digital Karl Barth Library.",

    "bonhoeffer-on-stupidity.md": "Dietrich Bonhoeffer's penetrating prison reflections on stupidity as a moral defect more dangerous to society than malice.",

    # Batch 2 - Generic descriptions replaced
    "bonhoeffers-definition-of-religion-in-prison-15-facets-aspects.md": "A 15-point summary of Bonhoeffer's prison theology of 'religion' from Letters and Papers from Prison, covering inwardness, metaphysics, and more.",

    "cedarville-2.md": "Why I can't be proud of Cedarville University anymore, and why prospective students should consider other Christian colleges.",

    "cedarville-let-there-be-light-pt-1.md": "Examining Cedarville's firing of Dr. Michael Pahl over doctrinal statement disagreements and what it reveals about institutional integrity.",

    "christian-daily-office-5-things-can-learn-morning-evening-prayer.md": "Five ways the ancient practice of Morning and Evening Prayer can shape your spiritual growth and help you follow Jesus daily.",

    "christianity-and-politics-my-2024-reading-list.md": "My reading list exploring Church-State relations and Christian political engagement, from high school curiosity to 2024 concerns.",

    "christians-and-wealth.md": "Why American Christians should embrace downward mobility, living simply at human flourishing standards and giving excess to the poor.",

    "church_and_state.md": "Reflections on Kevin DeYoung's Memorial Day theology and the complex relationship between Christian faith and national identity.",

    "concerning-romans.md": "Setting aside Cedarville chaos to focus on reading Romans with Karl Barth's commentary during my Greek exegesis independent study.",

    "creation-and-doxology-pt-1.md": "Recovering biblical creation theology from the Young Earth vs. Neo-Darwinism debate to rediscover God's beautiful, worshipful design.",

    "creation-and-doxology-pt-2.md": "Exploring the overlooked role of complexity and chaos in God's good creation before sin's entrance in Genesis 3.",

    # Batch 3 - Generic descriptions replaced
    "creation-and-doxology-pt-3.md": "How New Testament theology links creation with redemption through Christ, the Creator-Redeemer who brings new creation.",

    "cut-positivity-crap-frustrates.md": "Tell me what frustrates you—I'm looking for real problems to solve, not toxic positivity. Rant in the comments.",

    "death-in-his-grave.md": "Holy Week reflections on resurrection icons (anastasis) and the profound lyrics of John Mark McMillan's 'Death in His Grave.'",

    "deuteronomy-61-15-1.md": "A close reading and interpretation of Deuteronomy 6:1-15, exploring the Shema and Israel's call to fear and love the Lord.",

    "dinner-prayer-highlights.md": "Our 4-year-old's spontaneous dinner prayers evolved from routine to creative, including 'help us to be nice to people.'",

    "do-more-better-tim-challies-excellent-little-book-on-personal-productivity-could-change-your-life.md": "Tim Challies' 120-page productivity guide delivers on its bold promise: a practical, explicitly Christian framework to improve your life.",

    "dont-stir-the-pot.md": "On the predictable 'don't stir the pot' reaction whenever Anglican Compass publishes anything favoring women's ordination.",

    "for-the-good-of-the-order-a-plea-for-charity-on-the-ordination-of-women.md": "A deacon's rare confession: I've felt called to priesthood but cannot pursue it. A plea for charity in women's ordination debates.",

    "getting-ahead-in-gods-upside-down-kingdom.md": "A sermon on God's upside-down kingdom values, appealing for a consistently pro-life ethic rooted in justice and steadfast love.",

    "hate-running-try-rucking-instead.md": "Fell out of love with running? Try rucking—walking with a weighted backpack—for strength, cardio, and meditative exercise.",

    # Batch 4 - Generic descriptions replaced
    "help-im-looking-for-examples-of-theological-triage-doctrinal-taxonomy-or-dogmatic-rank.md": "Research request: looking for examples of theological triage—distinguishing levels of doctrinal importance in Christian theology.",

    "help-me-come-up-with-rules-for-conversation.md": "Crowdsourcing rules for constructive conversation in polarized times—what guidelines help us talk across differences?",

    "hermeneutical-implications-scriptures-theological-location.md": "Should the Bible be read differently than other texts? Exploring theological hermeneutics and Scripture's unique location in Christian theology.",

    "i-think-karl-barth-missed-the-pastoral-point-of-romans.md": "Preparing a paper on Barth's Romans 9:30–10:21 for Princeton, and realizing he may have missed Paul's pastoral concern.",

    "i-wish-these-2-barth-and-bonhoeffer-books-would-come-out-sooner.md": "Two eagerly anticipated 2019 releases from Baker: Barth's theological exegesis and his relationship with Bonhoeffer.",

    "im-resigning-from-ordained-ministry-in-the-anglican-church-in-north-america.md": "After much discernment and growing disaffection with ACNA, I'm stepping away from ordained ministry to focus on family and software engineering.",

    "inductive-bible-study-7-steps-amy-chase-ashley.md": "Amy Chase Ashley's guest post on mastering inductive Bible study in seven steps: Scripture, Handle With Care.",

    "interpretive-approaches-to-the-beatitudes.md": "How Barth and Bonhoeffer read the Beatitudes—exploring interpretive approaches to the opening of the Sermon on the Mount.",

    "its-time-for-another-social-media-fast.md": "Cal Newport's Deep Work convinced me: time for a 30-day fast from Twitter, Facebook, and Instagram to reclaim focus.",

    "karl-barths-reversal-on-the-knowledge-of-good-and-evil.md": "How Barth's interpretation of Genesis 2–3 changed from Romans to Church Dogmatics while maintaining his critique of religion as idolatry.",

    # Batch 5 - Generic descriptions replaced
    "let-there-be-light-my-resignation.md": "Resigning from the Let There Be Light platform to protest Cedarville University's troubling institutional changes and leadership decisions.",

    "master-the-art-of-interpersonal-relationships-with-how-to-win-friends-and-influence-people.md": "Dale Carnegie's timeless principles for mastering interpersonal relationships have helped millions excel in personal and professional life.",

    "most-useful-websites-my-favorite-online-resources.md": "My curated collection of favorite online resources: thinking tools, fitness guides, reading aids, design resources, and developer references.",

    "my-coding-bootcamp-journey-how-a-pastor-became-a-programmer.md": "From Bible major to bi-vocational ministry to software engineer—how I made the career transition through coding bootcamp.",

    "my-favorite-podcasts.md": "A guide to podcasts worth listening to during this golden age of the medium, from a seasoned podcast enthusiast.",

    "my-regional-ets-presentation-reconciliation-and-the-lack-thereof.md": "Presenting on reconciliation at the 2014 Evangelical Theological Society Southeastern Regional Meeting at Beeson Divinity School.",

    "my-unforgettable-cedarville-experience.md": "How I went from 'I will never attend Cedarville' to giving a speech at the CU Scholar Dessert Reception.",

    "no-one-knows-what-positivism-of-revelation-means.md": "Unpacking the greatest conundrum in the Barth-Bonhoeffer relationship: Bonhoeffer's critique of Barth's 'positivism of revelation.'",

    "on-scripture.md": "A theological statement: Scripture as the Spirit's illocutionary act testifying to the Son, accomplishing redemption in God's people.",

    "only-the-suffering-god-can-help.md": "Bonhoeffer's profound prison reflection: only the suffering God can help—a radical theological claim about God's nature and presence.",

    # Batch 6 - Generic descriptions replaced
    "open-apology.md": "A public apology to anyone I may have offended during my student activism efforts at Cedarville University.",

    "peru-2014.md": "Announcing our summer 2014 cross-cultural ministry practicum in Lima, Peru with the Stone and DeBoer families.",

    "political-thoughts.md": "Brief reflections on Christianity, politics, and faithful citizenship in complex times.",

    "prayers-for-the-sick.md": "Traditional prayers for the sick from the 1979 Book of Common Prayer, interceding for comfort and healing.",

    "preparing-the-way-of-the-lord-in-the-wilderness-luke-31-6.md": "An Advent sermon on Luke 3:1-6: heeding the prophets' call to repentance and preparing the way of the Lord.",

    "presenting-on-barth-at-2015-southeastern-ets.md": "My paper on Karl Barth and church unity has been accepted for the 2015 Southeastern Regional ETS meeting.",

    "quit-claiming-that-we-mutualists-egalitarians-dont-take-the-bible-or-tradition-seriously.md": "Challenging the false claim that mutualists ignore Scripture and tradition in women's ordination debates.",

    "requiescas-in-pace-mi-avia.md": "Rest in peace, grandmother: remembering her departure with the BCP's prayer for Christian souls leaving this world.",

    "scriptures-to-read-on-days-of-prayer-and-fasting-for-the-church.md": "Biblical passages from 1 Peter, Isaiah, and elsewhere for corporate prayer and fasting during times of church crisis.",

    "silence-and-violence.md": "Violence isn't human destiny because the God of peace frames our history—reflections on peacemaking and the crucified Messiah.",

    # Batch 7 - Generic descriptions replaced
    "software-testing-possibilities-problems-and-principles.md": "An overview of software testing principles and practices, drawing on Khorikov's Unit Testing and Aniche's Effective Software Testing.",

    "spirit-flesh-restoration-and-sublimation.md": "Bonhoeffer's prison reflections on spirit and flesh, restoration and sublimation, explored through meaningful hymn lyrics.",

    "stay-woke-ephesians-5.md": "Ephesians 5:11-14 speaks urgently against fascism and far-right Christianity: stay awake, expose darkness, live as children of light.",

    "systematic-theologies-a-list-help-me-update.md": "A curated list of systematic theology works, compiled from Glynn's Commentary and Reference Survey—help me keep it updated!",

    "take-up-your-tongue-and-follow-jesus.md": "A sermon on Mark 8:27-38 and James 3:1-12: discipleship means controlling our tongues as we carry our crosses.",

    "tech-hype-and-the-growing-chasm.md": "Meredith Whittaker on the growing gap between tech-optimist narratives and our actual tech-encumbered reality.",

    "thank-god-i-went-to-cedarville.md": "Despite everything else, Cedarville prepared me exceptionally well for seminary—gratitude for my undergraduate theological education.",

    "the-brokenhearted-god.md": "We lose sight of God's love when we emphasize 'strong' portraits of God while neglecting Scripture's 'weak,' brokenhearted images.",

    "the-epistle-to-philemon.md": "Paul's shortest letter analyzes reconciliation and slavery: bringing gospel truth to bear on an estranged Christian relationship.",

    "the-feast-of-st-james-the-apostle-a-homily-for-ministers.md": "St. James' martyrdom rebukes ministerial ambitions—a sobering homily for those who aspire to serve Christ's Church.",

    # Batch 8 - Generic descriptions replaced
    "the-four-tendencies-4-ways-you-can-play-to-your-personality-strengths.md": "Gretchen Rubin's Four Tendencies framework helps you understand your personality and play to your strengths in relationships and productivity.",

    "the-good-news-of-christmas.md": "After reading Scot McKnight's King Jesus Gospel, I discovered profound gospel messages hidden in the Christmas carols we often sing.",

    "the-guilt-of-karl-barth-strengths-and-weaknesses-of-barths-romerbrief-reading-of-romans-9301021.md": "My 2019 Barth Colloquium paper at Princeton: analyzing strengths and weaknesses of Barth's Römerbrief reading of Romans 9:30–10:21.",

    "the-hope-of-the-holy-innocents.md": "A December 28 sermon on the Slaughter of the Innocents: finding hope and meaning in Herod's horrific massacre of Bethlehem's babies.",

    "the-perfect-translation.md": "Reviewing Waltke's Dance Between God and Humanity and Goodwin's Translating the English Bible for Liverpool Hope's journal.",

    "the-phd-plan-or-the-lack-thereof.md": "Months of prayer for breakthrough or clarity to quit—my struggle to make progress on the Barth, Bonhoeffer, and Bible dissertation.",

    "the-tree-of-religion-karl-barth-and-dietrich-bonhoeffer-on-the-tree-of-knowledge-in-genesis-24-324.md": "How Barth and Bonhoeffer interpret the tree of knowledge in Genesis 2–3 as a critique of religion as idolatry.",

    "theology-against-nationalism.md": "Michael Gorman's 10 theological theses confronting American evangelicalism's dangerous conflation of gospel and nation.",

    "theology-is-exegesis-john-webster-on-what-we-can-learn-from-barth-and-bonhoeffer.md": "John Webster's essay on Barth and Bonhoeffer's biblical reading—the inspiration for my doctoral dissertation.",

    "to-be-or-not-to-be-religious-a-clarification-of-karl-barths-and-dietrich-bonhoeffers-divergence-and-convergence-regarding-religion.md": "Clarifying how Barth and Bonhoeffer both inherited and transformed post-Kantian understandings of religion in Christian theology.",

    # Batch 9 - Generic descriptions replaced
    "top-3-books-movies-and-podcasts-about-race-for-white-christians-like-me.md": "Accessible starting points for white Christians learning about racism and anti-racism—top 3 books, movies, and podcasts.",

    "two-of-bonhoeffers-most-convicting-paragraphs.md": "Bonhoeffer's Discipleship asks: How would we respond if Jesus showed up today and made the same concrete commands?",

    "unrighteous-anger-yoda-jonah-nahum-and-us.md": "A sermon exploring righteous versus unrighteous anger through Yoda's wisdom, Jonah's fury, Nahum's prophecy, and our own responses.",

    "volf-on-divine-violence.md": "Miroslav Volf on divine judgment in Exclusion and Embrace: God judges because some refuse to live in God's peace.",

    "want-a-taste-of-what-my-dissertation-is-about-read-these-two-passages-dissertation-dispatch-2020-04-03.md": "Two key passages reveal what Barth and Bonhoeffer meant by 'religion'—the heart of my dissertation challenge.",

    "we-switched-anglican-compass-over-from-hostgator-shared-to-bluehost-vps-hosting.md": "Successfully migrated Anglican Compass from HostGator shared hosting to Bluehost VPS—hoping this improves site performance.",

    "what-are-you-afraid-of.md": "I'm scared of wasting my life, of being worthless outside academia. Fear drives how we dress, parent, and vote.",

    "what-attracts-people-to-anglicanism-heres-my-take.md": "My Telos Collective post on what draws people to Anglican Christianity, based on Rookie Anglican conversations and insights.",

    "what-blogs-are-you-reading.md": "My current RSS reading list: Alan Jacobs, Farnam Street, Seth Godin, Cal Newport, James Clear, and more.",

    "what-did-barth-and-bonhoeffer-think-of-the-bible-dissertation-dispatch-2020-03-30.md": "Adding biblical content to the Barth-Bonhoeffer debate: what did they actually think about Scripture and its role?",

    # Batch 10 - Generic descriptions replaced (FINAL BATCH)
    "what-does-it-mean-to-be-human.md": "The act of asking 'what does it mean to be human?' reveals our self-transcendence—a dialectic between subject and object.",

    "what-is-fascism.md": "Defining fascism beyond the political buzzword: understanding its historical origins, characteristics, and why it matters today.",

    "what-to-make-of-jordan-peterson-some-takes-then-my-own.md": "Surveying various perspectives on Jordan Peterson's cultural phenomenon before offering my own theological and ethical assessment.",

    "whats-gone-wrong-with-the-digital-karl-barth-library.md": "Dissertation frustrations: longing for a complete, translated Barth Gesamtausgabe and a fully functional Digital Karl Barth Library.",

    "who-really-cares-about-the-trinity-in-2020.md": "A Trinity Sunday sermon connecting Father, Son, and Holy Spirit to racial justice: why Trinitarian theology matters in 2020.",

    "why-havent-you-torn-the-sky-open-yet-sermon-first-sunday-of-advent-2020.md": "An Advent sermon for those who hate waiting: Why haven't you torn the sky open yet, God? Wrestling with Isaiah's cry.",
}


def update_file_description(filepath: Path, new_description: str) -> bool:
    """Update the description in a markdown file's front matter."""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()

        # Split front matter and body
        if not content.startswith('---'):
            return False

        parts = content.split('---', 2)
        if len(parts) < 3:
            return False

        yaml_content = parts[1]
        body = parts[2]

        # Parse YAML
        data = yaml.safe_load(yaml_content)
        if data is None:
            data = {}

        # Update description
        data['description'] = new_description

        # Re-order fields
        field_order = ['title', 'date', 'author', 'categories', 'tags', 'description', 'url', 'draft']
        ordered = {}

        for field in field_order:
            if field in data:
                ordered[field] = data[field]

        # Add remaining fields
        for key, value in data.items():
            if key not in ordered:
                ordered[key] = value

        # Convert to YAML
        new_yaml = yaml.dump(ordered, default_flow_style=False, allow_unicode=True, sort_keys=False, width=1000)

        # Write back
        new_content = f"---\n{new_yaml}---{body}"

        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)

        return True

    except Exception as e:
        print(f"Error updating {filepath}: {e}")
        return False


def main():
    content_dir = Path('content/blog')
    updated_count = 0

    for filename, description in DESCRIPTIONS.items():
        filepath = content_dir / filename

        if not filepath.exists():
            print(f"⚠️  Not found: {filename}")
            continue

        if update_file_description(filepath, description):
            print(f"✅ Updated: {filename}")
            updated_count += 1
        else:
            print(f"❌ Failed: {filename}")

    print(f"\n✅ Updated {updated_count}/{len(DESCRIPTIONS)} descriptions")


if __name__ == '__main__':
    main()
