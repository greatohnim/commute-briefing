from tools.tts import extract_narration


def test_strips_frontmatter_directions_and_list_markers():
    md = """---
date: 2026-07-09
streak: 5
episode: 12
---

(인트로) 안녕하세요, 7월 9일 브리핑입니다.
(오늘의 AI)
  1) 첫 번째 헤드라인입니다.
  2. 두 번째 헤드라인입니다.
"""
    out = extract_narration(md)
    assert "date:" not in out
    assert "(인트로)" not in out
    assert "(오늘의 AI)" not in out          # 지문만 있는 줄은 사라진다
    assert "안녕하세요, 7월 9일 브리핑입니다." in out
    assert "첫 번째 헤드라인입니다." in out
    assert "두 번째 헤드라인입니다." in out
    assert "1)" not in out and "2." not in out


def test_strips_marker_before_direction_regardless_of_order():
    md = "1) (오늘의 AI) 실제 내용입니다.\n"
    out = extract_narration(md)
    assert "실제 내용입니다." in out
    assert "(오늘의 AI)" not in out
    assert "1)" not in out
