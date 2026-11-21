# Hero social proof card: live stream of completed Blowhorn activities - design plan

Issue blowhorn-ai/blowhorn-site#457. Status: design plan, written after Lee
asked on 2026-11-21 for a design plan here and a PR for it (comment
7059480302). This PR holds the plan only, no code. Merge held pending Lee's
review.

This plan is grounded in what is already on master, verified 2026-11-21
against origin/master (1e08ef9) and the #2057 thread. Most of the issue is
already built; what is left is one Cloud-side blocker, one Cloud data
question, one UX slice Kate owns, and two decisions for Lee. Nothing below
re-does work that already shipped, and nothing below starts the gated
slices early.

## The idea, as the issue frames it

One small card in the blowhorn.ai hero showing a Blowhorn user who just
finished an activity: platform icon, one line (role plus result), time since
it ran, a link to the user's public profile. One card at a time, swapping
about every 8s, pausing on hover, static under `prefers-reduced-motion`.
Major Blowhorn fills the spot when the feed is empty. Locked-6 flat 2D,
Layer5 green accent.

Two phases. Phase 1 is seeded sample events so the card can be built and
tuned now, with a checked-in JSON Schema the real feed also conforms to.
Phase 2 is a Cloud endpoint serving recent Public completed activities from
the run results Cloud already stores. Each activity gets a visibility
setting (Public, Org only, Private); the card only shows Public activities,
and the control lives in the app on the activity, following the screen
brief process (brief, Figma, code).

## What is already built (verified on master)

- **Seed data and schema - done.** PR #461 (merged 2026-11-05) added the
  public activity feed schema and sample data. PR #556 (merged 2026-11-09,
  merge commit 99b8e3cf) added the 75-item examples bundle
  (`data/activity_feed.examples.json`) and its schema
  (`schemas/activity_feed.examples.schema.json`).
- **The card - done, then rebuilt.** PR #556 wired the card to the live
  feed. PR #568 rebuilt it as a premium social-proof card, and PR #585
  moved it to the Distributed teams section on the Signal home (it stays
  in the hero on Reveille). Rotation is every 8s, pauses on hover and
  focus, holds a still frame under `prefers-reduced-motion`, with progress
  dots and a designed empty state ("No public activity yet"). The live
  behaviour is documented in `docs/activity-feed.md`.
- **The live feed consumer - done.** The card asks
  `GET <cloud_url>/api/events/feed` for `EventFeedPage` items, pinned to
  meshery/schemas v1.3.117 (`schemas/event_feed_page.schema.json`). When
  the feed is empty, the request fails, or the payload is invalid, the
  card rotates the bundled examples, labelled "Examples". The card is
  never blank, and the first bundled example is in the HTML so the card
  reads with no JavaScript.
- **The engine publisher - done.** blowhorn-ai/blowhorn#2268 (merged
  2026-11-09, da3829846) publishes completed schedule events in the
  `ScheduleCompletedEventMetadata` shape, gated on the account's
  `shareActivityPublicly` switch, fail-closed on read errors.
- **Per-activity visibility - done.** blowhorn-ai/blowhorn#2440 (merged
  2026-11-17) lets an activity carry its own visibility by writing
  `visibility=private` in its Params; those completed runs stay inside
  the org and never appear in the public feed. Unset, or `public`,
  follows the account's `shareActivityPublicly` switch, which stays the
  master gate. There is no third value: Cloud's EventVisibility is
  private/public only, and private already means visible only inside the
  event's organization, so Org only is private spelled out. The control
  on the activity itself still waits on a Blowhorn UX brief.
- **The visibility setting - designed, account-wide.** Per Mia's update
  on blowhorn-ai/blowhorn#2057 (2026-11-05), visibility is one
  account-wide switch, not a per-activity control: "Share my activity
  publicly" under "Share anonymous usage data" in Settings Privacy, on
  by default (Public), off is Private. Brief merged in
  blowhorn-ai/blowhorn#2061, Figma for the Settings Privacy card linked
  from that comment.

## Remaining slices

### Slice A - Cloud CORS (the sharp blocker, not a site-repo change)

As of 2026-11-09 the feed answers `Vary: Origin` but sends no
`Access-Control-Allow-Origin` for `https://blowhorn.ai`, so a browser
blocks the response and the card shows the examples. The account
service needs to allow `https://blowhorn.ai` (and
`https://www.blowhorn.ai`) on `GET /api/events/feed`. Until then the live
path cannot be seen in a browser. Tracked on blowhorn-ai/blowhorn#2057.
Once Cloud lands it, verify in a browser that live rows render, and the
card's live path is proven end to end.

### Slice B - Seed events in the live feed (Cloud data question)

Cloud reported about 100 seed events from 25 fake accounts. EventFeedItem
has no seed or example marker, so a seed event in the live feed would
render as real activity. Cloud must keep seed events out of the public
feed, or add a marker to the schema (and the site re-projects
`schemas/event_feed_page.schema.json`). Do not flip the card to
live-first until this is settled. Tracked on blowhorn-ai/blowhorn#2057.

### Slice C - Card spec and Figma (Blowhorn UX, Kate's slice)

Kate took this on 2026-11-17 (comment 6939831658): card spec plus Figma,
with the seeded-sample-events JSON Schema alongside it, then seed data
plus schema in the site repo, then the Phase 2 live feed only after
#2057 lands. No Figma link has been posted on #457 yet. This plan does
not redo her slice; it records it as hers and open. Her step 2 is
already on master (see above), so her remaining slice is the spec and
Figma, plus a check that the rebuilt card (#568, #585) still matches it.

### Slice D - Decision for Lee: the profile link

The issue text says the card "Links to the user's public profile." PR
#568 built a View profile pill, and PR #585 deliberately dropped it
(commit 95f1399, "drop View profile"). The card now renders no profile
link even when a live row carries `publicProfileUrl`. Confirm the
removal stands, or reopen it as a slice (link the name, or restore the
pill). No code here until Lee decides.

### Slice E - Decision for Lee: Major Blowhorn as the empty-state filler

The issue text says "Major Blowhorn fills the spot when the feed is
empty." Today an empty live feed shows the labelled Examples bundle,
and a card with no rows at all shows "No public activity yet". Say
whether a Major Blowhorn filler is still wanted, or the Examples bundle
is the empty state. No code here until Lee decides.

### Slice F - Separate: user-level pause

blowhorn-ai/blowhorn#2069, a user-level pause, needs a design call
first. Tracked on #2057; not part of this plan.

## Non-goals

- No change to the feed contract: meshery/schemas is the source of
  truth, and the site re-projects rather than redefining it.
- No new schema, no change to the Examples bundle, no change to the
  card's rotation, pause, or reduced-motion behaviour.
- No profile link until Slice D is decided, and no live-first flip
  until Slices A and B land.

## Order of work

1. Lee reviews this plan and decides Slices D and E.
2. Kate finishes Slice C (spec and Figma) against the rebuilt card.
3. Cloud lands Slice A (CORS) and settles Slice B (seed events).
4. With A and B landed, verify the live path in a browser, then close
   #457. Slices D and E, if reopened, land as their own small PRs.
