---
author: joshuapsteele
categories: personal
date: '2026-05-24T15:00:00Z'
description: I've spent thousands on my Logos library and pay for its AI features. Claude is far better. The fix is an MCP server, and Logos's licensing objection is really a solvable authorization problem.
draft: false
title: Logos Bible Software Needs an MCP Server
tags:
  - ai
  - mcp
  - claude
  - logos
  - bible-study
  - software
url: /logos-bible-software-needs-an-mcp-server/
atUri: "at://did:plc:fz4b2acwzs7snxpro4gzv7hs/site.standard.document/3mpydbfk5lh2v"
---

I've spent thousands of dollars on my [Logos Bible Software](https://www.logos.com/) library over the years, and I pay for a subscription partly to use its built-in AI features. They're fine. They'll find a passage, summarize a resource, answer a simple question. But they don't come close to what Claude Opus does when I'm actually trying to think hard about a text, chasing an idea across a dozen commentaries or weighing how different authors handle the same passage.

What I keep wishing for is simple. I want to point Claude at my own Logos library and let it work.

The technology to do that already exists. It's called [MCP](https://modelcontextprotocol.io/), and I'm not the only one asking. There's [a thread in the Logos Community forums](https://community.logos.com/discussion/257087/mcp-server-for-logos-bible-software) asking for exactly this.

## What an MCP server is

MCP, short for the Model Context Protocol, is an open standard for connecting AI assistants to outside tools and data. A program exposes an "MCP server," and any compatible AI client can plug into it. The AI calls defined tools, like "search my library" or "open this commentary at this verse," and uses the results in its answer.

The important word is *uses*. When you ask a question, the model reads what the server hands it and writes a response. That text passes through the one conversation and is not kept.

## The objection from Logos

When the community raised this, a Logos engineer gave an honest answer. The licensed content, he wrote, "commentaries, lexicons, and original language resource\[s\]," "is not ours to expose to AI models through an MCP Server." Many of their publisher agreements "prohibit the use of their copyrighted material for training AI models," and:

> We could not honor our contractual obligations if we permitted use of the content with free or personal ChatGPT plans which often do train on all user input.

I want to take that seriously, because it's a fair concern. Logos doesn't own most of what's in my library; it licenses it. If Logos shipped a feature that quietly fed *The Anchor Yale Bible* into someone's training data, that would be a real breach of trust with its publishers.

But the objection is narrower than it first sounds. Nobody is claiming MCP is technically impossible. The concern is specifically that licensed text might end up in a model's training data, and that is a problem the industry solves routinely.

One point from the forum thread is hard to get around. Logos already pipes this same licensed content into its own AI Study Assistant. So the real question was never whether licensed material can be used with an AI model. Logos has already settled that with its publishers for its own feature. An MCP server scoped to a user's own license is the same arrangement through a different door.

## Why this is solvable

I work in software, specifically in identity and access management (IAM). Deciding who can see what, under which terms, is most of my job. From that angle the Logos objection reads less like a wall and more like a list of requirements, and they're requirements I watch other companies meet all the time.

Start with the difference between retrieval and training. Handing text to a model inside a single prompt so it can answer a question is not the same as adding that text to a training set. The first is closer to reading; the second is closer to copying. Most of the fear here comes from blurring those two, and they're worth keeping apart.

Then there's the question of where the content actually goes. A publisher agreement restricts redistribution and training, not a paying licensee reading what they bought. An MCP server can run locally, on your own machine, authenticated to you, serving your own licensed resources to your own session. The content never leaves your computer and no one else ever sees it. That's the same thing that happens every time you open a commentary in the Logos app.

The engineer's specific worry, that free ChatGPT plans train on user input, is real, but it describes a default setting rather than a problem with MCP. The commercial tiers, Anthropic's API and Claude for Work, OpenAI's API and ChatGPT Enterprise, never train on submitted data. And the ordinary twenty-dollar plans, Claude Pro and ChatGPT Plus, both let you turn training off: Anthropic lets you decline it in your privacy settings, and OpenAI has an "Improve the model for everyone" toggle you can switch off. So the requirement isn't an expensive enterprise account. It's a client configured not to train on the content, which a normal paying subscriber can set up in under a minute.

The honest catch is verification. An enterprise or API connection gives Logos a contractual no-training guarantee it can point to when a publisher asks. A consumer opt-out is just as real, but Logos can't see whether you've flipped the switch. There's a reasonable way to close that gap. Because a local server is really just the licensee reading what they paid for, Logos can put the obligation where it already sits, on the user, with a short attestation that you're connecting a no-train client. My license already forbids me from redistributing the text; it can just as easily ask me to confirm I'm not feeding it into a training run.

