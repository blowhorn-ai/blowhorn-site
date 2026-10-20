{{- if not .Parent }}{{ errorf "tab: must be nested in tabs" }}{{ end -}}
{{- $id := .Get "id" | default (.Get "name" | urlize) -}}
{{- $name := .Get "name" | default $id -}}
{{- $panes := .Parent.Scratch.Get "tab-panes" | default slice -}}
{{- .Parent.Scratch.Set "tab-panes" ($panes | append (dict "id" $id "name" $name "inner" .Inner)) -}}
