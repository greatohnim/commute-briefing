from tools.validate_script import validate

GOOD = """---
date: 2026-07-09
streak: 5
episode: 12
---

(인트로) 안녕하세요. """ + ("가" * 750) + """
"""


def test_valid_script_passes():
    assert validate(GOOD, 700, 900, ["코나아이"]) == []


def test_missing_frontmatter_key_flagged():
    md = "---\ndate: 2026-07-09\n---\n\n본문"
    problems = validate(md, 1, 5000, [])
    assert any("episode" in p for p in problems)
    assert any("streak" in p for p in problems)


def test_banned_term_flagged():
    md = GOOD.replace("안녕하세요.", "안녕하세요. 코나아이 관련 내용.")
    problems = validate(md, 700, 900, ["코나아이"])
    assert any("코나아이" in p for p in problems)


def test_too_short_flagged():
    md = "---\ndate: 2026-07-09\nstreak: 1\nepisode: 1\n---\n\n(인트로) 짧음"
    problems = validate(md, 700, 900, [])
    assert any("분량" in p for p in problems)


def test_banned_term_only_in_stripped_direction_is_flagged():
    # The term lives ONLY inside a (...) stage direction, which
    # extract_narration removes before TTS. It must still be flagged,
    # because the scan targets the full raw md_text, not the narration.
    md = (
        "---\ndate: 2026-07-09\nstreak: 1\nepisode: 1\n---\n\n"
        "(코나아이 내부 메모) 안녕하세요.\n" + ("가" * 750)
    )
    problems = validate(md, 700, 900, ["코나아이"])
    assert any("코나아이" in p for p in problems)
