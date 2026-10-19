# {{ .Title }}

> {{ .Params.lead }}

## Service record
{{ range .Params.dossier }}
- {{ .k }}: {{ .v }}
{{- end }}

## The Blowhard incident

Young Private Blowhorn was told to whisper "lights out" to one barracks. He whispered into the camp megaphone and four counties went to bed. He was made Major on the spot, and the troops started calling him Major Blowhard. Not to his face.

## Old Thunderlung

His horn: a dented brass trumpet with a red tassel and one sticky valve, found in the henhouse rafters. "Is not instrument. Is colleague."

## Meet the troops
{{ range .Params.troops }}
### {{ .name }}

{{ .tag }}.

{{ .v }}
{{ range .links }}
- [{{ .t }}]({{ .u | absURL }})
{{- end }}
{{ end }}

## Dispatches from the barracks
{{ range sort .Params.dispatches "date" "desc" }}
### {{ (time.AsTime .date).Format "2006-01-02" }}: {{ .title }}

{{ .body }}
{{ end }}
