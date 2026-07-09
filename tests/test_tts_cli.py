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
