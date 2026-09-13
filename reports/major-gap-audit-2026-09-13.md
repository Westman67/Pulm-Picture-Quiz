# Major Visual-Coverage Gap Audit

Audited September 13, 2026 (America/New_York).

## Result

The scored bank increased from **239 to 246** questions. I added **7** sources only where the image is necessary, the visible evidence is sufficient, the key is medically defensible, and the source rights/provenance are explicit. The **19** review-only records remain excluded from scored sessions.

## Gaps filled

| Priority gap | Before | Added coverage |
|---|---:|---|
| Abnormal lung ultrasound | 0 pleural-effusion, 0 consolidation, 0 pneumothorax M-mode items | Pleural effusion; consolidation with air bronchograms; barcode/stratosphere sign |
| Airway and enteric tubes | 0 ETT and 0 NG/enteric-tube items | Right-mainstem ETT malposition; appropriately positioned ETT plus NG tube |
| Interstitial edema sign on CXR | 0 Kerley B-line items | Kerley B lines from interlobular septal thickening |
| Pathologic bronchoscopy | 0 internal airway-lesion items | Obstructing endobronchial mass, keyed only to the visible finding—not histology |

After the additions, the bank contains **5 ultrasound** questions and **70 X-ray** questions. The new bronchoscopy item adds the first scored endobronchial-lesion view.

## Deliberately not added

- **Dynamic lung point:** not converted to a static quiz because the required respiratory transition is not defensible from one still frame.
- **Foreign-body bronchoscopy:** no reviewed candidate met both the rights and unambiguous one-best-answer gates.
- **Cyanosis, barrel chest, and tracheal-deviation photographs:** deferred because of low image specificity, patient-identifiability concerns, or limited incremental value.
- **More echocardiography views:** the bank already contains a verified RV pressure-overload item; more should be added only if explicitly course-tested and source-verified.

## Duplicate and leakage checks

- Exact duplicates within the 27-record supplement: **0**.
- Exact supplemental matches to the RLS manifest: **0**.
- Likely perceptual duplicates among the seven new scored assets at a 64-bit dHash distance of 4 or less: **0**.
- New images have opaque learner-facing filenames and neutral alt text.
- Creator, license, landing page, original, and rationales remain hidden until feedback is available.

## Verification

- Manifest/question-bank validator: **PASS**.
- Automated tests: **12/12 PASS**.
- Production build: **PASS**.
- Desktop/mobile Learn and Exam review: **PASS**.
- Targeted render/reveal checks for the new ultrasound, lines/tubes, Kerley B-line, and bronchoscopy items: **PASS**.

See `reports/contact-sheets/major-gap-additions-2026-09-13.jpg` and `reports/visual-review/visual-check-gaps.json`.
