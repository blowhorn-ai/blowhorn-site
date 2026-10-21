{{- $item := partial "role-data.html" (dict "page" . "kind" "role") -}}
{{- partial "cast-page-md.md" (dict "item" $item "kind" "role") -}}
