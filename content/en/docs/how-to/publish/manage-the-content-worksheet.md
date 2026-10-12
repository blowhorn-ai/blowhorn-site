---
title: "Manage the content queue"
description: "Add, edit, and track queued posts in the Content screen and from the command line."
weight: 80
aliases: [/docs/how-to/manage-the-content-worksheet/]
---

# Manage the content queue

Everything you publish waits in the content queue first. Add rows in the
desktop app's Content screen, from the command line, or with the capture
bookmarklet. `blowhorn post` publishes from these rows and nothing else.

## The columns a run reads

| Column | What to put there |
| --- | --- |
| `Platform` | One `blowhorn post` publishes to: `linkedin`, `x`, `reddit`, `hn`, `slack`, `bluesky`, `github` (`twitter` and `bsky` also work) |
| `Profile` | Who posts it, or `all`. Never blank: a blank profile is refused rather than read as `all` |
| `Destination` | Where it goes: `r/<sub>` on Reddit, a link URL on Hacker News, the workspace on Slack (the channel goes in `Amplify`) |
| `Message Text` | The post itself |
| `Title` | Hacker News and Reddit titles |
| `Approved?` | `yes` to let a run pick the row up |
| `Promote On` | `YYYY-MM-DD HH:MM:SS` in this machine's own zone; blank means now |
| `Image URL`, `GDrive Link`, `Video URL` | One attachment for the post |
| `Amplify` | URL of existing content to amplify instead of publishing ([Amplify an existing post](/docs/how-to/publish/amplify-a-post/)) |
| `Comment on` | URL to reply to, with the reply in `Message Text` ([Reply to a post](/docs/how-to/publish/reply-to-a-post/)) |
| `Date Promoted`, `Promotion Link` | What the run writes back. Clear `Date Promoted` to queue the row again |

Row numbers are the queue's own, stable for the life of a row: deleting a
row never renumbers the rest, so a row number is safe to keep and script
against.

## Row states

`blowhorn content list` reports each row's state, decided by the same
rules that make a row pending for a post run:

- `pending`: a run will pick it up.
- `scheduled`: `Promote On` is in the future.
- `draft`: `Approved?` is not `yes`.
- `done`: `Date Promoted` is set.
- `unread`: the submit was clicked and nothing afterwards confirmed it
  (`Date Promoted` says `clicked, outcome not read`). The row is not
  pending and not done, and no run posts it again. Check the platform,
  then clear `Date Promoted` to try it again.
- `invalid`: a `Promote On` that will not parse. A post run skips it with
  a warning.
- `unsupported`: a `Platform` `blowhorn post` cannot publish to.

## From the command line

```bash
# Every row with its state.
blowhorn content list

# Only what a run would pick up now, as JSON.
blowhorn content list --pending --json

# One profile's rows; only X rows.
blowhorn content list --profile kate
blowhorn content list --platform x

# One row, every column, its state and its problems.
blowhorn content get 12 --json

# Create a row: it takes the next row number, which is never reused.
blowhorn content upsert --payload '{"Platform":"linkedin","Profile":"kate","Message Text":"Our v2.0 release is out","Approved?":"yes"}'

# Update in place: the payload is merged over the row; columns it does not
# name are left as they were.
blowhorn content upsert --row 12 --payload '{"Approved?":"yes"}'

# Delete (requires --yes; --dry-run previews first).
blowhorn content delete 12 --yes
```

A write refuses rather than guesses: an unknown `Platform`, a `Profile`
your account does not know, a blank `Profile`, an unparseable `Promote On`,
and unknown fields are all refused with the reason named.

## Capture a page from the browser

The bookmarklet turns the page you are reading into a new content entry
without retyping it. It holds no credential and reaches no account: it hands
the page's address, title, and any selected text to the desktop app, which
opens the Content screen on a new entry pre-filled from it.

To install it: in the app, **Content → Bookmarklet → Copy code**, then add
a bookmark in your browser named `Blowhorn: capture` and paste the code as
its address.

or paste this:

```
javascript:(function(w,d){var s=String((w.getSelection&&w.getSelection())||"").slice(0,4000);var u="blowhorn://content/new?url="+encodeURIComponent(String(w.location.href).slice(0,2048))+"&title="+encodeURIComponent(String(d.title||"").slice(0,300))+"&text="+encodeURIComponent(s);var left=false;function gone(){left=true}w.addEventListener("blur",gone);d.addEventListener("visibilitychange",gone);w.setTimeout(function(){w.removeEventListener("blur",gone);d.removeEventListener("visibilitychange",gone);if(left||d.visibilityState==="hidden"||(d.hasFocus&&!d.hasFocus()))return;var n=d.createElement("div");n.setAttribute("role","alert");n.textContent="Blowhorn did not open. Install or start the Blowhorn desktop app, then try the bookmarklet again.";n.style.cssText="position:fixed;top:16px;right:16px;z-index:2147483647;max-width:360px;padding:10px 14px;background:#111;color:#f5f5f5;font:13px/1.4 -apple-system,system-ui,sans-serif;border:1px solid #444;border-radius:6px;box-shadow:0 4px 16px rgba(0,0,0,.4);cursor:pointer";n.onclick=function(){n.parentNode&&n.parentNode.removeChild(n)};d.body.appendChild(n);w.setTimeout(function(){n.parentNode&&n.parentNode.removeChild(n)},8000);},2000);w.location.href=u;})(window,document)
```

You choose what the link is for (**post the link**, **amplify it**,
**reply to it**: the URL lands in `Message Text`, `Amplify`, or `Comment
on`), pick the platform and profile, and the editor's add button queues
the entry. Nothing reaches the queue until you add it.

## Related

- [Post content](/docs/how-to/publish/post-content/) - publish the rows.
- [Amplify an existing post](/docs/how-to/publish/amplify-a-post/) - the `Amplify` column.
- [Reply to a post](/docs/how-to/publish/reply-to-a-post/) - the `Comment on` column.
- [`blowhorn post` reference](/docs/reference/post/) - what "pending"
  means and what a run writes back.
