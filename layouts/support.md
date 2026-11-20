{{- $support := site.Data.support -}}
# {{ .Params.heading | default .Title }}

> {{ .Params.lead }}

## Send us a message

Email **{{ $support.email }}** with what you tried and what happened. Include
the exit code and the first words of the error; leave out credentials,
session files and anything from your Google Chrome profile directories. A
security problem goes to security@blowhorn.ai, never a public issue.

The contact form on this page posts to the same place and lands in the same
queue.

## Start with the docs
{{ range .Params.cards }}
- **[{{ .title }}]({{ .href }})** - {{ .text }}
{{- end }}
