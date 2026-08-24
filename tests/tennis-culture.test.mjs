import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const html = readFileSync(new URL('../tennis-culture/index.html', import.meta.url), 'utf8');
const css = readFileSync(new URL('../tennis-culture/styles.css', import.meta.url), 'utf8');
const sources = readFileSync(new URL('../tennis-culture/SOURCES.md', import.meta.url), 'utf8');
const archiveBase = 'https://jerryshi042003.github.io/david-choe-transcript-archive/#/';

// Working-record facts the page must keep.
for (const term of [
  'ball mower', 'Bellevue', 'daily job', 'Mike Cherman', 'Shingo Arai', 'One Hand Tony',
  'nothing finished to show Mike or Shingo', 'videographer friend',
  '17 August 2026', '10 August 2026', 'Late July 2026', 'what this changed',
  'Current plan', '17 September', 'Market Studios',
  'five designs a week', '30 August',
  'Chris Papa', 'Adil Dara', 'Rocco Arena', 'Patrick Palacio Ondevilla',
  'players who matter deeply in their country', 'field production and distribution',
  'Tom Guilmard', 'Not a vacation', 'first player collaborator', 'field unit',
]) {
  assert.ok(html.toLowerCase().includes(term.toLowerCase()), `missing record fact: ${term}`);
}

// Philippines trip planning stays concrete: courts, costs, platform, transport, map.
for (const term of [
  'Felicisimo Ampon', 'Rizal Memorial', 'Valle Verde', 'Rancho Uno', 'UP Diliman',
  'shell courts', 'play.psc.gov.ph', 'November to early December',
  '₱600', '₱100', 'no Uber', 'Grab', 'id="phmap"',
  'QUEZON CITY', 'MARIKINA', 'LRT-1', 'Makati or BGC', 'output=embed', '47 km',
  'Marikina Sports Center', 'philippinecolumbianassociation.com', 'class="cd"', 'class="sat"', '&t=k&',
  'sign up:', 'PSC Venue Reservation System', 'membership only', 'Gate 2 admin office',
  'Zheng Qinwen', 'Sinner effect', '27.3M players', '53,805 courts',
  'Philippine Tennis', '117K', 'TikTok', 'tennisph', 'National Tennis Centre',
]) {
  assert.ok(html.includes(term), `missing Philippines planning fact: ${term}`);
}

// Voice rules: no em dashes anywhere on the page.
assert.ok(!html.includes('—'), 'no em dashes on the page');

// External Choe archive citations stay absolute.
for (const id of [
  'saga1-episode-101-the-ranch-solo-series-part-one',
  'saga1-episode-119-the-ranch-solo-series-part-two',
  'saga2-saga-02-chapter-021-the-ranch-solo-series-3-the-lost-episode',
  '3QecMMrcCCA', '-wZk4B1BB0c', 'OP1mXscTUnw', 'zHyvVajsqMw'
]) assert.ok(html.includes(`${archiveBase}${id}`), `missing external archive source ${id}`);
assert.ok(!html.includes('../#/'), 'David archive links must not depend on repository nesting');

// The Choe accumulation survives in full.
const choeStart = html.indexOf('David Choe: repeated questions');
assert.ok(choeStart > -1, 'Choe accumulation must remain on the board');
assert.ok((html.slice(choeStart).match(/<li>/g) || []).length >= 30, 'Choe research sections must retain the full working accumulation');

// Every picture is cited; the board keeps at least seven plus the map.
assert.ok((html.match(/<figure/g) || []).length >= 8, 'board needs at least eight cited figures including the court map');
assert.ok((html.match(/<figcaption>/g) || []).length === (html.match(/<figure/g) || []).length, 'every figure needs a citation caption');

// The three-anchor tab is the only navigation; no generic UI structure.
for (const anchor of ['id="meetings"', 'id="philippines"', 'id="board"', 'href="#meetings"', 'href="#philippines"', 'href="#board"']) {
  assert.ok(html.includes(anchor), `missing tab anchor: ${anchor}`);
}
for (const forbidden of ['<header', '<nav', '<aside', '<section', '<table', '<details', '<button', 'class="card', 'FACT +', 'OPEN', 'useful work']) {
  assert.ok(!html.includes(forbidden), `forbidden site structure or status language: ${forbidden}`);
}
assert.doesNotMatch(html, /<h[1-6][^>]*>/i);

// One type size, black on white, no decorative chrome.
assert.match(css, /font-size:\s*15px/);
assert.equal((css.match(/font-size:/g) || []).length, 1, 'use one type size throughout');
assert.doesNotMatch(css, /--[a-z-]+:|position:\s*sticky|border:(?!\s*0(?:;|\s|}))|border-bottom|border-top|letter-spacing|text-transform|box-shadow|background:\s*#[^f]|color:\s*#[^0]/i);

// Source discipline.
assert.match(sources, /San Jose is not part of either exact claim/i);
assert.match(sources, /421 unique record IDs/i);
assert.match(sources, /173 review windows/i);
assert.match(sources, /Felicisimo Ampon/i);
assert.match(html, /href="SOURCES\.md"/);

console.log('single-page tennis project: to-do, meetings, Philippines planning, map, citations, and no-UI checks passed');
