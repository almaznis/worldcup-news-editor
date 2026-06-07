# WorldCupNewsAgent — Persistent Rules

## Portal
**Sport Arena Hub** — Футбол.kz (Russian-language football news)

## Article Generation

### Language
All article content, titles, excerpts, and tags must be in **Russian**.

### Article Types
Allowed `type` values: `transfer`, `match_report`, `preview`, `ranking`
(do NOT use `profile`)

### Categories
Use: "ЧМ-2026", "Трансферы", "Сборные", "Отчёты о матчах", "Новости игроков", "Аналитика", "Тренды"

### Article Archive
Save each article locally to `./articles/{src}-{slug}/{src}-{slug}.md`

### Logging
- Append each published article to `./logs/articles-history.jsonl`
- Write latest run summary to `./logs/last-run.json`

---

## Images

### Rule: Portrait / Face-Cropped Only
- Always use **portrait or face-cropped** images (head + shoulders, not full-body or team shots).
- Source from **Wikimedia Commons** using CC-licensed files (CC BY, CC BY-SA, CC0, or Public Domain).
- Preferred file size: **under 1.1 MB** before base64 encoding.
- Search pattern: `"{Player Name} (cropped).jpg"` or `"{Player Name} portrait"` on Wikimedia Commons.

### Rule: Upload via image_base64
- **Always upload images via the `image_base64` field** (downloads image → base64-encodes → sends in payload).
- The Edge Function automatically stores the image in the Supabase `images` bucket.
- Only fall back to `image_url` when the image is an SVG (cannot be base64-embedded as a raster image) or when all download attempts fail after retries.

### Wikimedia Rate Limits
- Add a 3–4 second delay between each image download to avoid HTTP 429.
- If a URL returns 429, search for an alternate portrait of the same subject with a different file path.
- Never skip the image entirely without at least 2 retry attempts with different URLs.

---

## YouTube Videos

### Rule: Russian Language Only
- Always embed **Russian-language YouTube videos** (commentary, reviews, previews in Russian).
- Preferred channels: Чемпионат, Sports.ru, Match TV, GOAL24, Football Star, РФС ТВ, official league/club Russian channels.
- Do **not** use English-language YouTube videos even if the match footage is more complete.

### Search Strategy
- Use Russian-language queries: `"{Команда А} {Команда Б} обзор матча"`, `"{Игрок} ЧМ 2026 превью"`, `"Группа X ЧМ-2026"`.
- Verify the video title is in Russian (Cyrillic) before using its ID.

### Embed Format
```markdown
## Видео по теме

[![{Russian label}](https://img.youtube.com/vi/{VIDEO_ID}/hqdefault.jpg)](https://www.youtube.com/watch?v={VIDEO_ID})

[Смотреть на YouTube →](https://www.youtube.com/watch?v={VIDEO_ID})
```

---

## Publishing Endpoint

- **URL:** `https://jcezmolckegxlvizvmtj.supabase.co/functions/v1/publish-articles`
- **Method:** POST only (PATCH/PUT → 405)
- **Auth:** `x-agent-secret: $AGENT_PUBLISH_SECRET`
- **Slug collisions:** Endpoint appends `-2`, `-3`, etc. automatically — this is expected behaviour.

---

## Fact-Checking
- Never fabricate match scores, goal scorers, or injury diagnoses.
- Cross-reference with at least 2 sources (ESPN, BBC Sport, AS.com, Championat.com, Sports.ru).
- If a source cannot be verified, state that the information is unconfirmed.
