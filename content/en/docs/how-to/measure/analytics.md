---
title: "Collect and read your analytics"
description: "Collect LinkedIn and X follower numbers, then read the history and the HTML report."
weight: 160
aliases: [/docs/how-to/collect-analytics/]
---

# Collect and read your analytics

Collect follower numbers from LinkedIn and X, then read them back as dated
series in the app or the command line.

Blowhorn collects LinkedIn pages and X profiles. A Bluesky scope is accepted by
the command but collects nothing today, so scope your runs to `linkedin` and
`x`.

## Collect

```bash
blowhorn analytics --platform linkedin --profile ada --lookback 30
blowhorn analytics --platform x --profile all
```

LinkedIn exports honour `--lookback`; X appends a follower and following trend
row per profile. Each run prints a receipt of the rows it collected. In the
app, the "analytics" screen collects on demand with "collect now" and draws
the same series.

## Read the history

```bash
blowhorn analytics history --since 30d
blowhorn analytics history --subject ada --json
```

`history` renders every LinkedIn page and every X profile as one dated series
from your account, whichever machine collected it. `--since` takes days, weeks,
months, years or `all`, and filters which points print, never what the 30-day
figures compute from.

Treat the 30-day net, growth rate and unfollowed figures as derived, not
measured: the output labels them so. LinkedIn measures new followers, so only
LinkedIn pages carry an unfollowed figure. X measures nothing but the total,
so an X profile has a net change and no unfollowed figure at all.

## Read the HTML report

```bash
blowhorn report
blowhorn report --no-open
```

`report` builds `analytics/analytics_report.html` from the exports already on
disk and opens it; `--no-open` writes the file and leaves it closed. Collect
first when you want fresh numbers: the report reads local files only.

## Related

- [Review what ran](/docs/how-to/measure/review-runs/) - per-machine operations from the same ledger
- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - collect on a schedule
- [Change your defaults](/docs/how-to/settings/defaults/) - pace, excluded profiles, logs
- [What the analytics numbers mean](/docs/explanation/analytics/) - measured versus trended
