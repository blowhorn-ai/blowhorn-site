{{- /* Markdown output for a role or use-case page. Kind selects the gets
  section title through cast-kind.html. */ -}}
{{- $item := .item -}}
{{- $meta := partial "cast-kind.html" (dict "kind" .kind "name" $item.name) -}}
# {{ $item.headline }}

> {{ $item.lead }}

## Sound familiar?
{{ range $item.pains }}
- **{{ .t }}.** {{ .b }}
{{- end }}

## {{ $meta.getsTitle }}
{{ range $item.gets }}
- **{{ .t }}.** {{ .b }}
{{- end }}
{{ with $item.prompt }}
## Or tell your agent

"{{ . }}"
{{ end }}
## Frequently Asked Questions
{{ range $item.faq }}
**{{ .q }}** {{ .a }}{{ with .link }} [{{ .label }}]({{ .href }}){{ end }}
{{ end }}
