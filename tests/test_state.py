from tools.state import update_state


def base():
    return {"streak": 0, "last_episode_date": None, "total_episodes": 0, "history": []}


def test_first_episode_sets_streak_1():
    s = update_state(base(), "2026-07-09")
    assert s["streak"] == 1
    assert s["total_episodes"] == 1
    assert s["episode"] == 1
    assert s["last_episode_date"] == "2026-07-09"
    assert s["history"][-1] == {"date": "2026-07-09", "episode": 1, "streak": 1}


def test_consecutive_day_increments_streak():
    s = update_state(base(), "2026-07-09")
    s = update_state(s, "2026-07-10")
    assert s["streak"] == 2
    assert s["total_episodes"] == 2


def test_gap_resets_streak():
    s = update_state(base(), "2026-07-09")
    s = update_state(s, "2026-07-12")   # 이틀 이상 공백
    assert s["streak"] == 1
    assert s["total_episodes"] == 2


def test_same_day_rerun_is_idempotent():
    s = update_state(base(), "2026-07-09")
    s2 = update_state(s, "2026-07-09")
    assert s2["total_episodes"] == 1
    assert s2["streak"] == 1
    assert s2["episode"] == 1
