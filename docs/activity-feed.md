# Hero activity feed

The home hero shows a small activity card: one recent line, who it was for, and Previous / Next. It ships with a bundled example collection so the card works on a first visit with no network. The live transport is disabled. Nothing in the page script names an endpoint.

Public copy on the card says the lines are examples. It does not name a cloud service, a price, or a browser.

## What is wired

| Piece | Role |
|---|---|
| `schemas/activity_feed.schema.json` | Contract v1. `sample: true` marks a whole payload as example data. An item may set `example: true`. |
| `data/activity_feed.examples.json` | The collection baked into the home page. `sample` is true, and every item has `example: true`. |
| `data/activity_feed.sample.json` | A shorter sample of the same contract, not rendered. |
| `layouts/_partials/activity-feed.html` | Static card (first example, Examples label) plus a `script type="application/json"` block. Hugo `jsonify` writes that block. The partial also loads the script, fingerprinted and deferred, and only where the card is rendered. |
| `layouts/_partials/home/signal.html` | Public home. The card sits in the hero grid under the copy, so the film beside the copy keeps its row. |
| `layouts/_partials/home/reveille.html` | Same slot, under the copy and beside the hero art. |
| `assets/js/activity-feed.js` | Validation, rotation, and `createFeedSource`. |
| `assets/css/site.css` | Card layout, under "Hero activity card". Glass variant, tokens only. |

`make check-schemas` validates the example file. `make test-activity-feed` runs `node --test` on `assets/js/activity-feed.test.mjs`. `make test-scripts` and `make check` run that target.

## Example collection

75 items. Each line is one supported action on a platform that `data/integrations.json` marks supported and that `data/platforms/<id>.yaml` lists for that action.

Actions used: post, comment, reply, amplify, react, follow, unfollow, accept, withdraw, find.

Analytics is a supported action and is left out. It records reach figures, and this card does not show performance stats, counts, or outcomes.

Roles are generic personas: Solo founder, Agency, Open source maintainer, DevRel, Marketing manager, Community manager, Founder. There is no display name, avatar, or profile URL. Account ids look like `example-account-12`. `completedAt` is a fixed date in October 2026. The card does not turn those into "just now" or "2 min ago". Example rows show the label "Example activity".

The static HTML shows the first item and a visible Examples badge: "Illustrative examples, not real customer activity." With script off, that first item stays. The Previous and Next controls keep their space and stay hidden until the script is running, so the card does not jump.

## Runtime behaviour

`boot` reads the JSON block and calls `createFeedSource({ transport: null, fallback })`. `transport` defaults to null. A null transport returns the bundled collection and does not start a timer.

Rotation is 7 seconds, a short opacity crossfade. It pauses while the pointer is over the card or focus is inside it, and while `document.hidden` is true (`visibilitychange`). `prefers-reduced-motion: reduce` skips the timer and the fade. Previous and Next still move one row. The rotating line is not an `aria-live` region. The card's accessible name is the static "Recent activity" label. `destroy` clears every timer and removes the listeners.

Items are checked before they are shown: known fields only, length limits, the platform list, `https` URLs, no `javascript:` or `data:` URLs. Text is written with `textContent`. A profile link, if a live item ever has one, uses `rel="noopener noreferrer nofollow"` and `target="_blank"`. Example rows do not render that link. Avatar URLs are not requested.

Invalid items are dropped. If none remain, or the body is empty or not JSON, the card uses the fallback. Timeout, a thrown network error, and any non-success status do the same. HTTP 429 also sets a wait from `Retry-After` (delta-seconds or an HTTP date) and will not call the transport again until that time. A missing or unreadable `Retry-After` waits 60 seconds.

A payload with `sample: true`, or an item with `example: true` or `sample: true`, keeps the Examples label. Those rows are not live events.

Live events, if a transport is ever passed in, may be shown only for the response `Cache-Control` `max-age`. That lifetime is capped at 30 seconds. A missing or zero `max-age` does not grant any hold, so the card shows the bundled examples instead. When the lifetime ends, the card asks the transport once more. If that refresh fails, or there is no transport, the live rows are dropped and the bundled examples take their place, with the Examples label. Expired live rows are never the offline fallback.

Nothing in this script writes `localStorage`, `sessionStorage`, `IndexedDB`, or a service-worker cache. Avatar URLs are not requested.

## Attaching a transport later

Leave the URL out of `assets/js/activity-feed.js`. Pass a function when the contract below is settled:

```javascript
import { createFeedSource, mountActivityFeed } from "./activity-feed.js";

const source = createFeedSource({
  transport: () => fetch(FEED_URL, { headers: { accept: "application/json" } }),
  fallback: embeddedExamples,
  timeoutMs: 8000,
});
mountActivityFeed(card, { source });
```

`FEED_URL` belongs to the caller. The browser global `BlowhornActivityFeed` exposes the same functions after the module loads. The only refresh is the one at the end of `max-age` (30 seconds at most). The transport on the public site stays null, so that refresh never runs there.

## Unresolved contract

These are open. Do not invent values for them in the page.

- Final field names, and the meaning of `sample`, as served by Layer5 Cloud. This schema is the preview contract (version 1), not a confirmed response.
- A machine-readable sample or seed marker on Cloud's seed events. Cloud reports about 100 seed events from 25 fake accounts. Those must always render with the Examples label, including when they are mixed into a live payload. Today the card treats `sample: true` on the payload, and `example: true` or `sample: true` on an item. The field name Cloud will use is not decided here.
- Whether real public events may be shown at all, and how a person revokes that. If they are shown, the page holds them only for `max-age`, capped at 30 seconds, then drops them. Avatar URLs stay unloaded.
