# YouTube


> What Blowhorn can do on YouTube, and how each action behaves there.


Blowhorn works on YouTube in your own signed-in Google Chrome,
and this page lists what it can do there.

<!-- BEGIN generated limits: release/scripts/capabilities_docs/build.py; do not edit -->

## Limits

The limits Blowhorn knows for YouTube.

| Limit | Value |
|---|---|
| Description | 5000 |
| Title | 100 |
| Video | 256000000000 bytes |
| Short length | 180 s |

<!-- END generated limits -->

## Supported actions



- **[Post](#action-post)**: Uploads a video through YouTube Studio with its title, description and visibility (private unless you choose unlisted or public), or as a Short. With Community set to yes, it publishes a post on your channel's Posts tab instead. Limits: At most 3 uploads and 2 Posts tab posts per profile a day. A Short longer than 3 minutes or wider than it is tall is refused before anything opens. Check each upload in YouTube Studio.
- **[Comment](#action-comment)**: Comments on the YouTube video you point it at. Limits: At most 10 a day per profile. A comment with an @name in it is refused. A scheduled run never comments; it waits for a run you start.
- **[Reply](#action-reply)**: Replies to the YouTube comment you point it at, by the comment's own link. Limits: At most 10 a day per profile. A reply to a reply, or one with an @name in it, is refused. A scheduled run never replies.
- **[Amplify](#action-amplify)**: Likes a video from each of your profiles. Limits: At most 20 likes a day per profile. A scheduled run never likes; it waits for a run you start.
- **[Analytics](#action-analytics)**: Reads your channel's and videos' figures through the YouTube Analytics and Data APIs, with the profile's own OAuth consent. Limits: Read-only. A profile without the consent is skipped. YouTube figures are kept for 30 days.


## Related

- [All platforms](/docs/reference/platforms/) - every platform, side by side.
- [Why Blowhorn uses your own browser](/docs/explanation/your-own-chrome/) - browser versus API.
- [You're in control](/docs/explanation/youre-in-control/) - every safety control in one place.

