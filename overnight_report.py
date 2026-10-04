"""Run a concrete overnight board through the digest workflow."""

from game_digest import BacklogRecord, DigestRequest, create_overnight_digest


def main() -> None:
    request = DigestRequest(
        store_name="Arcade Pass Storefront",
        records=[
            BacklogRecord("player_asset", "Neon avatar frame", "review", "Mina", 8),
            BacklogRecord("live_event", "Weekend double XP", "active", "Noah", 30),
            BacklogRecord("moderation", "Guild banner report", "pending", "Iris", 3),
        ],
    )
    result = create_overnight_digest(request)
    print(result["decision"]["priority_note"])
    print(result["artifact"])


if __name__ == "__main__":
    main()
