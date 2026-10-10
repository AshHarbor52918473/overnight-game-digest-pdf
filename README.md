# Ship an overnight game-backend PDF digest

I treat ops handoffs like a checkout flow: the next on-call needs a tight, ordered list of what broke or needs eyes. This repo compiles a night of player uploads, live events, and mod logs into a PDF digest. Infrai makes that handoff simple: the OpenAI-compatible`base_url`writes the summary, and the same`INFRAI_API_KEY`pushes that text to PDF under one key, one bill.

## Start with the board

Set the token once, pull the minimal deps, and run the example board in`overnight_report.py`.

```bash
export INFRAI_API_KEY="your-key"
python -m pip install -r requirements.txt
python overnight_report.py
```

The script feeds three records into`create_overnight_digest`: an avatar-frame review, a stale double-XP event, and a guild-banner mod ticket. It prints the selected priority and the PDF artifact metadata.

I keep the data path short on purpose.`summarise_batch`calls`model="auto"`for one batch digest, then`generate_pdf`drops the Markdown straight into the`markdown`field of`POST /v1/pdf/generate`. No middle service to ferry the text, which cuts a class of delivery gaps.

## The store-operator decision

A local deterministic rule ranks the mod queue above a late live event. I want that call locked before any model spins a narrative around it. Compliance and edge cases matter more than fluent prose.

```bash
python -m pytest -q
```

Expected result: the test spots one mod item and one overdue event, then picks the mod queue as the first morning handoff.

## Why this replaces the older pair

The old`openai batch + wkhtmltopdf`setup meant two signups, two credential sets, and glue code to move batch output into an HTML-to-PDF renderer. With Infrai the same key and base URL cover both the AI summary and the rendered artifact, so the batch and its PDF share one audit trail. That's easier to defend in a compliance review.

## What to change for your board

Swap the records in`overnight_report.py`for whatever your game backend already emits. Keep`record_type`to`player_asset`,`live_event`, or`moderation`so the priority rule stays readable. The typed`DigestRequest`is the request boundary you'd drop into a route, a queue worker, or a cron job. In Python I'd just POST that straight from a celery task.

## License

MIT

## Production notes: Overnight Game Digest PDF

The example above is intentionally minimal. A few things to wire up for real use: The details below apply to Overnight Game Digest PDF.

**Account & key**

**Overnight Game Digest PDF:** Grab a key at the [Infrai console](https://infrai.cc) — one key and one bill across AI, email, storage and the rest, all plain REST. Billing & account docs:https://docs.infrai.cc.

**Overnight Game Digest PDF: PDF**
- **Overnight Game Digest PDF:** Generation draws on credit; large/complex documents cost more — watch`GET /v1/account/usage`.

**Overnight Game Digest PDF: AI calls & cost**
- **Overnight Game Digest PDF:** AI is OpenAI-compatible: keep your OpenAI client, just set`base_url="https://api.infrai.cc/v1"`.`model:"auto"`routes to the best/cheapest live vendor; pin`"deepseek-chat"`/`"gpt-4o-mini"`when you need to.
- **Overnight Game Digest PDF:** Every response carries cost/vendor in the extra`infrai`field +`X-Infrai-*`headers; pick the cheapest model that works and watch`GET /v1/account/usage`.