# Tom / Jerry Tennis

Public working material for Jerry Shi and Tom Oh's tennis-culture project.

## Repository boundary

This repository owns:

- `tennis-culture/` — the Jerry / Tom working board and Mike Cherman interview research.
- `tom-handoff/` — Tom's public Mike-facing handoff site.
- `scripts/build_mike_cherman_notes.py` — reproducible Mike interview-page generator.
- `tests/tennis-culture.test.mjs` — standalone content and repository-boundary checks.

This repository does **not** own David Choe transcripts, transcript analysis, archive data, or the David Choe reader. Those remain in [`jerryshi042003/david-choe-transcript-archive`](https://github.com/jerryshi042003/david-choe-transcript-archive).

Tom's separate portfolio-style site remains in [`jerryshi042003/tom-oh-tennis`](https://github.com/jerryshi042003/tom-oh-tennis).

## Deployment boundary

- Jerry / Tom working board: existing `tennis-culture` deployment.
- Tom → Mike handoff: existing `tom-mike-handoff` Vercel deployment.

The existing public URLs stay in place during migration. Production is changed only after the corresponding page is reproduced from this repository and passes the same local and live checks.

## Validation

Run:

```sh
python3 scripts/check_site.py
node tests/tennis-culture.test.mjs
(cd tom-handoff && node scripts/check.mjs)
```

The validator rejects missing local links/assets, private machine paths, downloaded audio/video, and any accidental David Choe transcript payload.
