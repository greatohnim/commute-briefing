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


def build_feed(episodes, cfg, duration_fn):
    p = cfg["podcast"]
    base = p["base_url"].rstrip("/")
    items = []
    for e in episodes:
        url = f"{base}/audio/{e['filename']}"
        pub = format_datetime(
            datetime.combine(date.fromisoformat(e["date"]), time(6, 0), KST)
        )
        dur = duration_fn(e["filename"])
        title = f"{e['date']} 출근길 AI 브리핑"
        items.append(f"""    <item>
      <title>{escape(title)}</title>
      <enclosure url={quoteattr(url)} type="audio/mpeg" length="0"/>
      <guid isPermaLink="false">{escape(e['filename'])}</guid>
      <pubDate>{pub}</pubDate>
      <itunes:duration>{dur}</itunes:duration>
    </item>""")
    cover = f"{base}/{p['cover']}"
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0" xmlns:itunes="http://www.itunes.com/dtds/podcast-1.0.dtd">
  <channel>
    <title>{escape(p['title'])}</title>
    <link>{escape(base)}</link>
    <language>{escape(p['language'])}</language>
    <description>{escape(p['description'])}</description>
    <itunes:author>{escape(p['author'])}</itunes:author>
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
    eps = list_episodes(audio_dir, cfg["feed"]["keep_days"], today)
    xml = build_feed(eps, cfg, duration_fn=_duration_mutagen(audio_dir))
    with open("docs/feed.xml", "w", encoding="utf-8") as f:
        f.write(xml)
    print(f"[feed] {len(eps)}개 회차로 docs/feed.xml 갱신")


if __name__ == "__main__":
    main()
