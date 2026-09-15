# Pulmonary Picture Quiz Preflight Audit

Generated: 2026-09-14T23:22:30-04:00

## Scope

- Canonical upstream library: `/Users/chriselwell/Desktop/Picture Quiz` (read-only)
- Supplemental pulmonary-picture library: `/Users/chriselwell/Desktop/Pulmonary Picture Quiz App/source-additions` (read-only during quiz build)
- Audited collection: `/Users/chriselwell/Desktop/Picture Quiz/Pulmonary`
- Output project: `/Users/chriselwell/Desktop/Pulmonary Picture Quiz App`
- Quiz format: image-identification, one scored task per selected source/concept

## Upstream validation summary

- Extractor: `rls-picture-quiz-extractor` version 1
- Upstream manifest generated: 2026-09-12T13:38:43-04:00
- Manifest records: 555
- Active records: 540
- Active status counts: {'REFERENCE_ONLY': 285, 'USABLE': 252, 'EXCLUDED': 3}
- Active, high-confidence, scored-eligible candidates before downstream review: 252
- Source-document hashes were independently checked before this build: 37/37 matched.
- Extractor states were independently checked before this build: 38 complete, 1,995 slides inspected.

## Downstream ID gate

- Activated questions: 228
- Active third-party Pulm Pictures questions: 47
- Source additions represented before quality review: 65
- Distinct activated source groups: 228
- Manual-review exclusions: 0
- Learner-flagged items audited: 153
- Learner-flagged items removed from scoring: 56
- Learner-flagged images retained with local crop/trim: 97
- Repeated modality/answer concepts not duplicated in the bank: 14
- Question bank schema: 2
- Every item has four unique options and four index-aligned rationales.

## Activated questions by modality

- X-ray: 62
- CT: 30
- Histopathology: 29
- Gross Pathology: 17
- Histology: 15
- Clinical Image: 14
- Graph: 12
- Flow-Volume Loop: 7
- Other: 6
- Diagram: 5
- X-ray and CT: 4
- Angiography: 3
- Gross pathology: 3
- Microscopy: 3
- Ultrasound: 3
- Nuclear Imaging: 2
- Micrograph: 2
- Cytology: 2
- Gross Anatomy: 1
- Gross pathology and histology: 1
- Electron Microscopy: 1
- Map: 1
- MRI: 1
- Echocardiography: 1
- EKG: 1
- Immunohistochemistry: 1
- X-ray and pathology: 1

## Safety decisions

- Learner-facing assets use opaque hashed names.
- Images are losslessly re-encoded from decoded pixels to strip embedded metadata.
- Transparent pixels are composited onto a controlled neutral background.
- No image is upscaled, mirrored, recolored, or generatively altered.
- Source filenames, lecture names, pages, originals, and rationales remain hidden before Learn submission and Exam completion.
- Upstream `REFERENCE_ONLY`, `EXCLUDED`, inactive, broken, duplicate, and review-only records are not scored.
- Client-side answer hiding is interface behavior, not cryptographic secrecy.

## Limitations

- Distractors were selected deterministically from modality- and category-aligned, lecture-verified source records.
- 0 visually labeled or text-dependent candidates remain in the local builder review queue.
- The completed learner-flag batch is recorded in `quality-review-2026-09-15.json`; excluded records retain lineage but are not scored.
- The build preserves the upstream medical ground truth; it does not reinterpret RLS content from filenames.
