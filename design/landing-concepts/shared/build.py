#!/usr/bin/env python3
"""Builds the three landing concepts from one content structure.

Every concept renders the same section components (below) with its own copy config
and section order. The look comes only from a theme layer: shared/themes/<theme>.css,
scoped by <html data-theme="...">. Any page can preview another theme with
?theme=signal|full-volume|open-field, which proves the layers are swappable.
"""
import html, pathlib

ROOT = pathlib.Path(__file__).resolve().parent.parent
A = "../assets"
THEMES = ["signal", "full-volume", "open-field"]

PLATFORMS = [
    # key, name, logo, reach, example link
    ("linkedin", "LinkedIn", "linkedin-in-bug.png", "Your Chrome", "linkedin.com/feed/update/urn:li:activity:..."),
    ("x", "X", "x-logo-black.png", "Your Chrome", "x.com/you/status/..."),
    ("reddit", "Reddit", "reddit-logo.png", "Your Chrome", "reddit.com/r/devops/comments/..."),
    ("hn", "Hacker News", "hacker-news-y18.svg", "Your Chrome", "news.ycombinator.com/item?id=..."),
    ("slack", "Slack", "slack-mark.svg", "Slack API", "community.slack.com/archives/..."),
    ("bluesky", "Bluesky", "bluesky-butterfly-blue.svg", "Bluesky API", "bsky.app/profile/you/post/..."),
]

def esc(s):
    return html.escape(s, quote=True)

def logo(file, size=20):
    return f'<span class="ptile"><img src="{A}/platforms/{file}" alt="" width="{size}" height="{size}"></span>'

# ---------------------------------------------------------------- components

def nav(c):
    return f'''
<header class="nav" data-component="nav">
  <div class="wrap nav__inner">
    <a class="nav__brand" href="#top" aria-label="Blowhorn home">
      <img class="logo-on-light" src="{A}/brand/blowhorn-lockup-horizontal.svg" alt="Blowhorn" width="150" height="38">
      <img class="logo-on-dark" src="{A}/brand/blowhorn-lockup-horizontal-on-dark.svg" alt="Blowhorn" width="150" height="38">
    </a>
    <nav class="nav__links" aria-label="Primary">
      <a href="#how">Product</a><a href="#roles">Solutions</a><a href="#proof">Trust</a><a href="#pricing">Pricing</a><a href="#footer">Docs</a>
    </nav>
    <div class="nav__actions">
      <a class="nav__signin" href="#cta">Sign in</a>
      <a class="btn btn--primary btn--sm" href="#cta">Download for Mac</a>
    </div>
  </div>
</header>'''

def hero(c):
    return f'''
<section class="hero" id="top" aria-labelledby="hero-title" data-component="hero">
  <div class="hero__bg" aria-hidden="true"></div>
  <div class="wrap hero__grid">
    <div class="hero__copy">
      <p class="eyebrow"><span class="eyebrow__dot" aria-hidden="true"></span>{c["eyebrow"]}</p>
      <h1 id="hero-title" class="hero__title">{c["headline"]}</h1>
    </div>
    <div class="hero__aside">
      <p class="hero__sub">{c["sub"]}</p>
      <div class="hero__ctas">
        <a class="btn btn--primary btn--pop" href="#cta"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11m0 0 4.5-4.5M12 15l-4.5-4.5M5 19h14"/></svg>Download for Mac</a>
        <a class="btn btn--ghost" href="#how">{c.get("cta2", "See how it works")}</a>
      </div>
      <p class="hero__note">{c["note"]}</p>
    </div>
  </div>
  {c.get("hero_extra", "")}
  {('<div class="wrap hero__explore" data-component="explorer">' + explorer_body(c) + '<p class="hero__explore-note">Concept preview: counts use each network\'s own limits, and a Hacker News title over 80 characters is refused, never cut short. <a href="#cta">Download for Mac</a>, about a minute to set up.</p></div>') if c.get("hero_explorer") else ""}
  <div class="wrap hero__visual">
    {app_mock(c)}
    {major_float(c)}
  </div>
</section>'''

