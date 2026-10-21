{{- /* Markdown output for a role or use-case index.
  .kind (role | use-case) selects labelPrefix from cast-kind.html. */ -}}
{{- $meta := partial "cast-kind.html" (dict "kind" .kind) -}}
{{- $prefix := $meta.labelPrefix -}}
# {{ .page.Title }}

> {{ .page.Params.lead }}
{{ range .page.Pages.ByWeight }}{{ $item := partial "role-data.html" (dict "page" . "kind" $meta.kind) }}
- [{{ $prefix }}{{ $item.name }}: {{ $item.headline }}]({{ .Permalink }})
{{- end }}
