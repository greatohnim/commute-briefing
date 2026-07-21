import os
import re
import sys
from datetime import date, datetime, time, timedelta, timezone
from email.utils import format_datetime
from xml.sax.saxutils import escape, quoteattr

KST = timezone(timedelta(hours=9))
DATE_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})\.mp3$")


def list_episodes(audio_dir, keep_days, today):
    cutoff = date.fromisoformat(today) - timedelta(days=keep_days)
    eps = []
    for name in os.listdir(audio_dir):
        m = DATE_RE.match(name)
        if not m:
            continue
        d = m.group(1)
        if date.fromisoformat(d) >= cutoff:
            eps.append({"date": d, "filename": name})
    eps.sort(key=lambda e: e["date"], reverse=True)
    return eps


def _duration_mutagen(audio_dir):
    from mutagen.mp3 import MP3

    def fn(filename):
        return int(MP3(os.path.join(audio_dir, filename)).info.length)

    return fn


def _version_content(audio_dir):
    """mp3 내용 해시(앞 8자리)를 반환. 음성이 바뀌면 guid도 바뀌게 하기 위함."""
    import hashlib

    def fn(filename):
        with open(os.path.join(audio_dir, filename), "rb") as f:
            return hashlib.md5(f.read()).hexdigest()[:8]

    return fn


def build_feed(episodes, cfg, duration_fn, version_fn=None):
    p = cfg["podcast"]
    base = p["base_url"].rstrip("/")
    items = []
    for e in episodes:
        url = f"{base}/audio/{e['filename']}"
        pub = format_datetime(
            datetime.combine(date.fromisoformat(e["date"]), time(6, 0), KST)
        )
        dur = duration_fn(e["filename"])
        # guid에 내용 버전을 붙여, 파일명이 같아도 음성이 바뀌면 팟캐스트 앱이
        # 새 회차로 인식해 다시 받도록 한다. enclosure URL은 실제 파일 그대로 둔다.
        guid = e["filename"]
        if version_fn is not None:
            guid = f"{guid}#{version_fn(e['filename'])}"
        title = f"{e['date']} 출근길 AI 브리핑"
        items.append(f"""    <item>
      <title>{escape(title)}</title>
      <enclosure url={quoteattr(url)} type="audio/mpeg" length="0"/>
      <guid isPermaLink="false">{escape(guid)}</guid>
      <pubDate>{pub}</pubDate>
      <itunes:duration>{dur}</itunes:duration>
    </item>""")
    cover = f"{base}/{p['cover']}"
    explicit = "true" if p.get("explicit") else "false"
    category = p.get("category", "Technology")
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{escape(p['title'])}</title>
    <link>{escape(base)}</link>
    <language>{escape(p['language'])}</language>
    <description>{escape(p['description'])}</description>
    <itunes:author>{escape(p['author'])}</itunes:author>
    <itunes:summary>{escape(p['description'])}</itunes:summary>
    <itunes:type>episodic</itunes:type>
    <itunes:explicit>{explicit}</itunes:explicit>
    <itunes:category text={quoteattr(category)}/>
    <itunes:image href={quoteattr(cover)}/>
    <image><url>{escape(cover)}</url><title>{escape(p['title'])}</title><link>{escape(base)}</link></image>
{chr(10).join(items)}
  </channel>
</rss>
"""


def main():
    from tools.common import load_config

    today = sys.argv[1]
    cfg = load_config("config.yaml")
    audio_dir = "docs/audio"
    os.makedirs(audio_dir, exist_ok=True)
    eps = list_episodes(audio_dir, cfg["feed"]["keep_days"], today)
    xml = build_feed(
        eps,
        cfg,
        duration_fn=_duration_mutagen(audio_dir),
        version_fn=_version_content(audio_dir),
    )
    with open("docs/feed.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"[feed] {len(eps)}개 회차로 docs/feed.xml 갱신")


if __name__ == "__main__":
    main()
