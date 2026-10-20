{{- /* Markdown output of supported-actions: same data, as a list. */ -}}
{{- $d := index hugo.Data.platforms (.Get 0) -}}
{{ range $d.actions }}
{{- $a := partial "action-resolve.html" . }}
- **{{ $a.name }}**: {{ $a.description }}{{ with $a.limits }} Limits: {{ . }}{{ end }} ([example]({{ printf "#%s" $a.slug }}))
{{- end }}
