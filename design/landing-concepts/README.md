# Blowhorn landing concepts (design showcase, not shipped)

- `signal/`, `full-volume/`, `open-field/`: one `index.html` per concept, plus its PNG renders. Open the file in a browser. The whole `landing-concepts/` folder must stay together, because pages load `../shared` and `../assets`.
- `shared/tokens.css`: three layers. Brand primitives come from leecalcote/blowhorn `marketing/brand/tokens.json` v1, Figma desktop variables from node 56:21, and semantic page tokens sit on top.
- `shared/components.css`: every section component (nav, hero, app mock, platforms, explorer, how, wave, roles, major, proof, pricing, cta, footer). Components read semantic tokens only.
- `shared/themes/*.css`: the swappable look. Each file is scoped by `html[data-theme]`. Add `?theme=signal|full-volume|open-field` to any page to restyle it, for example `shared/theme-swap-*.png`.
- `shared/build.py`: renders every page from the same components with per-page copy and section order. To spin up a persona or solution page, add a config entry and run `python3 shared/build.py`.
- `shared/app.js`: theme preview, reveal on scroll, the app mock's delivery run, the repost wave and the compose explorer.
- `figma/`: screenshots of the Blowhorn Figma nodes the concepts draw from (node id in each file name).
- `assets/`: only the brand art, cast, Major Blowhorn, platform marks and fonts the pages load. The fonts are SIL Open Font License 1.1 (`assets/fonts/OFL.txt`), the same files as `static/assets/brand/fonts/`. Brand art is copyright Layer5, Inc.; see `static/assets/brand/LICENSES.md`.
- PNG renders: the fold (1440x900) of every concept and the full 1440 page of Signal.

This folder is design source for the Signal homepage work. It is not part of the Hugo build.