def major_float(c):
    img = c.get("major_float")
    if not img:
        return ""
    return f'<img class="hero__major" src="{A}/major/{img}" alt="Major Blowhorn, a teal rooster, pointing and shouting into his gold bullhorn" width="649" height="560">'

def app_mock(c):
    rows = "".join(f'''
          <li class="dcard" data-platform="{k}" style="--i:{i}">
            <div class="dcard__head">{logo(f, 16)}<span class="dcard__name">{n}</span>
              <span class="pill" data-status><span class="pill__dot"></span><span class="pill__text">Went out</span></span></div>
            <p class="dcard__meta">{"via your Chrome, as you" if r == "Your Chrome" else "via the " + r + ", as you"}</p>
            <p class="dcard__link">{l}</p>
          </li>''' for i, (k, n, f, r, l) in enumerate(PLATFORMS))
    return f'''
    <figure class="app" data-component="app-mock" aria-label="Example of the Blowhorn desktop app: one post went out to LinkedIn, X, Reddit, Hacker News, Slack and Bluesky as you">
      <div class="app__bar" aria-hidden="true"><span></span><span></span><span></span><em>Blowhorn</em></div>
      <div class="app__body">
        <aside class="app__rail" aria-hidden="true">
          <div class="app__brand"><img src="{A}/brand/blowhorn-icon-on-dark.svg" alt="" width="20" height="20">Blowhorn</div>
          <div class="app__new">+ New activity <kbd>&#8984;N</kbd></div>
          <ul class="app__navlist">
            <li>Home</li><li class="is-on">Activity <small>3 today</small></li><li>Profiles <small><b class="dot dot--pending"></b>1 needs you</small></li><li>Performance</li>
          </ul>
          <div class="app__spacer"></div>
          <div class="app__watch"><p><b class="dot dot--live"></b>This computer is on watch</p><p class="muted">Next check in 4 min <span class="chip">Pause</span></p></div>
          <div class="app__acct"><span class="avatar">YO</span><span><b>You</b><small>Example org, Team plan</small></span></div>
        </aside>
        <div class="app__list" aria-hidden="true">
          <div class="app__listhead"><b>Activity</b><kbd>&#8984;K to find</kbd></div>
          <div class="app__tabs"><span>Upcoming <small>12</small></span><span>Drafts <small>3</small></span><span>Routines <small>4</small></span><span class="is-on">History</span></div>
          <p class="app__day">Today</p>
          <div class="arow is-on"><span class="tag">Post</span><b>v2.0 ships today</b><time>9:02 AM</time><span class="arow__sub">6 networks, as you</span><span class="pill pill--sm"><span class="pill__dot"></span>Went out</span></div>
          <div class="arow"><span class="tag">Repost wave</span><b>v2.0 ships today</b><time>9:30 AM</time><span class="arow__sub">12 teammates</span><span class="pill pill--sm pill--pending"><span class="pill__dot"></span>7 of 12</span></div>
          <div class="arow"><span class="tag">React</span><b>Rally the release issue</b><time>9:45 AM</time><span class="arow__sub">GitHub issue, 12 profiles</span><span class="pill pill--sm pill--sched"><span class="pill__dot"></span>Scheduled</span></div>
          <div class="arow"><span class="tag">Comment</span><b>Reply on the HN thread</b><time>11:10 AM</time><span class="arow__sub">Hacker News, as you</span><span class="pill pill--sm pill--sched"><span class="pill__dot"></span>Scheduled</span></div>
        </div>
        <div class="app__detail">
          <div class="app__crumbs" aria-hidden="true"><span>Activity &#8250; History &#8250; Post</span><span class="chip">Duplicate</span></div>
          <p class="app__kind"><span class="tag">Post</span><span class="pill pill--sm" data-summary><span class="pill__dot"></span><span class="pill__text">Went out</span></span></p>
          <h3 class="app__title">v2.0 ships today</h3>
          <p class="app__meta">Tue Oct 20, 9:02 AM CDT as <u>you</u>, ran on <u>Studio Mac</u></p>
          <blockquote class="app__msg">v2.0 is out. Faster queue, team waves, and a new Hacker News flow. Written by us, posted by us.</blockquote>
          <p class="app__section"><span>1</span>Delivery<em>Example data</em></p>
          <ul class="app__grid">{rows}
          </ul>
        </div>
      </div>
    </figure>'''

