from tools.build_feed import list_episodes, build_feed


def test_list_episodes_filters_and_sorts(tmp_path):
    d = tmp_path / "audio"
    d.mkdir()
    for name in ["2026-07-01.mp3", "2026-07-09.mp3", "2026-05-01.mp3", "notes.txt"]:
        (d / name).write_bytes(b"x")
    eps = list_episodes(str(d), keep_days=30, today="2026-07-09")
    dates = [e["date"] for e in eps]
    assert dates == ["2026-07-09", "2026-07-01"]     # 최신순, 5월 것은 30일 초과로 제외


def test_build_feed_has_channel_and_items():
    cfg = {
        "podcast": {
            "title": "출근길 AI 브리핑", "author": "jhoh",
            "description": "설명", "language": "ko",
            "base_url": "https://u.github.io/commute-briefing",
            "cover": "assets/cover.png",
        }
    }
    eps = [{"date": "2026-07-09", "filename": "2026-07-09.mp3"}]
    xml = build_feed(eps, cfg, duration_fn=lambda fn: 300)
    assert "<rss" in xml and "itunes" in xml
    assert "<title>출근길 AI 브리핑</title>" in xml
    assert "https://u.github.io/commute-briefing/audio/2026-07-09.mp3" in xml
    assert "<itunes:duration>300</itunes:duration>" in xml
    assert 'url="https://u.github.io/commute-briefing/assets/cover.png"' in xml
