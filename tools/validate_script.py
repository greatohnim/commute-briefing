import re
import sys

from tools.tts import extract_narration

REQUIRED_KEYS = ("date", "streak", "episode")


def _frontmatter(md_text):
    m = re.match(r"^---\n(.*?)\n---\n", md_text, flags=re.DOTALL)
    return m.group(1) if m else ""


def validate(md_text, min_chars, max_chars, banned_terms):
    problems = []

    fm = _frontmatter(md_text)
    for key in REQUIRED_KEYS:
        if not re.search(rf"^{key}\s*:", fm, flags=re.MULTILINE):
            problems.append(f"프론트매터에 '{key}' 누락")

    narration = extract_narration(md_text)
    n = len(narration.replace("\n", ""))
    if n < min_chars or n > max_chars:
        problems.append(f"낭독 분량 범위 벗어남: {n}자 (허용 {min_chars}~{max_chars})")

    for term in banned_terms:
        if term.lower() in md_text.lower():
            problems.append(f"금지어 포함: '{term}'")

    return problems


def main():
    from tools.common import load_config

    cfg = load_config("config.yaml")
    with open(sys.argv[1], "r", encoding="utf-8") as f:
        md = f.read()
    s = cfg["script"]
    problems = validate(md, s["min_chars"], s["max_chars"], s["banned_terms"])
    if problems:
        for p in problems:
            print(f"[검증실패] {p}", file=sys.stderr)
        sys.exit(1)
    print("[검증] 통과")


if __name__ == "__main__":
    main()
