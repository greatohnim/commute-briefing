import re


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
