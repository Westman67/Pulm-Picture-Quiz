# Pulmonary ID Lab

An offline-capable, local browser application for pulmonary image-identification practice. The
upstream Picture Quiz library is read-only; this project contains separate, metadata-stripped display
derivatives and a schema-version-2 question bank.

The completed bank contains **258 scored questions**. Thirty-nine are supplemental pulmonary-picture
questions added from a separate, versioned source library; the original RLS and Pulm Pictures
collections were not modified.

## Included

- Learn Mode with immediate feedback, visual clues, and four option-specific rationales
- Exam Mode with deferred scoring and rationales
- category, unseen, incorrect, marked, and mixed filters
- lengths 10, 20, 40, all available, and endless practice
- keyboard controls: `1`–`4`, `Enter`, and `Z`
- zoom, pan, reset, and teaching-original toggle
- source-group/concept-aware local progress with export/import/reset
- manual review queue excluded from scoring (13 items remain; 6 were promoted with safe variants)

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
python3 "$HOME/.codex/skills/build-medical-picture-quiz/scripts/validate_bank.py" \
  data/source-manifest.json data/question-bank.json
node --test tests/*.test.mjs
node scripts/build.mjs
```

The generator requires Python 3 and Pillow. The application and tests use no third-party JavaScript
dependencies.

## Data and privacy

- Quiz assets have opaque hashed filenames and stripped metadata.
- Source filenames and lecture provenance appear only after Learn submission, Exam completion, or in
  reviewer mode.
- Openly licensed supplemental images show creator, license, and verified landing-page attribution
  only after feedback becomes available.
- Learner progress remains in browser `localStorage` unless explicitly exported.
- Client-side answer hiding is an interface safeguard, not cryptographic secrecy.
- Third-party educational images must remain local and must not be redistributed.

## Project outputs

- `reports/preflight-audit.md` and `reports/source-audit.json`
- `reports/supplemental-additions.md`, `reports/pulm-pictures-audit/`, and `reports/review-queue/`
- `data/source-manifest.json`
- `data/question-bank.json`
- `data/review-queue.json`
- `public/assets/images/`
- `dist/` production build
