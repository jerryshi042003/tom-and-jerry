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


def clock(seconds: int) -> str:
    hours, rest = divmod(max(0, int(seconds)), 3600)
    minutes, secs = divmod(rest, 60)
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def source_url(video_id: str, seconds: int | None = None) -> str:
    url = f"https://www.youtube.com/watch?v={video_id}"
    return f"{url}&amp;t={seconds}s" if seconds is not None else url


def render_licensed_transcript(record: dict, article_html: str) -> str:
    """Render a publisher-licensed caption transcript with explicit attribution."""
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Full transcript — {html.escape(record['title'])}</title>
<meta name="description" content="Complete timestamped publisher caption transcript for {html.escape(record['title'])}.">
<link rel="stylesheet" href="../styles.css"></head>
<body><main>
  <p class="top"><a href="../{record['id']}.html">← Interview summary and cleaned stories</a></p>
  <header class="hero transcript-hero">
    <p class="eyebrow">Complete timestamped caption transcript · {record['date']} · {clock(record['duration'])}</p>
    <h1>{html.escape(record['title'])}</h1>
    <p class="byline">{html.escape(record['channel'])}</p>
    <p class="summary">This is the full publisher caption sequence, separated from the edited interview notes so the complete source wording remains readable when needed.</p>
  </header>
  <section class="license-note"><p><b>Attribution.</b> “{html.escape(record['title'])},” by {html.escape(record['channel'])}, <a href="{source_url(record['id'])}" target="_blank" rel="noopener">published on YouTube</a> under {html.escape(record['license'])}. YouTube identifies Creative Commons uploads as reusable subject to CC BY attribution. Captions may contain machine errors; verify the recording before quoting.</p></section>
  <article class="full-transcript">{article_html}</article>
  <p class="end"><a href="{source_url(record['id'])}" target="_blank" rel="noopener">Watch the source recording ↗</a></p>
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


def render_page(record: dict, note: dict, cleaned_sections: list[list]) -> str:
    moments = "\n".join(
        f'''<li id="t{second}">
          <a class="time" href="{source_url(record['id'], second)}" target="_blank" rel="noopener">{clock(second)}</a>
          <div><h2>{html.escape(label)}</h2><p>{html.escape(body)}</p></div>
        </li>'''
        for second, label, body in note["moments"]
    )
    note_text = record.get("note")
    source_note = f'<p class="source-note">{html.escape(note_text)}</p>' if note_text else ""
    cleaned_transcript = ""
    if cleaned_sections:
        cleaned_blocks = "\n".join(
            f'''<li id="cleaned-t{second}">
          <a class="time" href="{source_url(record['id'], second)}" target="_blank" rel="noopener">{clock(second)}</a>
          <div><h2>{html.escape(label)}</h2><p>{html.escape(body)}</p></div>
        </li>'''
            for second, label, body in cleaned_sections
        )
        cleaned_transcript = f'''<section class="cleaned-reading">
    <p class="section-label">Cleaned interview</p>
    <p class="reading-note">Complete chronological reading notes for this recording. The wording is edited and paraphrased for clarity; timestamps open the source and these paragraphs should not be quoted as Mike’s exact words.</p>
    <ol class="cleaned-transcript">{cleaned_blocks}</ol>
  </section>'''
    if record.get("full_transcript_path"):
        transcript_access = (
            f'<p><a class="transcript-link" href="{html.escape(record["full_transcript_path"])}">'
            "Read the complete timestamped transcript →</a></p>"
            f'<p>The publisher released this recording under {html.escape(record["license"])}. '
            "The complete caption sequence is therefore reproduced with title, creator, source, and license attribution.</p>"
        )
    elif record["transcript_source"].casefold() == "youtube captions":
        transcript_access = (
            f'<p>This recording has a publisher-served YouTube caption track. '
            f'<a href="{source_url(record["id"])}" target="_blank" rel="noopener">Open the video</a>, '
            "then use YouTube’s <b>Show transcript</b> control to read the raw caption sequence.</p>"
        )
    else:
        transcript_access = (
            f'<p>The source does not expose a usable public English transcript. '
            f'<a href="{source_url(record["id"])}" target="_blank" rel="noopener">Open the recording</a>. '
            "The local machine transcript was used for these notes but is not republished as an authoritative source text.</p>"
        )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{html.escape(record['title'])} — Mike Cherman Interviews</title>
