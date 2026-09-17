# Explanation / Choice-Rationale Source Provenance

This document tracks which lecture source grounds each `FEATURE_RULES` entry
or `CONCEPT_SYNONYM_GROUPS` merge added during the "improve answer
explanations using lecture material" pass (per user request, "Full pass, flag
for review after" approach). It exists to satisfy the citation requirement:
every non-generic clue text introduced in this pass should trace back to a
specific lecture file and page, or be flagged as an unverified
same-finding/different-label synonym merge with no distinguishing content
claimed.

Lecture files live under `Desktop/Pulm/Lectures/` on the user's machine
(paths below are relative to that folder). All page numbers refer to the RLS
(Reduced Lecture Slides) PDF unless noted otherwise.

## Grounded FEATURE_RULES entries (new distinguishing clue text)

| Concept(s) | Lecture source | Page(s) | Grounded fact used |
|---|---|---|---|
| Bronchiectasis (situs inversus, CF, chronic bronchitis, squamous metaplasia, fibrosis/inflammation variants) | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases RLS | 65-78 | Pathogenesis (fibrosis/inflammation/cartilage loss, squamous metaplasia, dilated airways) and gross description (dilated, tortuous, collapsible airways extending to pleura; CF as prototypical cause) |
| Sarcoidosis (Schaumann bodies, erythema nodosum, adenopathy, lymphangitic granuloma, BAL) | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease RLS | 41-51 | Asteroid vs Schaumann/conchoidal body distinction; lymphangitic granuloma distribution; erythema nodosum as extrapulmonary finding; bilateral hilar/mediastinal adenopathy; BAL lymphocyte-predominant + giant cells |
| Saddle PE (lines of Zahn), wedge-shaped PE infarct, bilateral emboli | P26.1 Diseases of the Respiratory Tract - Part 3 - Vascular/Cancer/Other RLS | 49, 53 | "Pulmonary Saddle Embolism" with lines of Zahn description; wedge-shaped pulmonary infarct |
| Pink Puffer phenotype vs generic hyperinflation/COPD | P19 RLS | 61 | "Pink puffer" (dyspneic/tachypneic, gas exchange maintained) vs "blue bloater" (hypoxemic/hypercapnic) phenotype table |
| Asbestosis vs asbestos-related pleural plaque | P24 RLS | 33, 36 | Pleural disease (plaques, marker of exposure) vs interstitial lung disease/asbestosis (subpleural, lower-lung fibrosis + ferruginous bodies) listed as separate disease categories |
| ARDS hyaline membrane vs neonatal RDS | P26.1 RLS | 73-78 | Exudative-phase DAD (days 3-7 post-insult: infection, sepsis, shock, trauma) with hyaline membranes -- adult/insult-triggered pattern. (Neonatal RDS pathophysiology/surfactant-deficiency mechanism was **not found** in any lecture searched; the neonatal entry is differentiated only by population/clinical-entity framing, not by an asserted distinct mechanism, to avoid fabricating unsourced content.) |
| Pneumonia histologic phases: congestion / red hepatization / gray hepatization | P31 Review of Pneumonia (Pathology/Pharmacology) RLS | 16, 18, 20 | Congestion (mild edema, capillary congestion, few neutrophils) -> Red hepatization (dense, liver-like, neutrophils+RBCs) -> Gray hepatization (RBC lysis, fibrin deposition, progression to organizing pneumonia) |
| Hematogenous vs lymphangitic metastatic spread | (pattern reused from sarcoidosis lymphangitic-granuloma grounding, P24 RLS p.41-51) | -- | Lymphatic-route distribution (bronchovascular bundles, interlobular septa, subpleural) vs blood-borne nodular spread is the same established anatomic-route logic already grounded for granulomas; applied here to metastases as the standard radiologic-pathologic distinction, not from a metastasis-specific lecture page |
| Extralobar vs intralobar pulmonary sequestration | P36 Pulmonary Developmental Anomalies RLS | 40 | Extralobar: own pleura, systemic venous drainage, infancy presentation. Intralobar: shares visceral pleura, pulmonary venous drainage, later childhood/adolescence presentation |
| Plexiform lesion vs generic pulmonary hypertension | P26.1 RLS | 57, 63, 66 | Heath-Edwards classification (plexiform lesion = advanced glomeruloid endothelial-proliferation finding); PHTN complications (RVH/cor pulmonale) |
| Goodpasture vs generic alveolar hemorrhage | P26.1 RLS | 68-69 | Goodpasture: anti-GBM antibodies (anti-type IV collagen), linear IF staining, necrotizing GN -- distinguishes it from the broader "alveolar hemorrhage" category, which the same page lists as also including GPA, microscopic polyangiitis, SLE, and idiopathic pulmonary hemosiderosis |
| Mesothelioma histologic subtypes noted (not yet split into distinct clues; epithelioid/sarcomatoid already had separate concept labels pre-pass) | P26.1 RLS | 40-44 | 3 histologic subtypes (epithelial, sarcomatoid/spindle, biphasic); asbestos link; IHC marker table (calretinin, D2-40) |
| LLL/RLL vs RML/lingula silhouette sign | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | (silhouette sign slide, page not numbered in extracted text) | "RML/Lingula -- Silhouette the heart" vs "Lower Lobes -- Silhouette the diaphragms" |
| Cardiogenic vs noncardiogenic pulmonary edema (reference table, not yet consumed into a new FEATURE_RULES split this pass) | P26.1 RLS | 83 | Distinguishing table: pulmonary capillary pressure, permeability, edema protein content, distribution, pleural effusion frequency |

