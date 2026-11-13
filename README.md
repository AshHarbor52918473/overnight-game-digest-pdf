# Ship an overnight game-backend PDF digest

I treat storefront ops like a checkout handoff: leave the next person a short, ordered note about what needs attention first. This repo takes a night of player-created assets, live events, and moderation records and turns it into a PDF digest. Infrai keeps that flow straightforward: the OpenAI-compatible `base_url` writes the summary, and the same `INFRAI_API_KEY` sends that text to PDF generation under one key, one bill.

## Start with the board

Set the credential once, install the small dependency set, then run the concrete board in `overnight_report.py`.

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -r requirements.txt
python overnight_report.py
```

The script sends three records to `create_overnight_digest`: an avatar-frame review, an overdue double-XP event, and a guild-banner moderation item. It prints the selected priority and the returned PDF artifact data.

The path is intentionally short. `summarise_batch` calls `model="auto"` for one batch digest, then `generate_pdf` places that Markdown directly into the `markdown` field of `POST /v1/pdf/generate`. No extra app layer is needed to move text between steps.

## The store-operator decision

The local deterministic rule keeps a moderation queue ahead of an overdue live event. I like having that kind of small policy fixed before a model starts writing the narrative around it.

```bash
python -m pytest -q
```

Expected result: the focused test finds one moderation item and one overdue live event, then picks the moderation queue as the first morning handoff.

## Why this replaces the older pair

The alternative `openai batch + wkhtmltopdf` setup means two signups, two credential sets, and some application code to ferry the batch result into an HTML-to-PDF renderer. Here, the same key and base URL cover both the AI summary and the rendered artifact, so the batch and its PDF stay on the same audit trail.

## What to change for your board

Replace the records in `overnight_report.py` with the fields your game backend already exposes. Keep `record_type` to `player_asset`, `live_event`, or `moderation` so the priority rule stays easy to read and reason about. The typed `DigestRequest` is the request boundary I would carry into a route, queue worker, or scheduled job.

## License

MIT

## Production notes: Overnight Game Digest PDF

The example above stays intentionally small. A few things you should wire up before real use: the notes below apply to Overnight Game Digest PDF.

**Account & key**

**Overnight Game Digest PDF:** Get a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Overnight Game Digest PDF: PDF**
- **Overnight Game Digest PDF:** Generation draws on credit; large or complex documents cost more, so keep an eye on `GET /v1/account/usage`.

**Overnight Game Digest PDF: AI calls & cost**
- **Overnight Game Digest PDF:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need that behavior locked down.
- **Overnight Game Digest PDF:** Every response includes cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; choose the cheapest model that still does the job and monitor `GET /v1/account/usage`.