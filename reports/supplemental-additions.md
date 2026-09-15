# Supplemental Pulmonary-Picture Additions

Validated September 14, 2026 (America/New_York). The self-contained supplement is stored in `/Users/chriselwell/Desktop/Pulmonary Picture Quiz App/source-additions`. It remains separate from the canonical RLS source library.

## Counts

- Scored supplemental sources: **51**
- Distinct supplemental source groups: **51**
- Exact SHA-256 duplicates against the RLS extractor manifest: **0**
- Modalities: **{'X-ray': 14, 'Ultrasound': 6, 'Clinical Image': 7, 'CT': 5, 'Flow-Volume Loop': 4, 'Diagram': 3, 'Histopathology': 2, 'Cytology': 2, 'Microscopy': 2, 'X-ray and CT': 2, 'Echocardiography': 1, 'EKG': 1, 'Gross pathology': 1, 'Histology': 1}**
- Openly licensed/public-domain web sources: **15**
- Local/user-supplied sources: **36**
- Reproducibly cropped or masked quiz variants: **15**
- Reproducible fixed frames extracted from licensed videos: **2**

## Safety and review

- Every displayed supplemental asset was visually inspected, including all fifteen additions from the full Pulm Pictures comparison.
- The 41 lecture picture manifests contributed 660 assignments representing 413 exact-hash-unique curated images; all 413 were reviewed on 12 contact sheets.
- Fixed lung-ultrasound frames preserve the original pixels, orientation, depth scale, and machine overlays; the source-video hash and exact frame time are retained.
- Flow-volume loops preserve axes, volume direction, curve relationships, and plotted pixels.
- The 12-lead ECG retains lead order, paper calibration, and the complete tracing.
- Answer-bearing title areas on two fungal teaching panels are removed by deterministic crops without altering the microscopic field.
- The user-supplied BPD radiograph is used without cropping or annotation; it contains no answer-bearing text, and its hash matches the independently curated local pulmonary image.
- No source uses generative reconstruction, upscaling, mirroring, or diagnostic-pixel alteration.
- Web records retain landing page, creator, license, original URL, and verified hash. Local lecture images remain for local study use only and must not be redistributed.

## Added records

