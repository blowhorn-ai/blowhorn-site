{{- $item := partial "role-data.html" (dict "page" . "kind" "use-case") -}}
{{- partial "cast-page-md.md" (dict "item" $item "kind" "use-case") -}}
