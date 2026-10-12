# {{ .Title }}

> {{ .Params.lead }}

By group, because products within a group differ. Checked against vendor pages in October 2026.

{{ $groups := .Params.groups -}}
| Feature | Blowhorn |{{ range $groups }} {{ .name }} ({{ .examples }}) |{{ end }}
| --- | --- |{{ range $groups }} --- |{{ end }}
{{ range .Params.rows }}{{ $row := . }}| {{ .feature }} | {{ .blowhorn.text }} |{{ range $groups }} {{ (index $row .key).text }} |{{ end }}
{{ end }}
## Why it matters
{{ range .Params.why }}
- **{{ .title }}.** {{ .body }} [Details]({{ .link | absURL }})
{{- end }}

## Credit where due
{{ range .Params.fair }}
- {{ . }}
{{- end }}