None of this would be new ground. Someone in the thread asked for examples of copyrighted content exposed through MCP with the rights holder's blessing, and there are many. GitHub's official MCP server lets AI assistants read your private source code without that code becoming training data. Atlassian, Stripe, Notion, and others ship servers that expose proprietary and customer data to the authenticated owner under contractual "your data stays yours" terms. Licensed and confidential content moving through MCP, to the right person, under the right terms, is already the normal pattern.

A responsible design almost writes itself. Scope every request to the user's own license, so I only ever get what I already paid to read. Require a no-training configuration, whether that's an enterprise contract or an ordinary plan with training switched off. Let users choose which resources to expose. Where licensed text is involved, prefer short quotations with citations over wholesale dumps, which is the posture Logos search already takes. This is ordinary access control.

## Someone has already built one

This isn't hypothetical. A community developer has already built one, on GitHub as [robrawks/LogosBibleSoftwareMCP](https://github.com/robrawks/LogosBibleSoftwareMCP). It's roughly twenty tools that let Claude read Bible text, search Scripture, browse your library catalog, read your own notes and highlights, check reading plans, and open resources in the Logos app.

What I find encouraging is how carefully it respects the licensing. For Bible text it calls Faithlife's own free [Biblia API](https://bibliaapi.com/), and only for translations that are public domain or Faithlife's own, such as the LEB and the KJV, so no third-party copyrighted Bible gets pulled out. For licensed commentaries and lexicons it doesn't extract the text at all. Instead it opens the resource in the Logos desktop app at the right passage, so you read the licensed content inside Logos, exactly as your license intends. For your own notes, highlights, and reading progress, it reads your local Logos files without changing them.

So the grassroots version already respects the boundary by design. It shows two things at once: people want this badly enough to build it themselves, and it can be done without ever feeding a publisher's text into a training run. An official version, built with Faithlife's cooperation, could go further and do it more safely.

## The criticisms of AI I take seriously

I don't want to pretend any of this is free of cost. Several of the common criticisms of AI are right, and they shape what I'm actually asking for.

The environmental footprint is real. Training and running these models consumes a lot of energy and water, and the burden often falls on the communities living next to the data centers. That's a genuine cost, not a rounding error, and anyone who uses these tools should sit with that honestly instead of waving it away.

The theological objection is the one I feel most. Some of the work in the Christian life is supposed to form the person doing it. Wrestling with a difficult passage, sitting with a commentary that disagrees with you, praying over a text, writing your own sermon in your own voice: the labor isn't a delay before the result, it's part of the result. A pastor who has a model write his sermon has skipped the very thing that was meant to shape both him and his congregation. If AI becomes a way to avoid study and prayer rather than to go deeper into them, it's doing harm, however convenient it feels.

There's also the plain fact that these models make things up. A model will hand you a confident reading of a verse that no serious scholar holds, or invent a citation that looks real. In casual use that's annoying. In teaching and preaching it's dangerous, and it calls for more care, not less.

So I want to be clear about what I'm asking Logos for and what I'm not. I'm not asking for a sermon machine, or a substitute for study and prayer. I'm asking for a research assistant that helps me find and connect what's already in the library I bought: pulling the relevant commentaries together, surfacing a cross-reference I'd have missed, reminding me what I wrote in my own notes three years ago. A tool that sends me back into the sources makes my study deeper. A tool that does the studying for me hollows it out. I only want the first kind.

## What I'm asking for

I'm not asking Logos to fling the doors open. I'm asking them to build, or at least formally bless, an MCP server with a few properties. It's scoped to each user's own licensed library. It connects only to clients configured not to train on the content, whether that's an enterprise account or a twenty-dollar plan with training switched off. It lets users opt in one resource at a time. And it starts conservative, with personal data, Bible text, and in-app navigation, before moving toward cited retrieval of licensed content as the agreements allow.

There's an easy first step that avoids the licensing question altogether, and someone in the thread already named it: start with the content I created. My notes, highlights, reading plans, and sermons carry no publisher agreement at all. Shipping access to just those would put something genuinely useful in users' hands while the harder licensing terms get worked out.

I'd gladly pay more for this, and I suspect a lot of longtime customers would too. The demand is clearly there, the publisher concern is legitimate, and the space between them is a design problem that other companies have solved many times over.

If anyone at Logos is reading this: I love your software, and I've spent years and a good deal of money building my library inside it. I'd just like to study it with the best tools available.
