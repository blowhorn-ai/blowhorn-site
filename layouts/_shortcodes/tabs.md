{{- /* Markdown output of tabs: every pane, stacked, with its name. */ -}}
{{- .Scratch.Set "tab-panes" slice -}}
{{- $inner := .Inner -}}
{{- range .Scratch.Get "tab-panes" }}
### {{ .name }}

{{ .inner | strings.TrimSpace }}
{{ end -}}