def platforms(c):
    items = "".join(f'<li class="plat">{logo(f, 28)}<span class="plat__name">{n}</span><span class="plat__reach">{r}</span></li>' for (k, n, f, r, l) in PLATFORMS)
    items += f'<li class="plat">{logo("github-invertocat-black.svg", 28)}<span class="plat__name">GitHub</span><span class="plat__reach">Reactions on issues</span></li>'
    return f'''
<section class="section platforms" id="platforms" aria-labelledby="platforms-title" data-component="platforms">
  <div class="wrap">
    <div class="shead shead--center">
      <p class="eyebrow">Platforms</p>
      <h2 id="platforms-title" class="h2">Say it once. Say it everywhere.</h2>
      <p class="lede">One queue for every network your audience reads. LinkedIn, X, Reddit and Hacker News go through your own Chrome with the Blowhorn extension. Slack and Bluesky use their APIs. On GitHub, Blowhorn rallies reactions on the issue, it doesn't post.</p>
    </div>
    <ul class="plats">{items}</ul>
  </div>
</section>'''

def explorer_body(c):
    chips = "".join(f'<label class="xchip"><input type="checkbox" checked data-x-platform="{k}"> {logo(f, 16)} {n}</label>' for (k, n, f, r, l) in PLATFORMS)
    cards = "".join(f'''
      <article class="xcard" data-x-card="{k}">
        <header>{logo(f, 18)}<b>{n}</b><span class="xcard__count" data-x-count></span></header>
        <p class="xcard__text" data-x-text></p>
        <footer><span>{"Your Chrome" if r == "Your Chrome" else r}</span><span>as you</span></footer>
      </article>''' for (k, n, f, r, l) in PLATFORMS)
    return f'''
    <div class="xbox" id="try">
      <label class="visually-hidden" for="x-input">Your announcement</label>
      <div class="xbox__field">
        <img src="{A}/brand/blowhorn-icon.svg" alt="" width="28" height="28">
        <textarea id="x-input" rows="2" data-x-input>Blowhorn v2.0 is out. A faster queue, team waves and a new Hacker News flow. Written by us, posted by us.</textarea>
        <span class="xbox__kbd">&#8984;&#9166; Queue it</span>
      </div>
      <div class="xchips" role="group" aria-label="Destinations">{chips}</div>
    </div>
    <div class="xcards" aria-live="polite">{cards}</div>'''

def explorer(c):
    return f'''
<section class="section explorer" aria-labelledby="try-title" data-component="explorer">
  <div class="wrap">
    <div class="shead shead--center">
      <p class="eyebrow">Try it</p>
      <h2 id="try-title" class="h2">Write it once. See it everywhere.</h2>
      <p class="lede">Type an announcement and see how it reads on each network, counted against that network's own limits.</p>
    </div>
    {explorer_body(c)}
  </div>
</section>'''

def how(c):
    steps = [
        ("01", "Write it once", "Draft the post in the Mac app, from the Python CLI, or let your agent draft it. Nothing goes out until you approve it.", "blowhorn post --check-queue --profile all"),
        ("02", "Pick the moment", "Queue it for now or for launch o'clock. Add the reposts, quotes, comments and reactions your team will send after it. Preview any run first.", "blowhorn post --profile all --dry-run"),
        ("03", "It goes out as you", "Your Mac does the typing and clicking in your own Chrome, at a human pace, signed in as you. Every result lands in Activity.", "blowhorn report"),
    ]
    lis = "".join(f'<li class="step"><span class="step__n">{n}</span><h3 class="h3">{t}</h3><p>{d}</p><code class="step__code">$ {code}</code></li>' for n, t, d, code in steps)
    return f'''
<section class="section how" id="how" aria-labelledby="how-title" data-component="how">
  <div class="wrap">
    <div class="shead">
      <p class="eyebrow">How it works</p>
      <h2 id="how-title" class="h2">{c.get("how_title", "You give the orders. Your Macs carry them out.")}</h2>
      <p class="lede">Blowhorn Cloud keeps your queue, profiles and run history in sync at cloud.blowhorn.ai. The work itself happens in the desktop app on machines you own.</p>
    </div>
    <ol class="steps">{lis}</ol>
  </div>
</section>'''

