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
        line = re.sub(r"^\([^)]*\)\s*", "", line).strip()   # 앞 지문
        line = re.sub(r"^\d+[\).]\s*", "", line).strip()     # 목록 마커
        if not line:
            continue
        out_lines.append(line)
    return "\n".join(out_lines)
