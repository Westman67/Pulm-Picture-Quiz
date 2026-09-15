# Pulmonary ID Lab

An offline-capable, local browser application for pulmonary image-identification practice. The
upstream Picture Quiz library is read-only; this project contains separate, metadata-stripped display
derivatives and a schema-version-2 question bank.

The completed bank contains **220 scored questions**: 181 lecture questions and 39 third-party Pulm
Pictures questions. A completed 153-flag quality-review batch removed 56 irreparable items and retained
97 with project-local crops or neutral-border trims; the original RLS and Pulm Pictures collections
were not modified.

## Included

- Learn Mode with immediate feedback, visual clues, and four option-specific rationales
- Exam Mode with deferred scoring and rationales
- category, unseen, incorrect, marked, and mixed filters
- picture-source filtering for the 181 lecture questions or 39 third-party Pulm Pictures additions
- lengths 10, 20, 40, all available, and endless practice
- persistent Back/Next navigation with unanswered skipping and restored draft/locked state
- an in-quiz **Flag bad photo** form with quick issue categories and an optional note
- a separate local photo-fix queue with open/fixed status, stable source IDs, and JSON export
- keyboard controls: `1`–`4`, `Enter`, `Z`, `←`, and `→`
- zoom, pan, reset, and teaching-original toggle
- source-group/concept-aware local progress with export/import/reset
- empty manual-review queue; 13 review-only items were removed and 6 were promoted with safe variants

## Start the completed build

No package installation is required. From Terminal:

```bash
cd "$HOME/Desktop/Pulmonary Picture Quiz App"
python3 -m http.server 4173 -d dist
```

Then open <http://localhost:4173>. Internet access may be disabled; all runtime files are local.
Do not open `index.html` through `file://`, because browsers block the local JSON requests.

On macOS, you may instead double-click `start.command`. If Gatekeeper blocks it, right-click it and
choose **Open**, or run the Terminal command above.

## Development preview

```bash
cd "$HOME/Desktop/Pulmonary Picture Quiz App"
python3 -m http.server 4173
```

## Regenerate, test, and build

Regeneration reads the canonical RLS library from `~/Desktop/Picture Quiz` and the self-contained
supplemental library from `source-additions/`. It never writes into the canonical RLS library:

```bash
python3 scripts/generate_bank.py
npm test
npm run build
```

The generator requires Python 3 and Pillow. The application and tests use no third-party JavaScript
dependencies.

`npm test` runs the project-local fail-closed bank and image validator before the unit suite. The
optional `npm run test:visual` command requires the local server to be running and exercises desktop,
mobile, Learn/Exam, skip/Back restoration, and the newly added questions in headless Chrome.

## Data and privacy

- Quiz assets have opaque hashed filenames and stripped metadata.
- Source filenames and lecture provenance appear only after Learn submission, Exam completion, or in
  reviewer mode.
- Openly licensed supplemental images show creator, license, and verified landing-page attribution
  only after feedback becomes available.
- Learner progress remains in browser `localStorage` unless explicitly exported.
- Photo-quality flags are stored separately from study marks and quiz progress; resetting progress does
  not erase them. Use **Review & flags** to mark fixes complete, reopen them, or export the queue.
- Flags covered by a completed review batch resolve automatically once after the updated bank loads;
  a flag that the learner deliberately reopens remains open.
- Client-side answer hiding is an interface safeguard, not cryptographic secrecy.
- Third-party educational images must remain local and must not be redistributed.

## Project outputs

- `reports/preflight-audit.md` and `reports/source-audit.json`
- `reports/quality-flag-remediation-2026-09-15.md` and `source-additions/quality-review-2026-09-15.json`
- `reports/supplemental-additions.md`, `reports/pulm-pictures-audit/`, `reports/pulm-pictures-full-comparison-2026-09-14/`, and `reports/review-queue/`
- `data/source-manifest.json`
- `data/question-bank.json`
- `data/review-queue.json`
- `public/assets/images/`
- `dist/` production build
