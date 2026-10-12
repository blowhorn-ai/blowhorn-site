# {{ .Title }}

> {{ .Params.lead }}

## How it works

1. Install Blowhorn for Mac and the Blowhorn Chrome extension.
2. {{ .Params.wire_title }}: {{ .Params.wire_body }}
3. Say what you want. {{ .Params.tool }} turns it into blowhorn commands, and you approve what publishes.

`{{ .Params.wire_file }}`

```
{{ .Params.wire_code }}
```
{{ with .Params.extra_file }}
`{{ . }}`

```
{{ $.Params.extra_code }}
```
{{ end }}
{{- with .Params.prompts }}
## Try saying
{{ range . }}
- "{{ . }}"
{{- end }}
{{ end }}
## Commands

```
{{ .Params.commands }}
```

## Where it pays off
{{ range .Params.uses }}
- **{{ .t }}**: {{ .b }}
{{- end }}

## Questions
{{ range .Params.faq }}
**{{ .q }}** {{ .a }}
{{ end }}
