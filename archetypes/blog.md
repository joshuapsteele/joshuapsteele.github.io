---
title: '{{ replace .File.ContentBaseName "-" " " | title }}'
date: {{ .Date }}
draft: false
author: joshuapsteele
tags: []
categories: []
showToc: true
TocOpen: false
url: /{{ replace .File.ContentBaseName " " "-" | lower }}/
---

