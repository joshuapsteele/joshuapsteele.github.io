---
author: joshuapsteele
categories: productivity
date: 2025-05-05
description: Are you using OpenFGA or a Zanzibar-inspired authorization system in
  production? I'd love to hear how you're managing models and authorization data at
  scale.
draft: false
tags:
- openfga
- zanzibar
- authorization
- rebac
- security
title: Real-World Authorization Lessons with OpenFGA? I’d Love to Hear Them
url: /real-world-openfga-authorization-lessons/
---

Are you using [OpenFGA](https://openfga.dev/) or another Google Zanzibar-inspired authorization engine **in the wild**—not just for a side project or proof of concept, but in a production environment with real users and systems?

If so, I’d love to learn from your experience.

## My Interest

I’m currently working on a centralized authorization system prototype based on OpenFGA. The design is aiming to support fine-grained, relationship-based access control (ReBAC) for multiple business units—each with its own data domain, developer team, and authorization needs.

The documentation and examples for OpenFGA are helpful, but they tend to focus on **small-scale setups**. What’s much harder to find are **real-world case studies** or lessons learned from organizations that are actually using it (or something similar like Topaz, SpiceDB, or AuthZed) in production at scale.

## My Questions for You

If you’ve deployed OpenFGA—or any Google Zanzibar-style system—in production, would you be willing to share your answers to some of the following questions?

### 1. **How are you managing authorization models?**
- How do application teams define and evolve their FGA models?
- Do you use a UI, CLI, or CI/CD pipeline to update model definitions?
- Have you hit any pain points around model versioning, migrations, or validation?

### 2. **How do clients get data into your FGA store?**
- Do application teams push tuples directly via API?
- Is there a dedicated “tuple management service” (e.g. fed via CDC pipelines or batch jobs)?
- What safeguards do you have to avoid flooding the system with unnecessary or stale relationships?

### 3. **What does your production environment look like?**
- How do you handle tenancy? One store per tenant? One store for all?
- How do you monitor and alert on query latency, error rates, or integrity issues?
- Have you hit any performance bottlenecks under load?

## Why I’m Asking

I think Zanzibar-style systems have a ton of potential—especially for complex, multi-tenant, or federated environments—but they also come with their own complexity tax. Getting the **model layer** and the **data ingestion layer** right seems critical for long-term success, and I’d rather learn from those who’ve been there.

If you’ve got hard-won wisdom, pain points, patterns, or even horror stories—**I’m all ears**.

Feel free to drop a comment below, or [contact me](/contact/).

Thanks in advance!

– Josh