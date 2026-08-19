import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('../tennis-culture/index.html', import.meta.url), 'utf8');
const css = readFileSync(new URL('../tennis-culture/styles.css', import.meta.url), 'utf8');
const sources = readFileSync(new URL('../tennis-culture/SOURCES.md', import.meta.url), 'utf8');
const archiveBase = 'https://jerryshi042003.github.io/david-choe-transcript-archive/#/';

// Meeting facts and dated entries the record must keep.
for (const term of [
  'ball mower', 'Bellevue', 'daily job', 'Mike Cherman', 'Shingo Arai', 'One Hand Tony',
  'nothing finished to show Mike or Shingo', 'videographer friend', 'Tom has not reviewed',
  'one proof — proposed, not agreed', 'one finished object',
  '17 August 2026', '10 August 2026', 'Late July 2026', 'What this changed',
  'Current plan', '17 September', 'Market Studios',
]) {
  assert.ok(html.toLowerCase().includes(term.toLowerCase()), `missing meeting fact: ${term}`);
}

// Philippines trip planning must stay concrete, not generic.
for (const term of [
  'Felicisimo Ampon', 'Rizal Memorial', 'Valle Verde', 'Rancho Uno', 'UP Diliman',
  'shell courts', 'play.psc.gov.ph', 'November to early December',
]) {
  assert.ok(html.includes(term), `missing Philippines planning fact: ${term}`);
}

// External Choe archive citations stay absolute.
for (const id of [
  'saga1-episode-101-the-ranch-solo-series-part-one',
  'saga1-episode-119-the-ranch-solo-series-part-two',
  'saga2-saga-02-chapter-021-the-ranch-solo-series-3-the-lost-episode',
  '3QecMMrcCCA', '-wZk4B1BB0c', 'OP1mXscTUnw', 'zHyvVajsqMw'
]) assert.ok(html.includes(`${archiveBase}${id}`), `missing external archive source ${id}`);
assert.ok(!html.includes('../#/'), 'David archive links must not depend on repository nesting');

// The Choe accumulation survives in full.
const choeStart = html.indexOf('David Choe — repeated questions');
assert.ok(choeStart > -1, 'Choe accumulation must remain on the board');
const choeSections = html.slice(choeStart);
assert.ok((choeSections.match(/<li>/g) || []).length >= 30, 'Choe research sections must retain the full working accumulation');

// Every picture is cited; the board keeps at least seven.
assert.ok((html.match(/<figure>/g) || []).length >= 7, 'board needs at least seven cited pictures');
assert.ok((html.match(/<figcaption>/g) || []).length === (html.match(/<figure>/g) || []).length, 'every picture needs a citation caption');

// The three-anchor tab is the only navigation; no generic UI structure.
for (const anchor of ['id="meetings"', 'id="philippines"', 'id="board"', 'href="#meetings"', 'href="#philippines"', 'href="#board"']) {
  assert.ok(html.includes(anchor), `missing tab anchor: ${anchor}`);
}
for (const forbidden of ['<header', '<nav', '<aside', '<section', '<table', '<details', '<button', 'class="card', 'FACT +', 'OPEN', 'useful work']) {
  assert.ok(!html.includes(forbidden), `forbidden site structure or status language: ${forbidden}`);
}
assert.doesNotMatch(html, /<h[1-6][^>]*>/i);

// One type size, black on white, no decorative chrome. No rules/borders at all now.
assert.match(css, /font-size:\s*15px/);
assert.equal((css.match(/font-size:/g) || []).length, 1, 'use one type size throughout');
assert.doesNotMatch(css, /--[a-z-]+:|position:\s*sticky|border:(?!\s*0(?:;|\s|}))|border-bottom|border-top|letter-spacing|text-transform|box-shadow|background:\s*#[^f]|color:\s*#[^0]/i);

// Source discipline.
assert.match(sources, /San Jose is not part of either exact claim/i);
assert.match(sources, /421 unique record IDs/i);
assert.match(sources, /173 review windows/i);
assert.match(sources, /Felicisimo Ampon/i);
assert.match(html, /href="SOURCES\.md"/);

console.log('single-page tennis project: content, Philippines planning, external archive citations, and no-UI checks passed');
