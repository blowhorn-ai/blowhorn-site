# {{ .Params.heading | default .Title }}
{{ with .Params.notice }}
> {{ . }}
{{ end }}
> {{ .Params.lead }}
{{ with .Params.matrix }}{{ $acts := $.Params.actions }}
| Platform |{{ range $acts }} {{ .name }} |{{ end }}
| --- |{{ range $acts }} --- |{{ end }}
{{ range . }}{{ $row := . }}| {{ .platform }} |{{ range $acts }}{{ with index $row .key }} {{ .risk }}{{ with .text }}: {{ . }}{{ end }} |{{ else }} none |{{ end }}{{ end }}
{{ end }}{{ end }}
{{ .RenderShortcodes }}
