---
date: '2025-03-07T09:16:56-05:00'
title: "Authorization, Continued: Experimenting with OpenFGA, Topaz, and Permify"
author: joshuapsteele
categories:
- Software Engineering
tags:
- authorization
url: /authorization-continued/
---

As I mentioned in my previous post, "Devs, Let's Talk Authorization!", I'm working on a new, exploratory work project related to authorization. Specifically, we're gathering authorization requirements from various orgs across our company and building 1-3 proofs-of-concept of a centralized, fine-grained approach to authorization. Right now, each org handles authorization in its own, usually coarse-grained and role-based way.

## Clarify Current Requirements

The first thing I did was gather and clarify my org's current authorization model/requirements. We're heavily role-and-permission-based when it comes to authorization, with a touch of attribute-based access control mixed-in (to make sure that, for example, a user can only view resources related to their company, and not other companies). So, RBAC (role-based access control) with a bit of ABAC (attribute-based access control).

## Which Authorization Paradigm(s) Make the Most Sense?

I then spent some time researching [commonly used access control paradigms](https://auth0.com/blog/an-overview-of-commonly-used-access-control-paradigms/), in order to determine which approach would, in broad brushstrokes, be the best fit for our company going forward. Like I said, we're currently RBAC with a touch of ABAC. But we're already experiencing some role-bloat, and a centralized approach to authorization for our company needs to be more flexible and fine-grained than pure RBAC allows for.

An attribute-and-policy-based approach, such as that offered by [Open Policy Agent (OPA)](https://www.openpolicyagent.org/), would be fine-grained enough for our current needs. And we're experimenting with [Topaz](https://www.topaz.sh/docs/intro), which builds upon OPA and its Rego policy language, for one of our prototypes.

However, because my org and others would like to be able to do more with organizational hierarchy when it comes to authorization, a relationship-based approach to access control (ReBAC), such as that offered by [OpenFGA](https://openfga.dev/), is appealing!

## Experimenting with ReBAC in OpenFGA

So, I've spent some time modeling my org's current authorization requirements using OpenFGA. As far as our current needs go, it was relatively easy to put together a fairly abstract authorization model in OpenFGA's configuration language.

However, it seems like a significant limitation to OpenFGA is that it does not evaluate indirect relationships recursively beyond one level of separation/indirection. 

According to OpenFGA’s documentation on ["Referencing Relations on Related Objects"](https://openfga.dev/docs/configuration-language#referencing-relations-on-related-objects):

> OpenFGA does not allow the referenced relation (the word after `from`, also called the tupleset) to reference another relation and does not allow non-concrete types (type bound public access (`<object_type>:*`) or usersets (`<object_type>#<relation>`)) in its type restrictions; adding them throws a validation error when calling `WriteAuthorizationModel`.

### Example: Management Chain Authorization

Consider a scenario where permissions should propagate up a management chain:

1. **Object A** is **owned** by **User B**.
2. **User B** is **managed** by **User C**.
3. **User C** is **managed** by **User D**.

### ✅ What OpenFGA *Can* Handle

OpenFGA allows referencing relationships **one level deep** via `X from Y`.  

For example, if an authorization model defines:

```fga
allow manager from owner
```

Then **User C** can inherit access to **Object A** because:

> "User C manages User B, who owns Object A."

### ❌ What OpenFGA _Cannot_ Handle

However, OpenFGA **does not** support evaluating this deeper chain:

> "User D should be able to view Object A, because User D manages User C, who manages User B, who owns Object A."

This is because OpenFGA **does not allow chaining references beyond one level**.

Another warning of this limitation is found in [OpenFGA’s documentation on modeling parent-child relationships](https://openfga.dev/docs/modeling/parent-child#05-check-if-bob-is-an-editor-of-documentmeeting_notesdoc):

> When searching tuples that are related to the object (the word after `from`, also called the tupleset), OpenFGA will not do any evaluation and only considers concrete objects (of the form `<object_type>:<object_id>`) that were directly assigned. OpenFGA will throw an error if it encounters any rewrites, a `*`, a type bound public access (`<object_type>:*`), or a userset (`<object_type>:<object_id>#<relation>`).

### UPDATE: OpenFGA Does Handle Recursive Relationships!

Shout-out to [Raghd Hamzeh](https://social.rhamzeh.com/@raghd), who's a part of the [OpenFGA](https://mastodon.social/@openfga) team, for helping me out with a solution to the management chain problem/example.

[Raghd writes](https://social.lol/@raghd@rhamzeh.com/114123110921262312):

> Hey @steele!  
> Good news! It does! :) Evaluating indirect relationships is one of @openfga 's strong suites!  
> Let me know what issue you're facing or need clarification on and I can see if I can help  
> You'll find several examples on this and other use-cases in the OpenFGA sample stores repo: https://github.com/openfga/sample-stores/tree/main/stores

Here's the workaround/solution: splitting a `manager` relation into a `manager` and a `can_manage` relation!

```fga
model
  schema 1.1

type user
  relations
    define manager: [user]
    define can_manage: manager or can_manage from manager

type resource
  relations
    define owner: [user]
    define can_view: owner or can_manage from owner
```

You can then assign a chain of management relationships via relational tuples:

```yaml
tuples:
  - user: user:B
    relation: owner
    object: resource:A
  - user: user:C
    relation: manager
    object: user:B
  - user: user:D
    relation: manager
    object: user:B
```

The following test will pass:

```yaml
tests:
  - name: Tests
    check:
      - user: user:D
        object: resource:A
        assertions:
          can_view: true
```

## What Now? Experimenting with Permify (and SpiceDB, maybe)

To be clear, it is possible to model multi-level management relationships, as well as intra-organization relationships across a large company, in OpenFGA. It just ends up taking more relational tuples to represent the relationships than I initially expected. (UPDATE: See above! It seems to either take more tuples than anticipated, OR splitting up the recursive relationship to allow for evaluation.)

So, I did some research on ReBAC and recursive relationships, and it sounds like other ReBAC solutions, like Permify and SpiceDB, can evaluate indirect relationships recursively. They avoid infinite loops and undue performance costs in various ways.

I'm currently trying to translate the OpenFGA authorization model I created into Permify's syntax. (Which, if anyone already has a tool or a script that does this, taking an `.fga` or an `.fga.yaml` file as input, please let me know!) I'll then put in some test data and run some checks to see if there are any noticeable differences between OpenFGA and Permify when it comes to performance, "pain-in-the-ass" of development, etc.

If time allows, I'll also do some experimenting with SpiceDB. We'll see!

---

Are you a software engineer who's worked with tools like OpenFGA, Permify, and/or SpiceDB? If so, I'd love to make your acquaintance and hear your thoughts about these tools, authorization in general, etc. 

Please send me an email at [blog@joshuapsteele.com](mailto:blog@joshuapsteele.com) or reach out to me on [BlueSky @joshuapsteele.bsky.social](https://bsky.app/profile/joshuapsteele.bsky.social). Cheers!