def roles(c):
    rs = [
        ("DevRel", "Ship the release notes, the HN post and the conference recap from one queue, in your own voice.", "Launch day", "cast/keyboard-warrior.png"),
        ("Marketing managers", "One message, many real voices. Schedule the company post and every teammate's amplification for the same minute.", "Campaigns", "cast/general.png"),
        ("Founders and maintainers", "Personal, company and project profiles in one place. Announce a release on six networks before your coffee cools.", "Open source releases", "cast/mouse-marine.png"),
        ("Team amplification leads", "Rally the team behind a post. Each person reposts as themselves, from their own Chrome, no bot to invite.", "Repost waves", "cast/robo-recruit.png"),
    ]
    lis = "".join(f'''
      <li class="role">
        <div class="role__art"><img src="{A}/{img}" alt="" loading="lazy"></div>
        <p class="eyebrow">{tag}</p>
        <h3 class="h3">{t}</h3>
        <p>{d}</p>
        <a class="role__link" href="#roles">Blowhorn for {t.lower() if t != "DevRel" else "DevRel"} <span aria-hidden="true">&#8594;</span></a>
      </li>''' for t, d, tag, img in rs)
    return f'''
<section class="section roles" id="roles" aria-labelledby="roles-title" data-component="roles">
  <div class="wrap">
    <div class="shead">
      <p class="eyebrow">Who it's for</p>
      <h2 id="roles-title" class="h2">{c.get("roles_title", "Built for the people who carry the message.")}</h2>
    </div>
    <ul class="roles__grid">{lis}</ul>
    <div class="usecases">
      <span class="eyebrow">Use cases</span>
      <a href="#roles">Launch day</a><a href="#roles">Open source releases</a><a href="#roles">Conferences</a>
    </div>
  </div>
</section>'''

def wave(c):
    return f'''
<section class="section wave" id="wave" aria-labelledby="wave-title" data-component="wave">
  <div class="wrap wave__grid">
    <div>
      <p class="eyebrow">Coordinated amplification</p>
      <h2 id="wave-title" class="h2">Real voices make a sound wave.</h2>
      <p class="lede">Schedule one message and have every profile you add amplify it at the moment you pick, each profile posting as itself. Coordinated so the same post isn't sent twice. Pause the whole wave with one command.</p>
    </div>
    <ol class="wave__list" aria-label="Example repost wave">
      <li><span class="avatar">AR</span><b>Ana R.</b><span>LinkedIn repost</span><time>9:30</time></li>
      <li><span class="avatar">RC</span><b>Ravi C.</b><span>X quote</span><time>9:31</time></li>
      <li><span class="avatar">MD</span><b>Mia D.</b><span>Bluesky repost</span><time>9:33</time></li>
      <li><span class="avatar">JO</span><b>Jon O.</b><span>GitHub reactions</span><time>9:34</time></li>
      <li><span class="avatar">KS</span><b>Kai S.</b><span>Reddit comment</span><time>9:41</time></li>
      <li class="wave__more">+ 7 more teammates <em>Example data</em></li>
    </ol>
  </div>
</section>'''

def major(c):
    img = c.get("major", "locked-hat-left.png")
    return f'''
<section class="section major" aria-label="Major Blowhorn" data-component="major">
  <div class="wrap major__grid">
    <figure class="major__fig"><img src="{A}/major/{img}" alt="Major Blowhorn, a teal rooster in a campaign hat, pointing and shouting into his bullhorn" loading="lazy"></figure>
    <div class="major__copy">
      <p class="bubble">Tab after tab. One post. Somebody call a medic.</p>
      <p class="eyebrow">Major Blowhorn</p>
      <p>He ran basic training for thirty years. Now he runs your queue: every approved action is an order, every profile is in his platoon. His recruits call him Major Blowhard. Not to his face.</p>
    </div>
  </div>
</section>'''

