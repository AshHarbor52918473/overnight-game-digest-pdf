from game_digest import BacklogRecord, decide_priority


def test_moderation_queue_precedes_an_overdue_event() -> None:
    records = [
        BacklogRecord("live_event", "Weekend double XP", "active", "Noah", 28),
        BacklogRecord("moderation", "Guild banner report", "pending", "Iris", 2),
    ]

    decision = decide_priority(records)

    assert decision.moderation_count == 1
    assert decision.overdue_live_events == 1
    assert decision.priority_note == "Review the moderation queue before publishing the live-event recap."
