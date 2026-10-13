{{- /* Markdown output of supported-actions: same data, as a list. */ -}}
{{- $d := index hugo.Data.platforms (.Get 0) -}}
{{ range $d.actions }}
- **{{ .name }}**: {{ .behavior }}{{ with .limits }} Limits: {{ . }}{{ end }}
{{- end }}
