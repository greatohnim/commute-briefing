import runpy
import sys
import warnings

import edge_tts
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


def test_cli_entrypoint_runs_as_main(monkeypatch, tmp_path):
    """Drives `python -m tools.tts` via runpy so the __main__ guard executes
    during module load — the only path that re-triggers the ordering bug
    (main() calling extract_narration before it is defined -> NameError)."""

    class _StubCommunicate:
        def __init__(self, *a, **k):
            pass

        async def save(self, out_path):
            with open(out_path, "wb") as f:
                f.write(b"ID3stub")

    monkeypatch.setattr(edge_tts, "Communicate", _StubCommunicate)
    monkeypatch.chdir(tmp_path)
    (tmp_path / "config.yaml").write_text(
        "tts:\n  voice: ko-KR-InJoonNeural\n  rate: '-5%'\n", encoding="utf-8"
    )
    script = tmp_path / "s.md"
    script.write_text(
        "---\ndate: 2026-07-09\n---\n\n(인트로) 안녕하세요.\n", encoding="utf-8"
    )
    out = tmp_path / "docs" / "audio" / "out.mp3"
    monkeypatch.setattr(sys, "argv", ["tools.tts", str(script), str(out)])

    with warnings.catch_warnings():
        # runpy re-executes an already-imported module; silence its RuntimeWarning
        warnings.simplefilter("ignore", RuntimeWarning)
        runpy.run_module("tools.tts", run_name="__main__")

    assert out.exists() and out.stat().st_size > 0
