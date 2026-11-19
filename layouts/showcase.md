# {{ .Title }}

> {{ .Params.lead }}

## What it is

Blowhorn is a desktop app with a small browser extension. You write a post once, queue it, and Blowhorn sends it from your own computer, through your Chrome profiles, at a pace you choose. Nothing posts from a vendor server.

## Four formations

{{ $mrot := partial "machines-rotation.html" . -}}
{{- $names := dict "muster" "Muster" "battalion-map" "Battalion Map" "one-thunder" "One Thunder" "call-to-arms" "Call to Arms" -}}
{{- range $v := $mrot.variants }}
### {{ index $names $v.id }}

{{ $v.headline }} {{ $v.subhead }}
{{ end }}
## What it does

{{ range .Params.features }}
- **{{ .title }}.** {{ .body }}
{{- end }}

## Where it works

{{- $named := slice -}}
{{- range site.Data.integrations.platforms }}
  {{- if eq .status "supported" }}{{ $named = $named | append (partial "integration-row.html" .).name }}{{ end }}
{{- end }}
Supported now: {{ delimit $named ", " }}. Coming soon: YouTube, Instagram, TikTok and Facebook.

## See the code

Blowhorn is open source: [Blowhorn on GitHub](https://github.com/blowhorn-ai). [How Blowhorn compares]({{ (site.GetPage "/compare").RelPermalink }})
