{{- $mx := partialCached "action-matrix.html" . "action-matrix" -}}
{{- $copy := $mx.copy -}}
{{- $counts := partial "platform-counts.html" . -}}
# {{ $copy.headline }}

> {{ $copy.lede }}

{{ printf $copy.tally $counts.activities $counts.platforms $counts.comingSoon }}
{{ range $mx.groups }}
## {{ .name }}

{{ .summary }}
{{ range .actions }}
- **{{ .name }}**: {{ $links := slice }}{{ range where .cells "status" "supported" }}{{ $links = $links | append (printf "[%s](%s)" .platformName .href) }}{{ end }}{{ delimit $links ", " }}
{{- end }}
{{ end }}
[{{ $copy.docsCta }}]({{ $copy.docsPath }})
