# {{ .Params.lead }}
{{ with .Params.status }}
Status: {{ . }}
{{ end }}
{{ .Params.intro | default .Description }}
{{ range .Params.code }}
```{{ .lang | default "bash" }}
{{ .code }}```
{{ end }}{{ with .Params.code_note }}{{ . }}
{{ end }}{{ with .Params.ways }}
## {{ $.Params.ways_title }}
{{ range . }}
- [{{ .t }}]({{ (site.GetPage .path).Permalink }}) ({{ .status }}): {{ .b }}
{{- end }}
{{ end }}{{ with .Params.cards }}
## {{ $.Params.cards_title }}
{{ range . }}
- **{{ .t }}.** {{ .b }}
{{- end }}
{{ end }}{{ with .Params.rules }}
## {{ $.Params.rules_title }}
{{ range . }}
- **{{ .t }}.** {{ .b }}
{{- end }}
{{ end }}
