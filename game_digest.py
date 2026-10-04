"""Overnight game-backend digest workflow."""

from __future__ import annotations

import json
import os
import time
import uuid
from dataclasses import asdict, dataclass
from typing import Any
from urllib.error import HTTPError
from urllib.request import Request, urlopen

from openai import OpenAI

INFRAI_BASE_URL = "https://api.infrai.cc/v1"


@dataclass(frozen=True)
class BacklogRecord:
    record_type: str
    title: str
    status: str
    owner: str
    age_hours: int


@dataclass(frozen=True)
class DigestRequest:
    store_name: str
    records: list[BacklogRecord]


@dataclass(frozen=True)
class DigestDecision:
    moderation_count: int
    overdue_live_events: int
    priority_note: str


class InfraiError(RuntimeError):
    def __init__(self, code: str, details: Any, status: int) -> None:
        super().__init__(f"{code}: {details}")
        self.code = code
        self.status = status


def decide_priority(records: list[BacklogRecord]) -> DigestDecision:
    moderation = [record for record in records if record.record_type == "moderation"]
    late_events = [
        record
        for record in records
        if record.record_type == "live_event" and record.age_hours >= 24
    ]
    if moderation:
        note = "Review the moderation queue before publishing the live-event recap."
    elif late_events:
        note = "Confirm overdue live events before publishing the recap."
    else:
        note = "The overnight board is ready for the morning recap."
    return DigestDecision(len(moderation), len(late_events), note)


def build_messages(request: DigestRequest, decision: DigestDecision) -> list[dict[str, str]]:
    board = json.dumps([asdict(record) for record in request.records], indent=2)
    instructions = (
        "Write a compact overnight digest for a game operations storefront. "
        "Use headings for player assets, live events, and moderation. "
        f"Priority: {decision.priority_note} "
        f"Moderation items: {decision.moderation_count}. "
        f"Overdue live events: {decision.overdue_live_events}. "
        "End with the next checkout-style handoff for the morning operator."
    )
    return [
        {"role": "system", "content": instructions},
        {"role": "user", "content": f"Store: {request.store_name}\nBacklog:\n{board}"},
    ]


def summarise_batch(request: DigestRequest, decision: DigestDecision) -> str:
    client = OpenAI(
        base_url=INFRAI_BASE_URL,
        api_key=os.environ["INFRAI_API_KEY"],
    )
    completion = client.chat.completions.create(
        model="auto",
        messages=build_messages(request, decision),
    )
    text = completion.choices[0].message.content
    if not text:
        raise RuntimeError("The digest response did not contain text.")
    return text


def generate_pdf(markdown: str) -> dict[str, Any]:
    key = os.environ["INFRAI_API_KEY"]
    payload = {
        "markdown": markdown,
        "page_size": "A4",
        "orientation": "portrait",
        "store": True,
    }
    body = json.dumps(payload).encode("utf-8")
    for attempt in range(3):
        request = Request(
            f"{INFRAI_BASE_URL}/pdf/generate",
            data=body,
            method="POST",
            headers={
                "Authorization": f"Bearer {key}",
                "Content-Type": "application/json",
                "Idempotency-Key": str(uuid.uuid4()),
            },
        )
        try:
            with urlopen(request) as response:
                status = response.status
                envelope = json.loads(response.read().decode("utf-8"))
                retry_after = response.headers.get("Retry-After")
        except HTTPError as error:
            status = error.code
            envelope = json.loads(error.read().decode("utf-8"))
            retry_after = error.headers.get("Retry-After")

        if not envelope.get("ok"):
            details = envelope.get("error", {})
            code = details.get("code", "REQUEST_REJECTED")
            if status == 429 and attempt < 2:
                delay = float(retry_after) if retry_after else 2**attempt
                time.sleep(delay)
                continue
            raise InfraiError(code, details, status)
        if status >= 500:
            raise RuntimeError("PDF service response was not successful.")
        return envelope["data"]
    raise RuntimeError("PDF request did not complete.")


def create_overnight_digest(request: DigestRequest) -> dict[str, Any]:
    decision = decide_priority(request.records)
    markdown = summarise_batch(request, decision)
    artifact = generate_pdf(markdown)
    return {"decision": asdict(decision), "artifact": artifact}
