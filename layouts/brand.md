# {{ .Title }}

> {{ .Params.lead }}

Download the brand kit: [{{ .Params.kit.url | absURL }}]({{ .Params.kit.url | absURL }}) (ZIP, {{ .Params.kit.size }}): the logo, wordmark, lockups and Major Blowhorn in SVG and PNG, light and dark, the colors and a PDF of the guidelines.

## Logo

The Crowhorn: a megaphone that is also a rooster. Use the horizontal lockup unless the space says otherwise, and pick the file drawn for the ground it sits on.
{{ range (.Params.lockups | append .Params.marks | append .Params.wordmarks) }}
- [{{ .name }}]({{ printf "assets/brand/logo/%s" .file | absURL }}){{ with .note }}: {{ . }}{{ end }}
{{- end }}

## Clear space and minimum size

- Clear space: half the icon's height on every side.
- Minimum sizes: horizontal lockup 96 px wide, stacked lockup 64 px, icon 24 px. Below that, use the favicons.

## Color
{{ range hugo.Data.brand_colors.groups }}
### {{ .name }}
{{ range .colors }}
- {{ .name }}: {{ .hex }}, rgb({{ delimit .rgb ", " }}). {{ .use }}
{{- end }}
{{ end }}
## Type
{{ range .Params.fonts }}
- {{ .family }} ({{ .role }}): {{ .weights }}. {{ .url }}
{{- end }}

## Major Blowhorn

The mascot. Put him on white, light teal or cream, one appearance per page, and keep him off security, billing and legal pages.

## Usage

Do: full color on light grounds; the on-dark file on dark grounds; one color on teal and busy grounds.

Don't: recolor, stretch, squash or rotate the logo; add shadows, glows or gradients; set it on a busy ground; put the full-color icon on teal; retype the wordmark in a font; rearrange the parts; use retired marks or old names.

The name is Blowhorn: one word, capital B. In formal copy, Layer5 Blowhorn the first time, then Blowhorn.
