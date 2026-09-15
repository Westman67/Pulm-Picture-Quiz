# Pulm Pictures → Pulmonary Picture Quiz full comparison

Generated: 2026-09-14T20:41:12-04:00

## Outcome

- Reviewed all 2,109 valid images in `/Users/chriselwell/Desktop/Pulm/Pulm Pictures/Pulm Picture` recursively, including 1,423 exact-unique top-level files.
- Reconciled the earlier 413-image curated audit and visually inspected all 1,012 newly surfaced top-level candidates across 41 contact sheets.
- Compared all 183 Finder-tagged app assets (146 scored questions) against their teaching originals across 13 paired contact sheets.
- Added 15 image-first, nonredundant scored questions across two focused curation passes. The bank increased from 261 to 276 questions.
- Assigned the remaining 997 newly reviewed candidates to `REFERENCE_ONLY`; nothing was deleted from the source collection.

## Added scored questions

| Concept | Question ID | Why it earned a scored slot |
|---|---|---|
| Acute epiglottitis with a thumb sign | `q_5bfda1e68918` | Clean, complete lateral neck radiograph with a directly testable visual sign and matching P33 lecture context. |
| Acute deep venous thrombosis | `q_4c4d3558ad74` | Paired compression-ultrasound panels make noncompressibility visually decisive; only the answer title was cropped. |
| Saddle pulmonary embolism | `q_c5909e0f0017` | Complete axial CTPA image clearly localizes thrombus across the pulmonary-artery bifurcation and aligns with P26. |
| Pancoast tumor with chest-wall extension | `q_96f7b3d4be63` | Complete chest radiograph and overlay distinguish a superior-sulcus mass with local invasion from a generic apical opacity. |
| Left diaphragmatic rupture with bowel herniation | `q_4059823e919e` | Intrathoracic bowel loops and mediastinal shift provide a discriminating radiographic task; only the answer title was removed. |
| Pulmonary contusion | `q_69b0a713ddbd` | The complete unannotated sagittal CT panel shows a peripheral nonlobar traumatic opacity without redundant answer-labeled material. |
| Transient tachypnea of the newborn | `q_258da53caab0` | The complete unannotated neonatal radiograph shows hyperinflation, perihilar streaking, and fissural fluid in a useful neonatal differential. |
| Split pleura sign of empyema | `q_f2d764e078f0` | Complete contrast-enhanced CT makes separation of the enhancing pleural layers by a lentiform collection visually decisive. |
| Westermark sign | `q_ea64902d3274` | The retained comparison radiographs and magnified regions directly demonstrate abrupt pulmonary-artery cutoff with distal oligemia. |
| Nonspecific interstitial pneumonia pattern | `q_acf504733555` | Complete HRCT adds a distinct fibrotic pattern through symmetric ground glass, fine reticulation, traction change, and relative subpleural sparing. |
| Tree-in-bud pattern | `q_9aebde0f198d` | A reproducible title-and-label crop preserves the complete CT and magnified inset needed to recognize branching centrilobular nodules. |
| Pneumocystis jirovecii pneumonia | `q_0f55c8f39a6f` | Paired H&E and silver-stained sections jointly show foamy intra-alveolar exudate and crescentic cyst forms after the answer title is removed. |
| Retropharyngeal abscess | `q_3de250d13643` | The diagnosis label is masked while the complete sagittal anatomy and highlighted posterior pharyngeal-space collection remain visible. |
| Superior vena cava syndrome | `q_623e3a884053` | The two-part diagram jointly depicts central thoracic venous obstruction and the characteristic upper-body venous-congestion findings. |
| Traumatic hemothorax | `q_1c5effc65e64` | The answer-title crop retains paired supine radiograph and CT panels that jointly localize hyperattenuating blood to the pleural space. |

## Notable candidates retained as reference only

- Hampton hump: useful teaching example, but the available composite visibly states the diagnosis and duplicates an already deep pulmonary-embolism section.
- Lupus pernio: recognizable, but the facial photograph is patient-identifiable and adds less pulmonary-image value than the selected radiology and ultrasound gaps.
- Clinical DVT photograph: answer-labeled and less discriminating than the selected paired compression-ultrasound study.
- Additional neonatal, trauma, and meconium examples: retained when titles, arrows, redundant duplicate panels, or weaker differential value made them inferior to the selected variants.
- Large groups of tables, algorithms, labeled reference diagrams, and repeated chest-radiograph patterns remain available in the source library but were not forced into an image-identification format.

## App-wide changes

- Replaced the six dominant generic stem templates with modality-specific tasks; jointly tested composites now say that all panels are considered together.
- Added `case_context`, `visual_target`, `panel_handling`, and `joint_images` metadata to learner-facing questions.
- Rewrote generated rationales as concise, image-specific contrasts for every option.
- Added persistent Back and Next controls, free navigation without forced submission, per-question draft preservation, and retained locked answers/feedback on revisit.
- Final scoring distinguishes correct, incorrect, and unanswered questions; unanswered items can be retried.
- Added independent picture-source filtering for 225 lecture questions or 51 third-party Pulm Pictures additions.
- Added a persistent in-quiz bad-photo flag workflow with an open/fixed review queue and JSON export.
- Added a fail-closed validation gate for source lineage, four-choice contracts, visual targets, opaque paths, readable PNGs, and asset-map consistency.

## Verification

- Source integrity: 2109 images before and 2109 after; 0 added, 0 removed, 0 hash changes.
- Finder tags after rebuild: {'Red': 183, 'Orange': 1} (the prior 183 red-tagged assets remain tagged).
- Static/unit tests: 15 passed.
- Browser checks: baseline desktop/mobile, existing gap items, all 15 full-comparison additions, Learn/Exam reveal timing, zoom, answer locking, skip/Back draft restoration, source filtering, photo flags, and final results all passed.
- Production build validation: PASS.

## Audit artifacts

- Per-candidate disposition: `/Users/chriselwell/Desktop/Pulmonary Picture Quiz App/reports/pulm-pictures-full-comparison-2026-09-14/new-source-candidate-disposition.csv`
- Machine-readable audit: `/Users/chriselwell/Desktop/Pulmonary Picture Quiz App/reports/pulm-pictures-full-comparison-2026-09-14/audit.json`
- Candidate sheets: `/Users/chriselwell/Documents/Codex/2026-09-14/ca-2/work/full-audit/review-sets/new-source-candidates`
- Red-tag original/quiz pairs: `/Users/chriselwell/Documents/Codex/2026-09-14/ca-2/work/full-audit/review-sets/red-tag-pairs`
