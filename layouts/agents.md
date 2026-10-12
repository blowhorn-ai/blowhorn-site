# {{ .Title }}

> {{ .Params.lead }}

{{ .Description }}
{{ range .Pages.ByWeight }}
- [{{ .Params.tool }}]({{ .Permalink }}): {{ .Params.hook }}
{{- end }}
{{ range .Params.pillars }}
- **{{ .t }}**: {{ .b }}
{{- end }}