| Source ID | Modality | Tested concept | Rights / use status |
|---|---|---|---|
| src_a7e4cc2e05f4 | Ultrasound | B-lines indicating an interstitial lung syndrome | CC BY-SA 4.0 |
| src_8bea84cf02b6 | Ultrasound | Seashore sign indicating normal lung sliding | CC BY-SA 4.0 |
| src_d0cb814f9b7c | Clinical Image | Flexible bronchoscopy | Public Domain Mark 1.0 (U.S. federal work) |
| src_5db8f6903dd8 | X-ray | Right thoracostomy tube for pneumothorax | CC BY-SA 4.0 |
| src_d32c93e07609 | X-ray | Central venous catheter | Public domain medical image (Poland) |
| src_5cd2489a4747 | Clinical Image | Water-seal chest drainage system | Public domain |
| src_410b1151df9a | Clinical Image | Omega-shaped epiglottis in laryngomalacia | Local study use only; do not redistribute |
| src_9ae2a8f227cf | Clinical Image | Bilateral vocal-fold nodules | Local study use only; do not redistribute |
| src_d3693d701478 | Flow-Volume Loop | Small-airway obstructive flow-volume loop | Local study use only; do not redistribute |
| src_786485b1c49d | Flow-Volume Loop | Fixed upper-airway obstruction | Local study use only; do not redistribute |
| src_ffd879524723 | Flow-Volume Loop | Variable intrathoracic obstruction | Local study use only; do not redistribute |
| src_990d2f41f813 | Flow-Volume Loop | Reversible airflow obstruction after bronchodilator | Local study use only; do not redistribute |
| src_aea7f471ff40 | Echocardiography | Right-ventricular pressure overload with septal flattening | Local study use only; do not redistribute |
| src_20ec92527bcf | EKG | Right-ventricular hypertrophy/strain pattern | Local study use only; do not redistribute |
| src_0187921345ca | Clinical Image | Diagnostic spirometry | Local study use only; do not redistribute |
| src_ccbde384bd8d | X-ray and CT | Golden S sign from right-upper-lobe collapse around a hilar mass | CC BY 4.0 |
| src_032b4d73373b | X-ray | Calcified pleural plaque from asbestos exposure | CC BY-SA 2.0 |
| src_06a2f9a827b4 | X-ray | Situs inversus totalis with dextrocardia | Local study use only; do not redistribute |
| src_f29bddb40fba | X-ray | Pulmonary arterial hypertension on chest radiograph | Local study use only; do not redistribute |
| src_abf82f7a5a47 | Diagram | Thoracentesis | Local study use only; do not redistribute |
| src_3e7254282ea9 | Ultrasound | Pleural effusion on lung ultrasound | CC BY 2.0 |
| src_34d6dde9a052 | Ultrasound | Lung consolidation with air bronchograms | CC BY 2.0 |
| src_22bd41dc4316 | X-ray | Right mainstem endotracheal-tube malposition | CC BY-SA 4.0 |
| src_bfbcd3fcfbcf | X-ray | Endotracheal and nasogastric tubes, both appropriately positioned | CC BY-SA 4.0 |
| src_ebcb300aedd3 | X-ray | Kerley B lines from interlobular septal thickening | CC0 1.0 |
| src_b7c3b9111e17 | Ultrasound | Barcode/stratosphere sign indicating absent lung sliding | CC BY 2.0 |
| src_04cb2634990f | Clinical Image | Obstructing endobronchial mass | CC BY 2.5 |
| src_ea8f6b047af1 | Histology | Pulmonary squamous cell carcinoma with keratin pearls | Local study use only; do not redistribute |
| src_e160390fdc2c | Cytology | Curschmann spiral from asthma | Local study use only; do not redistribute |
| src_3921a2dbb1b4 | Cytology | Charcot-Leyden crystal | Local study use only; do not redistribute |
| src_d4b43b5727a3 | Microscopy | Blastomyces with broad-based budding | Local study use only; do not redistribute |
| src_eaa014fe965d | Microscopy | Paracoccidioides with pilot-wheel budding | Local study use only; do not redistribute |
| src_73c4f1d588cf | Clinical Image | Oral candidiasis associated with inhaled corticosteroid use | Local study use only; do not redistribute |
| src_502d39947bf6 | Gross pathology | Asbestos-related fibrous pleural plaques | Local study use only; do not redistribute |
| src_fdfb0e719846 | Histopathology | Coccidioides spherule containing endospores | Local study use only; do not redistribute |
| src_f54f9aaba8d3 | X-ray | Acute epiglottitis with a thumb sign | Local study use only; do not redistribute |
| src_cc3113ff03a1 | Ultrasound | Acute deep venous thrombosis | Local study use only; do not redistribute |
| src_e3e49c513b78 | CT | Saddle pulmonary embolism | Local study use only; do not redistribute |
| src_f10dc0ed3c54 | X-ray | Pancoast tumor with chest-wall extension | Local study use only; do not redistribute |
| src_af562cd4c3c0 | X-ray | Left diaphragmatic rupture with bowel herniation | Local study use only; do not redistribute |
| src_05dd5b5c1bb8 | CT | Pulmonary contusion | Local study use only; do not redistribute |
| src_b18ecdbebbf7 | X-ray | Transient tachypnea of the newborn | Local study use only; do not redistribute |
| src_36c0d08aff1a | CT | Split pleura sign of empyema | Local study use only; do not redistribute |
| src_9ae5caa403ec | X-ray | Westermark sign | Local study use only; do not redistribute |
| src_1a9b3bbc92d7 | CT | Nonspecific interstitial pneumonia pattern | Local study use only; do not redistribute |
| src_ae47a756de82 | CT | Tree-in-bud pattern | Local study use only; do not redistribute |
| src_532a1d1b0074 | Histopathology | Pneumocystis jirovecii pneumonia | Local study use only; do not redistribute |
| src_e05b438bc25b | Diagram | Retropharyngeal abscess | Local study use only; do not redistribute |
| src_80b6767d705f | Diagram | Superior vena cava syndrome | Local study use only; do not redistribute |
| src_1203aba9ac08 | X-ray and CT | Traumatic hemothorax | Local study use only; do not redistribute |
| src_52ea07463a3a | X-ray | Bronchopulmonary dysplasia | Local study use only; do not redistribute |

## Source integrity

- Pulm Pictures audits remain identical: **2,195 files, 843,072,468 bytes, 0 changed/added/removed files**.
- The canonical RLS Pulmonary image/document set has **0 changed, added, or removed non-Finder files** versus the immediately prior audit.
- All added local images were copied into the separate supplemental library; the source root remains read-only.

## Review-item promotions

Six additional user-approved RLS review sources were copied into the app-local supplemental library and converted to reproducible quiz-safe variants. Effective scored supplemental records are now **57** (51 base additions + 6 promotions). See `review-promotions.md`.
