---
title: "What the analytics numbers mean"
description: "Measured versus trended counts, what each tile counts, and how fresh the numbers are."
weight: 289
---

Analytics counts what the platforms showed, not what Blowhorn hoped.
Every number is either measured, read off the platform during
collection, or trended, appended to the profile's history so growth
reads across runs. Nothing is estimated and no reach is promised.

LinkedIn tiles count the page: total followers, new followers over 30
days, impressions, and reactions, each read from the page's own
analytics export during collection. LinkedIn collects for one profile
at a time; a run asked for all profiles says so and collects none for
LinkedIn. X and Bluesky append one follower and following trend row
each per run instead of tiles: two counts and a timestamp, growing the
CSV history the report reads.

`blowhorn analytics` collects into the repository-root `data/analytics/`
directory and records the readings beside the exports, so a later
collection reads as change, not as a fresh claim. `blowhorn report`
summarizes the exports already sitting there into
`analytics_report.html`; it reads local files only, so stale exports
give a stale report and it says which exports it read. The analytics
screen states each number's freshness in its header for the same
reason: a count without a date is decoration.

A dry run prints the tile shapes with no values, proving the shape of
the read without touching a platform. Bluesky page-style tiles do not
exist: Bluesky gives the trend row, and asking the tiles for more
would be inventing numbers the platform never showed.

## Related

- [Collect and read your analytics](/docs/how-to/measure/analytics/) - collect now, read the report.
- [The Blowhorn app, screen by screen](/docs/reference/use-the-desktop-app/) - the analytics screen.
- [Platforms](/docs/reference/platforms/) - which platforms collect what.
- [Preview and publish queued posts](/docs/how-to/publish/post-content/) - dry runs print shapes too.
