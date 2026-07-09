import sys

import pytest
from tools import tts


def test_synthesize_falls_back_to_gtts(monkeypatch, tmp_path):
    out = tmp_path / "o.mp3"

    def boom(*a, **k):
        raise RuntimeError("edge down")

    def fake_gtts(text, out_path, voice, rate):
        open(out_path, "wb").write(b"ID3fake")

    monkeypatch.setattr(tts, "_synth_edge", boom)
    monkeypatch.setattr(tts, "_synth_gtts", fake_gtts)

    engine = tts.synthesize("안녕하세요", str(out), "ko-KR-InJoonNeural", "-5%")
    assert engine == "gtts"
    assert out.exists() and out.stat().st_size > 0


def test_synthesize_raises_when_all_fail(monkeypatch, tmp_path):
    def boom(*a, **k):
        raise RuntimeError("down")

    monkeypatch.setattr(tts, "_synth_edge", boom)
    monkeypatch.setattr(tts, "_synth_gtts", boom)
    with pytest.raises(RuntimeError):
        tts.synthesize("x", str(tmp_path / "o.mp3"), "v", "-5%")


def test_main_cli_path_runs(monkeypatch, tmp_path):
    """CLI 진입점(main)이 extract_narration NameError 없이 끝까지 실행되는지 검증."""
    script = tmp_path / "s.md"
    script.write_text(
        "---\ndate: 2026-07-09\n---\n\n(인트로) 안녕하세요, 테스트입니다.\n",
        encoding="utf-8",
    )
    out = tmp_path / "o.mp3"

    calls = {}

    def fake_synth(text, out_path, voice, rate):
        calls["text"] = text
        calls["out_path"] = out_path
        return "edge"

    monkeypatch.setattr(tts, "synthesize", fake_synth)
    monkeypatch.setattr(
        tts, "load_config", lambda p: {"tts": {"voice": "v", "rate": "-5%"}}
    )
    monkeypatch.setattr(sys, "argv", ["tools.tts", str(script), str(out)])

    tts.main()

    assert calls["out_path"] == str(out)
    assert "안녕하세요" in calls["text"]
