---
title: "Collect and read your analytics"
description: "Collect LinkedIn and X follower numbers, read the history, one activity's result and the HTML report."
weight: 160
aliases: [/docs/how-to/collect-analytics/]
---


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
app, the "results" screen collects on demand with "collect now" and draws
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

A LinkedIn page also carries its reception: the latest impressions and
reactions, the date they were read, and their 30-day change (derived, like
the follower figures).

## Read one activity's result

```bash
blowhorn analytics activity 42
blowhorn analytics activity 42 --profile ada --json
```

`activity` takes a content row number and answers, for each profile and
platform the row is addressed to:

- **Delivery** (measured): whether it went out and when, the link to the live
  item, the computer and Chrome profile that ran it, and for a failed attempt
  the error and the fix to try next.
- **Reception** (measured): the activity's own impressions, clicks, likes,
  comments, reposts and rates with the date they were read, compared with the
  median of the page's other activities. LinkedIn page activities only today;
  anywhere else it says reception isn't collected, never zero.
- **Follower change** (derived): followers at the reading before the activity
  and the first reading a week after it. It is a correlation, not a cause.

A computer that is not connected to a store yet says so in one sentence and
exits 3.

## Import content exports

```bash
blowhorn analytics import-exports
blowhorn analytics import-exports data/analytics/layer5_content_20260719_033126.xls --dry-run --json
```

Each LinkedIn collection saves a page content export and imports its "All
posts" sheet into the store by itself. `import-exports` does the same for
exports already on disk: every `*_content_*.xls` under `data/analytics/` when
you name no paths. Each post is matched to the content row whose promotion link
names it; a post with no matching row is kept and marked unmatched. The output
verifies every file: rows read, matched, unmatched, skipped with the reason,
and stored. Importing the same export twice stores it once; `--dry-run` reads
and matches without storing.

## Read the HTML report

```bash
blowhorn report
blowhorn report --no-open
```

`report` builds `data/analytics/analytics_report.html` from the exports already on
disk and opens it; `--no-open` writes the file and leaves it closed. Collect
first when you want fresh numbers: the report reads local files only.

## Related

- [Review what ran](/docs/how-to/measure/review-runs/) - per-machine operations from the same ledger
- [Schedule a job](/docs/how-to/schedule/schedule-a-job/) - collect on a schedule
- [Change your defaults](/docs/how-to/settings/defaults/) - pace, excluded profiles, logs
- [What the analytics numbers mean](/docs/explanation/analytics/) - measured versus trended