def proof(c):
    facts = [
        ("Human pace, always", "Blowhorn works at a pace you choose and never solves a CAPTCHA for you."),
        ("Never twice", "Your machines coordinate through one queue, so the same post isn't sent from two of them."),
        ("Hacker News, by the rules", "Submit and comment only. It never votes, and caps each profile at 2 link submissions a day."),
        ("Agents on a leash", "AI agents get the same queue and limits you do. Only approved posts go out."),
    ]
    fl = "".join(f'<li class="fact"><h3 class="h3">{t}</h3><p>{d}</p></li>' for t, d in facts)
    logos = "".join('<li class="logo-slot">Customer logo</li>' for _ in range(5))
    return f'''
<section class="section proof" id="proof" aria-labelledby="proof-title" data-component="proof">
  <div class="wrap">
    <ul class="logos" aria-label="Customer logo placeholders">{logos}</ul>
    <div class="shead">
      <p class="eyebrow">Trust</p>
      <h2 id="proof-title" class="h2">{c.get("proof_title", "Yours to keep. Yours to control.")}</h2>
    </div>
    <div class="proof__grid">
      <figure class="quote">
        <span class="slot-label">Placeholder: customer quote</span>
        <blockquote>"A real customer's words about launch day go here, once we have them on record."</blockquote>
        <figcaption><span class="avatar avatar--ghost">?</span><span><b>Name, title</b><small>Company</small></span></figcaption>
      </figure>
      <ul class="facts">{fl}</ul>
    </div>
  </div>
</section>'''

def pricing(c):
    return f'''
<section class="section pricing" id="pricing" aria-labelledby="pricing-title" data-component="pricing">
  <div class="wrap pricing__card">
    <div>
      <p class="eyebrow">Pricing</p>
      <h2 id="pricing-title" class="h2">Priced per person, not per channel.</h2>
      <p class="lede">One profile covers every network that person posts to. Add as many Macs as you like.</p>
      <p class="slot-label">Draft message, pending pricing decision</p>
    </div>
    <ul class="pricing__list">
      <li><b>Every network</b><span>LinkedIn, X, Reddit, Hacker News, Slack, Bluesky, GitHub reactions</span></li>
      <li><b>Every machine</b><span>Run the queue from each Mac you own, coordinated</span></li>
      <li><b>Every surface</b><span>Desktop app, Python CLI and agent access</span></li>
    </ul>
    <a class="btn btn--ghost" href="#pricing">See pricing</a>
  </div>
</section>'''

def cta(c):
    return f'''
<section class="section cta" id="cta" aria-labelledby="cta-title" data-component="cta">
  <div class="wrap cta__inner">
    <img class="cta__icon" src="{A}/brand/blowhorn-app-icon.svg" alt="" width="72" height="72">
    <h2 id="cta-title" class="h2">{c.get("cta_title", "Own your voice. Keep your accounts.")}</h2>
    <p class="lede">One disk image for Apple silicon and Intel, plus a Chrome extension. About a minute to set up.</p>
    <div class="hero__ctas hero__ctas--center">
      <a class="btn btn--primary btn--pop" href="#cta"><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 4v11m0 0 4.5-4.5M12 15l-4.5-4.5M5 19h14"/></svg>Get Blowhorn for Mac</a>
      <a class="btn btn--ghost" href="#footer">Read the docs</a>
    </div>
  </div>
</section>'''

def footer(c):
    cols = {
        "Product": ["Platforms", "How it works", "Download", "Pricing"],
        "Solutions": ["DevRel", "Marketing managers", "Founders", "Team amplification"],
        "Resources": ["Docs", "Compare", "Major Blowhorn", "Changelog"],
        "Trust": ["Trust Center", "Privacy", "Terms", "Status"],
    }
    cl = "".join(f'<div><p class="eyebrow">{h}</p><ul>' + "".join(f'<li><a href="#top">{i}</a></li>' for i in items) + "</ul></div>" for h, items in cols.items())
    return f'''
<footer class="footer" id="footer" data-component="footer">
  <div class="wrap footer__grid">
    <div class="footer__brand">
      <img class="logo-on-light" src="{A}/brand/blowhorn-lockup-horizontal.svg" alt="Blowhorn" width="140" height="36">
      <img class="logo-on-dark" src="{A}/brand/blowhorn-lockup-horizontal-on-dark.svg" alt="Blowhorn" width="140" height="36">
      <p>Not a bot. You, at full volume.</p>
    </div>
    {cl}
  </div>
  <div class="wrap footer__legal"><span>&copy; 2026 Layer5, Inc.</span><span>Concept mock, not the live site</span></div>
</footer>'''

