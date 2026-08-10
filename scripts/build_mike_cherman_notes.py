#!/usr/bin/env python3
"""Build rights-safe Mike Cherman interview notes from a reviewed notes manifest."""

from __future__ import annotations

import html
import json
import os
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "tennis-culture" / "mike-cherman"

READ_FIRST = {
    "jWC4joiHaTY", "5KhgzVrU-JM", "4XLDVLg_Rx8", "NG3SqEpqIkY",
    "lnnGQdwfNt0", "lKKxUcky-KA", "sTp-Rh5gydg",
}
READ_SEQUENCE = (
    "jWC4joiHaTY", "5KhgzVrU-JM", "4XLDVLg_Rx8", "NG3SqEpqIkY",
    "lnnGQdwfNt0", "lKKxUcky-KA", "sTp-Rh5gydg",
)
READ_NEXT = {
    "pmk_c5DpnKQ", "q7T4j22Ph_4", "TGzzXsnzdKE", "5C4AeKriXkw",
    "b3GuvG3cDX4", "PexMQy3K4K4", "UNJMsSzxCjw", "ajV5DdiY_WE",
    "AQqPH5oef6E", "XOAUWHLCDMs", "w0ElIfi3s0k",
}

OVERALL = (
    "Across these interviews, Mike’s career is less a story about having the right taste than about building an operating stack. "
    "He starts with shirts made in school, teaches himself design, uses aggressive self-promotion to get near people he wants to learn from, "
    "and takes low-status production jobs where he can watch files become physical objects. Goodwood, the Bowery customization shop, early Kith work, "
    "ICNY, freelance production, and Chinatown Market are not separate anecdotes. Each stage adds a capability: graphics, machinery, sourcing, retail, "
    "wholesale, cash flow, licensing, team management, or audience feedback.\n\n"
    "His repeatable method is: make one clear thing, put it in front of real people, produce against the response, and use what happens to decide the next move. "
    "The most useful early Chinatown Market stories are not the large collaborations. They are the one photographed sample, the handwritten label, the blank shirts bought only after orders arrived, "
    "and the speed of having design, printing, photography, posting, and shipping close together. Speed mattered because it shortened learning, not because every fast idea was good. "
    "The Frank Ocean refund, offensive or careless releases, and the later name change show what happens when speed outruns legal or ethical judgment.\n\n"
    "Mike consistently chooses access over streetwear purity. He wanted MARKET in stores ordinary people used, wanted the social account to feel like a person, and built live customization and Discord programs where customers could contribute instead of only buy. "
    "The smiley basketball is the cleanest example of the product philosophy: take an object people already understand, keep it functional, and change its cultural meaning enough that it can live in sport, fashion, play, and collecting at once. "
    "For Tom, tennis equipment and court rituals offer the same opening—but only if the object still works and the tennis community is treated as a participant rather than scenery.\n\n"
    "The interviews are also unusually candid about the cost of growth. Mike lost ICNY, misunderstood revenue as profit, entered partnerships before terms were clear, hired people faster than he knew how to manage them, and learned that not every early teammate fits every stage. "
    "His better later advice is concrete: contracts before committed labor; small runs before inventory; roles before enthusiasm; trusted production partners; and feedback from people qualified to disagree. "
    "He sees former employees building their own companies as part of MARKET’s result, even when the relationship ended badly.\n\n"
    "What Tom should take to Mike is therefore not a broad request for mentorship and not a polished mood board. Bring one finished tennis object, the failed samples that explain its decisions, a short record of how an actual player used it, the production constraint still unresolved, and one precise question. "
    "A strong ask would be: ‘Here is the object, here is what changed after ten players touched it, and here is the one production or community decision I cannot resolve. What am I missing?’ "
    "That approach matches what Mike repeatedly rewards: visible initiative, proximity to the craft, willingness to show the miss, and enough operating seriousness that his answer has somewhere to go."
)

def reading_verdict(video_id: str, note: dict) -> tuple[str, str]:
    if video_id in READ_FIRST:
        return "Read first", note["tom"]
    if video_id in READ_NEXT:
        return "Read if this angle matters", note["tom"]
    return "Skip for now", note["tom"]


