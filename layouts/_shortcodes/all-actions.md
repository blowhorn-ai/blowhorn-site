{{- /* Markdown output of all-actions: same rows as the HTML table. */ -}}
{{- $mx := partialCached "action-matrix.html" .Page "action-matrix" }}
| Action | Platform | What it does |
| --- | --- | --- |
{{- range $mx.supportedRows }}
| [{{ .actionName }}]({{ .href }}) | {{ .platformName }} | {{ replace .note "|" "\\|" }}{{ with .limits }} {{ replace . "|" "\\|" }}{{ end }} |
{{- end }}
