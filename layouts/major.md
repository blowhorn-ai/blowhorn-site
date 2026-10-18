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

## The portrait gallery

Oil paintings of the Major and his squad:

- Giving orders. He is always giving orders: {{ printf "assets/brand/mascot/lore/major-oil-locked6.webp" | absURL }}
- The General. Calm, few words, never a bullhorn: {{ printf "assets/brand/mascot/lore/general-oil-locked6.webp" | absURL }}
- Keyboard Warrior, on patrol: {{ printf "assets/brand/mascot/lore/keyboard-warrior-oil-locked6.webp" | absURL }}
- Robo-Recruit. Has not blinked since reveille: {{ printf "assets/brand/mascot/lore/robo-recruit-oil-locked6.webp" | absURL }}
- Night shift at the terminal: {{ printf "assets/brand/mascot/lore/scene-terminal-oil-locked6.webp" | absURL }}
- Briefing in the command tent. Major has the floor. Major always has the floor: {{ printf "assets/brand/mascot/lore/scene-command-tent-oil-locked6.webp" | absURL }}

## Dispatches from the barracks
{{ range sort .Params.dispatches "date" "desc" }}
### {{ (time.AsTime .date).Format "2006-01-02" }}: {{ .title }}

{{ .body }}
{{ end }}