<meta name="description" content="Cleaned notes and Tom-specific takeaways from {html.escape(record['title'])}.">
<link rel="stylesheet" href="styles.css"></head>
<body><main>
  <p class="top"><a href="./">← All Mike interviews</a></p>
  <header class="hero">
    <p class="eyebrow">{html.escape(record['format'])} · {record['date']} · {clock(record['duration'])}</p>
    <h1>{html.escape(record['title'])}</h1>
    <p class="byline">{html.escape(record['channel'])}</p>
    <p class="summary">{html.escape(note['summary'])}</p>
    <p><a href="{source_url(record['id'])}" target="_blank" rel="noopener">Watch the original on YouTube ↗</a></p>
  </header>
  <blockquote><p>“{html.escape(note['quote'])}”</p><cite><a href="{source_url(record['id'], note['quote_t'])}" target="_blank" rel="noopener">Caption excerpt · {clock(note['quote_t'])}</a></cite></blockquote>
  <section class="tom-card"><p class="eyebrow">What Tom should take from this</p><p>{html.escape(note['tom'])}</p></section>
  <section><p class="section-label">Interview details and stories</p><ol class="moments">{moments}</ol></section>
{cleaned_transcript}
{source_note}
  <details class="transcript-access"><summary>Raw transcript access</summary>{transcript_access}</details>
  <section class="method"><p><b>Editorial method.</b> These are source-faithful paraphrases made from public captions or local speech recognition, not a verbatim transcript. Timestamps open the exact recording position. Verify the source before quoting Mike.</p></section>
</main></body></html>'''


def render_index(records: list[dict], notes: dict) -> str:
    def cards(tier: str) -> str:
        def searchable(record: dict) -> str:
            note = notes[record["id"]]
            moment_text = " ".join(f"{label} {body}" for _, label, body in note["moments"])
            return " ".join((record["title"], record["channel"], note["summary"], note["tom"], moment_text)).lower()

        return "\n".join(
            f'''<li data-search="{html.escape(searchable(r))}">
              <p class="eyebrow">{r['date']} · {html.escape(r['format'])} · {clock(r['duration'])}</p>
              <h2><a href="{r['id']}.html">{html.escape(r['title'])}</a></h2>
              <p>{html.escape(notes[r['id']]['summary'])}</p>
              <a class="detail" href="{r['id']}.html">Notes + Tom insight →</a>
            </li>'''
            for r in records if r["tier"] == tier
        )

    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>Mike Cherman Interviews — Jerry / Tom</title>
<meta name="description" content="Twenty-eight Mike Cherman interviews and appearances, cleaned into timestamped notes and practical insights for Tom.">
<link rel="stylesheet" href="styles.css"></head>
<body><main>
  <p class="top"><a href="../">← Jerry / Tom board</a></p>
  <header class="hero">
    <p class="eyebrow">Jerry / Tom · Interviews</p>
    <h1>Mike Cherman interviews</h1>
    <p class="summary">Twenty-eight public interviews and substantive appearances. Together they trace Mike from homemade school shirts and ICNY through Chinatown Market, MARKET, teams, collaborations, physical retail, sports objects, community, and the responsibilities that came with growth.</p>
    <p class="scope">22 direct interviews, podcasts, and panels · 6 adjacent first-person appearances · searched 10 August 2026</p>
  </header>
  <section class="corpus-summary">
    <p class="section-label">What the full set says</p>
    <p>Mike’s recurring method is simple: make one thing, put it in front of people, learn the operational work behind it, and use the response to make the next thing. The interviews repeatedly return to five tensions: access versus exclusivity; fast cultural response versus legal and ethical responsibility; founder control versus giving a team room; collaboration excitement versus contracts and ownership; and a product’s image versus the community and physical work that make it real.</p>
    <p>For Tom, the useful pattern is not “start a streetwear brand.” It is to arrive with a finished tennis object, document how it was made, know who it serves, invite a real participant into the process, and ask Mike for one concrete criticism. The archive also argues for boundaries: keep authorship clear, define the pilot, and do not let enthusiasm become unlimited unpaid development.</p>
  </section>
  <section><p class="section-label">Direct interviews, podcasts, and panels</p><ol class="interviews" id="core">{cards('core')}</ol></section>
  <section><p class="section-label">Adjacent first-person appearances</p><p class="scope">Included because Mike speaks substantively; kept separate so a workshop, tour, or campaign is not mislabeled as an interview.</p><ol class="interviews" id="adjacent">{cards('adjacent')}</ol></section>
  <section class="method"><p><b>Coverage.</b> “Every” means every qualifying result recovered by the documented twelve-query YouTube sweep. Ranked search is not a perfect global index. <a href="SOURCES.md">Read the inclusion rule, exclusions, and transcript method.</a></p></section>
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
    oversized = {video_id: len(note["quote"].split()) for video_id, note in notes.items() if len(note["quote"].split()) > 24}
    if oversized:
        raise ValueError(f"caption excerpts exceed 24 words: {oversized}")
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
