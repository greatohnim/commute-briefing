import asyncio
import re
import sys

import edge_tts

from tools.common import load_config


def _synth_edge(text, out_path, voice, rate):
    async def run():
        communicate = edge_tts.Communicate(text, voice=voice, rate=rate)
        await communicate.save(out_path)

    asyncio.run(run())


def _synth_gtts(text, out_path, voice, rate):
    from gtts import gTTS

    gTTS(text=text, lang="ko").save(out_path)


def synthesize(text, out_path, voice, rate):
    """edge-tts로 변환, 실패 시 gTTS로 폴백. 사용 엔진명을 반환."""
    for name, fn in (("edge", _synth_edge), ("gtts", _synth_gtts)):
        try:
            fn(text, out_path, voice, rate)
            return name
        except Exception as e:  # noqa: BLE001 — 폴백 목적의 광범위 캐치
            print(f"[tts] {name} 실패: {e}", file=sys.stderr)
    raise RuntimeError("모든 TTS 엔진 실패")


def main():
    script_path, out_path = sys.argv[1], sys.argv[2]
    cfg = load_config("config.yaml")
    with open(script_path, "r", encoding="utf-8") as f:
        md = f.read()
    text = extract_narration(md)
    engine = synthesize(text, out_path, cfg["tts"]["voice"], cfg["tts"]["rate"])
    print(f"[tts] {out_path} 생성 완료 (engine={engine})")


if __name__ == "__main__":
    main()


def extract_narration(md_text):
    """대본 마크다운에서 낭독할 순수 텍스트만 뽑는다.

    - YAML 프론트매터 제거
    - 줄 앞 지문 (인트로)/(오늘의 AI) 등 제거
    - 목록 마커 '1)' '2.' 제거
    - 지문만 있던 줄(내용이 비면)은 버린다
    """
    text = re.sub(r"^---\n.*?\n---\n", "", md_text, count=1, flags=re.DOTALL)
    out_lines = []
    for raw in text.splitlines():
        line = raw.strip()
        if not line:
            continue
        # 앞 지문 (...)과 목록 마커 1)/1. 를 순서에 무관하게 제거
        # (예: "1) (오늘의 AI) 텍스트" 처럼 마커가 지문보다 앞서도 둘 다 제거)
        while True:
            stripped = re.sub(r"^\([^)]*\)\s*", "", line)      # 앞 지문
            stripped = re.sub(r"^\d+[\).]\s*", "", stripped)   # 목록 마커
            stripped = stripped.strip()
            if stripped == line:
                break
            line = stripped
        if not line:
            continue
        out_lines.append(line)
    return "\n".join(out_lines)