def clock(seconds: int) -> str:
    hours, rest = divmod(max(0, int(seconds)), 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def source_url(video_id: str, seconds: int | None = None) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    return f"{url}&amp;t={seconds}s" if seconds is not None else url


def raw_access(record: dict) -> tuple[str, str]:
    if record.get("full_transcript_path"):
        return html.escape(record["full_transcript_path"]), "Raw transcript"
    if record["transcript_source"].casefold() == "youtube captions":
        return source_url(record["id"]), "Raw transcript on YouTube"
    return source_url(record["id"]), "Source recording"


def render_licensed_transcript(record: dict, article_html: str) -> str:
    """Render a publisher-licensed caption transcript with explicit attribution."""
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Full transcript — {html.escape(record['title'])}</title>
<meta name="description" content="Complete timestamped publisher caption transcript for {html.escape(record['title'])}.">
<link rel="stylesheet" href="../styles.css"></head>
<body><main>
  <p class="back"><a href="../{record['id']}.html">← Interview notes</a></p>
  <header class="transcript-hero">
    <h1>{html.escape(record['title'])}</h1>
    <p class="meta">Raw transcript · {html.escape(record['channel'])} · {record['date']} · {clock(record['duration'])}</p>
  </header>
  <p class="license-note">{html.escape(record['license'])} · <a href="{source_url(record['id'])}" target="_blank" rel="noopener">source</a></p>
  <article class="full-transcript">{article_html}</article>
  <p class="end"><a href="{source_url(record['id'])}" target="_blank" rel="noopener">Watch →</a></p>
</main></body></html>'''


def build_licensed_transcripts(records: list[dict]) -> None:
    """Refresh licensed transcript artifacts when the ignored source corpus is present."""
    source_dir_value = os.environ.get("MIKE_TRANSCRIPT_SOURCE_DIR")
    source_dir = Path(source_dir_value) if source_dir_value else None
    for record in records:
        relative_target = record.get("full_transcript_path")
        if not relative_target:
            continue
        target = OUT / relative_target
        if source_dir:
            source = source_dir / f"{record['id']}.html"
            if not source.exists():
                raise FileNotFoundError(f"licensed transcript source missing: {source}")
            source_text = source.read_text(encoding="utf-8")
            match = re.search(r"<article>(.*?)</article>", source_text, flags=re.DOTALL)
            if not match:
                raise ValueError(f"licensed transcript article missing: {source}")
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_text(render_licensed_transcript(record, match.group(1)), encoding="utf-8")
        elif not target.exists():
            raise RuntimeError(
                f"{target} is absent; set MIKE_TRANSCRIPT_SOURCE_DIR to rebuild licensed transcripts"
            )


def select_summary_moments(moments: list[list], limit: int = 4) -> list[list]:
    """Keep a short, evenly distributed overview while the full digest remains below."""
    if len(moments) <= limit:
        return moments
    indexes = [round(index * (len(moments) - 1) / (limit - 1)) for index in range(limit)]
    return [moments[index] for index in indexes]


def render_page(record: dict, note: dict, cleaned_sections: list[list]) -> str:
    summary_bullets = [
        f'''<li class="overview">{html.escape(note["summary"])}</li>''',
    ]
    summary_bullets.extend(
        f'''<li><strong>{html.escape(label)}</strong><span>{html.escape(body)}</span></li>'''
        for _, label, body in select_summary_moments(note["moments"])
    )
    cleaned_blocks = "\n".join(
        f'''<li id="cleaned-t{second}">
          <h3>{html.escape(label)}</h3>
          <p>{html.escape(body)}</p>
        </li>'''
        for second, label, body in cleaned_sections
    )
    raw_url, raw_label = raw_access(record)
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(record['title'])} — Mike Cherman Interviews</title>
<meta name="description" content="Context, summary, and chronological transcript notes for {html.escape(record['title'])}.">
<link rel="stylesheet" href="styles.css"></head>
<body><main>
  <p class="back"><a href="./">← All interviews</a></p>
  <header class="interview-header">
    <p class="source">{html.escape(record['channel'])}</p>
    <h1>{html.escape(record['title'])}</h1>
    <p class="context"><span>{html.escape(record['format'])}</span><span>{record['date']}</span><span>{clock(record['duration'])}</span></p>
  </header>
  <section class="summary-block"><h2>Summary</h2><ul>{''.join(summary_bullets)}</ul></section>
  <section><h2>Transcript summary</h2><ol class="cleaned-transcript">{cleaned_blocks}</ol></section>
  <p class="raw"><a href="{raw_url}" target="_blank" rel="noopener">{raw_label} →</a></p>
</main></body></html>'''


def render_index(records: list[dict], notes: dict) -> str:
    def priority(record: dict) -> tuple[int, str, str]:
        if record["id"] in READ_FIRST:
            return 0, f"{READ_SEQUENCE.index(record['id']):02d}", record["id"]
        rank = 1 if record["id"] in READ_NEXT else 2
        return rank, record["date"], record["id"]

    cards = []
    for record in sorted(records, key=priority):
        note = notes[record["id"]]
        verdict, reason = reading_verdict(record["id"], note)
        raw_url, raw_label = raw_access(record)
        cards.append(f'''<li>
      <h2><a href="{record['id']}.html">{html.escape(record['title'])}</a></h2>
      <p class="meta">{html.escape(record['channel'])} · {record['date']} · {clock(record['duration'])}</p>
      <p><b>{verdict}.</b> {html.escape(reason)}</p>
      <p>{html.escape(note['summary'])}</p>
      <p class="actions"><a href="{record['id']}.html">Open notes</a> · <a href="{raw_url}" target="_blank" rel="noopener">{raw_label}</a></p>
    </li>''')
    synthesis = "".join(f"<p>{html.escape(paragraph)}</p>" for paragraph in OVERALL.split("\n\n"))
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mike Cherman interviews</title>
<meta name="description" content="Twenty-eight Mike Cherman interviews and appearances, cleaned into timestamped notes and practical insights for Tom.">
<link rel="stylesheet" href="styles.css"></head>
<body><main>
  <h1>Mike Cherman</h1>
  <p class="meta">28 public interviews and substantive appearances</p>
  <div class="synthesis">{synthesis}</div>
  <ol class="interviews">{''.join(cards)}</ol>
</main></body></html>'''


def main() -> None:
    manifest = json.loads((OUT / "manifest.json").read_text(encoding="utf-8"))
    records = sorted(manifest["records"], key=lambda record: (record["date"], record["id"]), reverse=True)
    build_licensed_transcripts(records)
    notes = json.loads((OUT / "notes.json").read_text(encoding="utf-8"))
    cleaned = json.loads((OUT / "cleaned-transcripts.json").read_text(encoding="utf-8"))
    ids = {record["id"] for record in records}
    if set(notes) != ids:
        raise ValueError(f"notes/manifest mismatch: missing={sorted(ids-set(notes))}, extra={sorted(set(notes)-ids)}")
    if set(cleaned) != ids:
        raise ValueError(
            f"cleaned/manifest mismatch: missing={sorted(ids-set(cleaned))}, extra={sorted(set(cleaned)-ids)}"
        )
    for record in records:
        blocks = cleaned[record["id"]]
        seconds = [block[0] for block in blocks]
        if seconds != sorted(set(seconds)):
            raise ValueError(f"cleaned transcript timestamps not strictly ordered: {record['id']}")
        if seconds[0] > 120 or seconds[-1] < record["duration"] - 240:
            raise ValueError(f"cleaned transcript does not cover full chronology: {record['id']}")
        for second, label, body in blocks:
            if not (0 <= second <= record["duration"]):
                raise ValueError(f"cleaned transcript timestamp outside duration: {record['id']} {second}")
            if not label.strip() or len(body.split()) < 20:
                raise ValueError(f"thin cleaned transcript block: {record['id']} {second}")
    for index, record in enumerate(records):
        (OUT / f"{record['id']}.html").write_text(
            render_page(record, notes[record["id"]], cleaned[record["id"]]), encoding="utf-8"
        )
    (OUT / "index.html").write_text(render_index(records, notes), encoding="utf-8")
    block_count = sum(len(blocks) for blocks in cleaned.values())
    print(f"Built {len(records)} complete cleaned interview pages with {block_count} chronological blocks")


if __name__ == "__main__":
    main()
