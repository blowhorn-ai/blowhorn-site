{{- $platform := .Get "platform" | default (.Get 0) -}}
{{- $action := .Get "action" -}}
{{- $yaml := index hugo.Data.platforms $platform -}}
{{- $want := cond $action (slice $action) slice -}}
{{- if not $action -}}
  {{- range $yaml.actions }}{{ $want = $want | append .id }}{{ end -}}
{{- end -}}
{{- range $want }}
{{- $id := . -}}
{{- $resolved := partial "action-resolve.html" (dict "id" $id) -}}
{{- $ex := false -}}
{{- range site.Data.action_examples.examples -}}
  {{- if and (eq .platform $platform) (eq .action $id) }}{{ $ex = . }}{{ end -}}
{{- end }}
### {{ $resolved.name }}

{{- with $ex.surfaces.cli }}
{{- if eq .status "available" }}

```bash
{{ .command }}
```
{{ with .notes }}{{ . }}{{ end }}
{{- else }}

{{ .notes | default "No CLI command for this action." }}
{{- end }}
{{- end }}
{{ end -}}
