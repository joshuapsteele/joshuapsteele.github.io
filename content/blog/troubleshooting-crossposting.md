---
date: '2024-11-19T17:25:36-05:00'
title: 'Troubleshooting Hugo to Micro.blog Crossposting'
author: joshuapsteele
tags:
  - hugo
url: /troubleshooting-hugo-to-microblog-crossposting/
---

*UPDATE: This now seems to work! The post made it to Micro.blog, BlueSky, and Mastodon, at least. Just not to Threads.*

I'm trying to troubleshoot what's going on with my current crossposting configuration between my Hugo website, my Micro.blog account, and my accounts on BlueSky, Mastodon, and Threads. 

What's supposed to happen is that this blog post, after I merge it to my [GitHub repository](https://github.com/joshuapsteele/joshuapsteele.github.io), will end up on the JSONfeed at `https://joshuapsteele.com/blog/feed.json`. 

That JSONFeed is supposed to get polled by Micro.blog, which should then add the new post to my Micro.blog timeline, as well as cross-post it to BlueSky, Mastodon, and Threads. 

As best I can tell, the JSONFeed at `/blog/feed.json` is valid. Here's how I have it configured:

First, here's my `/layouts/_default/list.jsonfeed.json`:

```
{{- $pctx := . -}}
{{- if .IsHome -}}{{ $pctx = site }}{{- end -}}
{{- $pages := slice -}}
{{- if or $.IsHome $.IsSection -}}
{{- $pages = $pctx.RegularPages -}}
{{- else -}}
{{- $pages = $pctx.Pages -}}
{{- end -}}
{{- $limit := site.Config.Services.RSS.Limit -}}
{{- if ge $limit 1 -}}
{{- $pages = $pages | first $limit -}}
{{- end -}}
{{- $title := "" }}
{{- if eq .Title .Site.Title }}
{{- $title = .Site.Title }}
{{- else }}
{{- with .Title }}
{{- $title = print . " on "}}
{{- end }}
{{- $title = print $title .Site.Title }}
{{- end }}
{
    "version": "https://jsonfeed.org/version/1.1",
    "title": {{ $title | jsonify }},
    "home_page_url": {{ .Permalink | jsonify }},
    {{- with  .OutputFormats.Get "jsonfeed" }}
    "feed_url": {{ .Permalink | jsonify  }},
    {{- end }}
    {{- if (or .Site.Params.author .Site.Params.author_url) }}
    "authors": [{
      {{- if .Site.Params.author }}
        "name": {{ .Site.Params.author | jsonify }},
      {{- end }}
      {{- if .Site.Params.author_url }}
        "url": {{ .Site.Params.author_url | jsonify }}
      {{- end }}
    }],
    {{- end }}
    {{- if $pages }}
    "items": [
        {{- range $index, $element := $pages }}
        {{- with $element }}
        {{- if $index }},{{end}} {
            "title": {{ .Title | jsonify }},
            "id": {{ .Permalink | jsonify }},
            "url": {{ .Permalink | jsonify }},
            {{- if .Site.Params.showFullTextinJSONFeed }}
            "summary": {{ with .Description }}{{ . | jsonify }}{{ else }}{{ .Summary | jsonify }}{{ end -}},
            "content_html": {{ .Content | jsonify }},
            {{- else }}
            "content_text": {{ with .Description }}{{ . | jsonify }}{{ else }}{{ .Summary | jsonify }}{{ end -}},
            {{- end }}
            {{- if .Params.cover.image }}
            {{- $cover := (.Resources.ByType "image").GetMatch (printf "*%s*" (.Params.cover.image)) }}
            {{- if $cover }}
            "image": {{ (path.Join .RelPermalink $cover) | absURL | jsonify }},
            {{- end }}
            {{- end }}
            "date_published": {{ .Date.Format "2006-01-02T15:04:05Z07:00" | jsonify }}
        }
        {{- end }}
        {{- end }}
    ]
    {{ end }}
}
```

Then, here's the relevant portion of my `hugo.yaml` file:

```
mediaTypes:
  application/feed+json:
    suffixes:
      - json
outputs:
  home:
    - HTML
    - RSS
    - JSON
  section:
    - HTML
    - RSS
    - JSONFeed
outputFormats:
  RSS:
    mediaType: application/rss+xml
    baseName: feed
  JSONfeed:
    mediaType: application/feed+json
    baseName: feed
    rel: alternate
    isPlainText: true
```

Is anything obviously wrong with the way I have things set up?