## Synonym merges (same underlying finding under different image/source labels, no distinguishing content claimed)

These were merged in `CONCEPT_SYNONYM_GROUPS` rather than given distinct
explanation text, because no lecture source was found that describes a
radiographically/histologically distinguishing feature between the merged
labels -- they are treated as the same finding described at different
specificity or from different source images:

- Cardiogenic Pulmonary Edema + Congestive Heart Failure Stage III (Alveolar Edema)
- Atypical Pneumonia + Mycoplasma Pneumonia (mycoplasma is lecture-named as one cause of the "atypical pneumonia" category, P31 RLS p.21; no separate radiographic description given)
- Bacterial Pneumonia + Community Acquired Pneumonia
- Centriacinar Emphysema + Centri-acinar Emphysema Secondary Pneumonia
- Mesothelioma + Pleural mesothelioma + Malignant pleural mesothelioma + Mesothelioma Encasing Lung
- Hematogenous Metastatic Spread + Multiple hematogenous metastases (literal wording variants)
- Peripheral Tumor + Primary lung cancer + Non-Small Cell Lung Cancer (no source-image-specific distinguishing content found)
- Bronchiectasis + Bronchiectasis Lung Specimens + Bronchiectasis Right Lung Saggital (same gross finding, different specimen/orientation labels)
- Silicosis + Circumscribed silicotic nodule from silicosis
- Lung mass + Left hilar lung mass + Lung nodule (undifferentiated focal lesion labels)
- Emphysema + Hyperinflation in COPD + Severe COPD (hyperinflation is emphysema's radiographic manifestation, per P19 RLS p.47-64)

## Known remaining gaps (not fixed this pass)

As of the last duplicate-clue scan (5 questions remaining, down from 133 at
the start of this pass), these clusters still share identical auto-generated
rationale text and were left unresolved because no lecture grounding was
located for a distinguishing feature:

- Ankylosing Spondylitis / Kyphosis / Scoliosis triad (chest-wall restrictive mechanics) -- these are three legitimately different diagnoses; distinguishing content would need a specific musculoskeletal/rheumatology lecture page not yet located.
- CPAM subtype cluster (CPAM Type 3 / CPAM and Emphysema / Type 4 CPAM vs pleuropulmonary blastoma / CPAM with pulmonary sequestration / Large CPAM with right lung hyperinflation) -- P36 RLS has partial CPAM-type content (e.g. p.28-31) but not a full Type 1-4 comparison table; needs a follow-up read of the full CPAM section before either merging or writing distinguishing clues.

## Methodology note

For each cluster, the fix was verified by: (1) reading the concept strings
programmatically from `data/question-bank.json` rather than guessing, (2)
extracting lecture text via `pypdf`/`pdftotext` and confirming the grounding
fact is actually present on the cited page, (3) regenerating the bank and
re-running a duplicate-clue scan (`feature_for()` applied to all 4 options of
every question) to confirm the fix took effect, (4) re-running
`scripts/validate_bank.py` (must show `PASS`) and the Node test suite (must
show 17/17) before committing.
