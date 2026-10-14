---
title: Internal
layout: internal
description: Internal pages. Rendered only by `hugo --environment internal`.
# Keep internal pages out of section lists, menus, the search index,
# llms.txt and related-page lists, even in the internal build. Pages still
# render (segments decide whether they render at all).
cascade:
  - build:
      list: never
      render: always
    sitemap:
      disable: true
build:
  list: never
  render: always
sitemap:
  disable: true
---

The internal Blowhorn site. Nothing under this section is committed to this
repository: `make build-internal` copies it from a private checkout at build
time (see docs/deploy.md). The public build never renders it.

- [GTM strategy](/internal/strategy/)
- [Assistant comparison](/internal/strategy/compare/)
- [Break-even analysis](/internal/finance/): report and downloadable XLSX model
