# Final Validation

Validated September 13, 2026 (America/New_York).

## Source integrity

- Initial and final Pulmonary audits each contain 879 files and 947,428,047 bytes.
- File-by-file SHA-256 comparison: **0 changed, added, or removed source files**.
- Referenced RLS documents: **37/37 hashes unchanged**.
- Upstream extractor manifest: **PASS** — 555 records and 111 variants, with no errors or warnings.

## Bank

- Schema version: **2**
- Scored image-identification questions: **219**
- Distinct scored source groups: **219**
- Manual-review exclusions: **19**
- Repeated modality/answer concepts withheld: **14**
- Builder manifest/bank validator: **PASS**
- Four unique options and four non-empty, index-aligned rationales: **PASS**
- Key/distractor containment check: **PASS**

## Application

- Automated tests: **12 passed, 0 failed**
- Production build: **PASS**
- Desktop and mobile visual checks: **PASS**
- Learn rationale timing: **PASS**
- Exam rationale timing: **PASS**
- Locked answers and deterministic scoring: **PASS**
- Zoom control and representative asset rendering: **PASS**
- Exam results and review cards: **PASS**

Representative screenshots and the machine-readable result are stored in `reports/visual-review/`.