SECTIONS = dict(platforms=platforms, explorer=explorer, how=how, roles=roles, wave=wave, major=major, proof=proof, pricing=pricing, cta=cta)

def page(c):
    body = nav(c) + "<main>" + hero(c) + "".join(SECTIONS[s](c) for s in c["sections"]) + "</main>" + footer(c)
    links = "\n  ".join(f'<link rel="stylesheet" href="../shared/themes/{t}.css">' for t in THEMES)
    return f'''<!doctype html>
<html lang="en" data-theme="{c["theme"]}">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{esc(c["title"])}</title>
  <meta name="description" content="{esc(c["meta"])}">
  <link rel="icon" href="../assets/brand/blowhorn-icon.svg">
  <link rel="stylesheet" href="../shared/tokens.css">
  <link rel="stylesheet" href="../shared/components.css">
  {links}
</head>
<body>
<a class="skip" href="#hero-title">Skip to content</a>
{body}
<script src="../shared/app.js" defer></script>
</body>
</html>
'''

CONCEPTS = {
    "signal": dict(
        theme="signal",
        title="Blowhorn: not a bot. You, at full volume.",
        meta="Write it once and post to LinkedIn, X, Reddit, Hacker News, Slack and Bluesky as you, from your own Chrome on your own Mac.",
        eyebrow="Blowhorn for macOS",
        headline='Not a bot.<br><span class="accent">You, at full volume.</span>',
        sub="Write the launch post once. Blowhorn sends it to LinkedIn, X, Reddit, Hacker News, Slack and Bluesky as you, from your own Chrome, on the Macs you own.",
        note="As many social profiles as you want. About a minute to set up.",
        cta2="See the 2-minute tour",
        major="locked-hat-feathers-left.png",
        sections=["platforms", "how", "wave", "roles", "major", "proof", "pricing", "cta"],
    ),
    "full-volume": dict(
        theme="full-volume",
        title="Blowhorn: your whole team, at full volume.",
        meta="One message, many real voices. Blowhorn helps teams say it once and post everywhere, each person as themselves.",
        eyebrow="Social amplification for teams",
        headline='Real voices<br>make a <span class="accent">sound wave.</span>',
        sub="One message, posted everywhere by the people behind it. Each teammate amplifies from their own Chrome, as themselves, at the minute you pick. No bot to invite.",
        note="For DevRel, marketing, founders and the people who rally a team.",
        cta2="See a launch, start to finish",
        major_float=None,
        hero_extra=f'<div class="hero__band" aria-hidden="true"><img src="{A}/major/locked-hat-right.png" alt=""></div>',
        major="locked-medals-left.png",
        roles_title="Four roles. One queue.",
        proof_title="Loud, not reckless.",
        cta_title="Sound off.",
        sections=["platforms", "wave", "how", "roles", "proof", "major", "pricing", "cta"],
    ),
    "open-field": dict(
        theme="open-field",
        title="Blowhorn: own your voice, keep your accounts.",
        meta="The social console that runs in your own Chrome. Try it: write one announcement and see it on every network.",
        eyebrow="Runs in your own Chrome",
        headline='Own your voice.<br><span class="accent">Keep your accounts.</span>',
        sub="LinkedIn, X, Reddit, Hacker News, Bluesky and Slack from one queue, posted as you. Write once below and see how it lands everywhere.",
        note="Mac app, Python CLI and Chrome extension. Sign in with Blowhorn Cloud.",
        cta2="Try it below",
        major="locked-plain-left.png",
        major_float="cutout-hat-feathers-left.png",
        hero_explorer=True,
        cta_title="Your next launch, everywhere at once.",
        sections=["platforms", "how", "roles", "wave", "proof", "major", "pricing", "cta"],
    ),
}

if __name__ == "__main__":
    for name, c in CONCEPTS.items():
        d = ROOT / name
        d.mkdir(exist_ok=True)
        (d / "index.html").write_text(page(c))
        print("built", d / "index.html")
