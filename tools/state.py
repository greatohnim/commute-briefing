import json
import sys
from datetime import date, timedelta


def _yesterday(today):
    y = date.fromisoformat(today) - timedelta(days=1)
    return y.isoformat()


def update_state(state, today):
    s = dict(state)
    s.setdefault("history", [])

    if s.get("last_episode_date") == today:
        return s  # 같은 날 재실행 — 멱등

    if s.get("last_episode_date") == _yesterday(today):
        s["streak"] = s.get("streak", 0) + 1
    else:
        s["streak"] = 1

    s["total_episodes"] = s.get("total_episodes", 0) + 1
    s["episode"] = s["total_episodes"]
    s["last_episode_date"] = today
    s["history"] = s["history"] + [
        {"date": today, "episode": s["episode"], "streak": s["streak"]}
    ]
    return s


def main():
    """CLI: python -m tools.state <state.json> <today>"""
    path, today = sys.argv[1], sys.argv[2]
    with open(path, "r", encoding="utf-8") as f:
        state = json.load(f)
    new = update_state(state, today)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(new, f, ensure_ascii=False, indent=2)
    print(f"[state] streak={new['streak']} episode={new['episode']}")


if __name__ == "__main__":
    main()
