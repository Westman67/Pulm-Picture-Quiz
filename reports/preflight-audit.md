# Pulmonary Picture Quiz Preflight Audit

Generated: 2026-09-14T20:40:55-04:00

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

- Activated questions: 276
- New pulmonary-picture additions: 57
- Distinct activated source groups: 276
- Manual-review exclusions: 0
- Repeated modality/answer concepts not duplicated in the bank: 14
- Question bank schema: 2
- Every item has four unique options and four index-aligned rationales.

## Activated questions by modality

- X-ray: 77
- CT: 33
- Histopathology: 29
- Clinical Image: 25
- Gross Pathology: 19
- Histology: 17
- Graph: 15
- Flow-Volume Loop: 8
- Ultrasound: 7
- Other: 6
- Diagram: 6
- Angiography: 4
- Gross pathology: 4
- X-ray and CT: 4
- Micrograph: 3
- Microscopy: 3
- Nuclear Imaging: 2
- Cytology: 2
- Gross Anatomy: 1
- Gross pathology and histology: 1
- CT and diagram: 1
- CT and PET-CT: 1
- Micrograph and CT: 1
- Culture and clinical specimen: 1
- Electron Microscopy: 1
- Map: 1
- MRI: 1
- Echocardiography: 1
- EKG: 1
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
- 0 visually labeled or text-dependent candidates remain in the local review queue; six user-approved sources were promoted through reproducible local crops or opaque masks.
- The build preserves the upstream medical ground truth; it does not reinterpret RLS content from filenames.
