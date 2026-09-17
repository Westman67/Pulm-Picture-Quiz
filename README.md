# Pulmonary ID Lab

A local, offline-capable pulmonary visual-identification quiz rebuilt from every supported image in
`~/Desktop/Rename` and `~/Desktop/Add`. Both source collections are read-only. The app contains
separate, metadata-stripped derivatives with opaque browser paths (lossless PNG teaching originals,
visually-lossless WebP quiz-display copies for fast loading) and a schema-version-2 question bank.

## Start the completed build

No package installation is required. From Terminal:

```bash
cd "$HOME/Desktop/Pulmonary Picture Quiz App"
python3 scripts/serve.py 4173 dist
```

Then open <http://localhost:4173>. The app works with internet access disabled. On macOS you may
instead double-click `start.command`.

Do not open `index.html` through `file://`; browsers block the local JSON requests.

## Included

- Learn Mode with immediate feedback, visual clues, and four option-specific rationales
- Exam Mode with deferred results and rationales
- separate image-type and collection selectors, plus unseen, incorrect, marked, and mixed filters
- collections for `Rename collection`, `3rd Party` (Desktop/Add), and all pictures
- image categories for CXR, CT, All Imaging, Histology, and Gross
- lengths 10, 20, 40, all available, and endless practice
- persistent Back/Next navigation with unanswered skipping and restored draft/locked state
- zoom, pan, reset, teaching-original toggle, and keyboard controls (`1`–`4`, `Enter`, `Z`, arrows)
- local progress export/import/reset and a separate learner photo-quality flag queue
- reviewer-visible withheld sources that were not safe or specific enough for scored sessions

## Regenerate, validate, test, and build

The generator reads `~/Desktop/Rename` and `~/Desktop/Add` and never writes into either folder:

```bash
python3 scripts/generate_rename_bank.py
npm test
npm run build
```

Python 3 and Pillow are required. The app and automated JavaScript tests have no third-party npm
dependencies.

## Data and privacy

- All images are classified as `third_party`; the independent collection key identifies either
  `Rename collection` or `3rd Party`.
- Rights are unknown, so the collection and app are restricted to local study use and must not be
  published or redistributed.
- Learner progress and photo flags stay in browser `localStorage` unless explicitly exported.
- Source filenames appear only after Learn submission, Exam completion, or in reviewer mode.
- Client-side answer hiding is an interface safeguard, not cryptographic secrecy.

## Project outputs

- `reports/preflight-audit.md`, `reports/source-audit-rename.json`, and `reports/source-audit-add.json`
- `data/source-manifest.json`
- `data/question-bank.json`
- `data/review-queue.json`
- `public/assets/images/`
- `dist/` production build
