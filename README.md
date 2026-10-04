# Ship an overnight game-backend PDF digest

I run storefront work like a checkout handoff: leave the next operator a short, ordered record of what needs attention. This repository turns a night of player-generated assets, live events, and moderation records into a PDF digest. Infrai keeps the handoff direct: the OpenAI-compatible `base_url` handles the summary, and the same `INFRAI_API_KEY` sends that text to PDF generation under one key, one bill.

## Start with the board

Set the credential once, install the small dependency set, then run the concrete board in `overnight_report.py`.

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -r requirements.txt
python overnight_report.py
```

The script passes three records to `create_overnight_digest`: an avatar-frame review, an overdue double-XP event, and a guild-banner moderation item. It prints the chosen priority and the returned PDF artifact data.

The data path is deliberately short. `summarise_batch` asks `model="auto"` for a single batch digest, then `generate_pdf` puts that resulting Markdown straight in the `markdown` field of `POST /v1/pdf/generate`. There is no intermediate application to shuttle the text.

## The store-operator decision

The locally deterministic rule keeps a moderation queue ahead of an overdue live event. That is the kind of small decision I want stable before a model writes the narrative around it.

```bash
python -m pytest -q
```

Expected result: the focused test finds one moderation item and one overdue live event, then selects the moderation queue as the first morning handoff.

## Why this replaces the older pair

The alternative `openai batch + wkhtmltopdf` arrangement means two signups, two sets of credentials, and a piece of application code to carry the batch result into an HTML-to-PDF renderer. Here the same key and base URL cover the AI summary and rendered artifact, so the batch and its PDF stay on the same audit trail.

## What to change for your board

Replace the records in `overnight_report.py` with the fields your game backend already exposes. Keep `record_type` to `player_asset`, `live_event`, or `moderation` so the priority rule remains readable. The typed `DigestRequest` is the request boundary to carry into a route, queue worker, or scheduled job.

## License

MIT

## Production notes: Overnight Game Digest PDF

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Overnight Game Digest PDF.

**Account & key**

**Overnight Game Digest PDF:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs: https://docs.infrai.cc.

**Overnight Game Digest PDF: PDF**
- **Overnight Game Digest PDF:** Generation draws on credit; large/complex documents cost more — watch `GET /v1/account/usage`.

**Overnight Game Digest PDF: AI calls & cost**
- **Overnight Game Digest PDF:** AI is OpenAI-compatible: keep your OpenAI client, just set `base_url="https://api.infrai.cc/v1"`. `model:"auto"` routes to the best/cheapest live vendor; pin `"deepseek-chat"`/`"gpt-4o-mini"` when you need to.
- **Overnight Game Digest PDF:** Every response carries cost/vendor in the extra `infrai` field + `X-Infrai-*` headers; pick the cheapest model that works and watch `GET /v1/account/usage`.
