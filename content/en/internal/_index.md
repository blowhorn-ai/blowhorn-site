---
title: Internal
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

This section is excluded from the public build by the `public` segment in
`hugo.toml`. This repository is public: do not commit confidential content here.
