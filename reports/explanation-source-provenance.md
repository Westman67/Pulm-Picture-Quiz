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

## Follow-up pass (closed the remaining gaps)

The two gaps below were resolved in a follow-up verification pass:

| Concept(s) | Lecture source | Page(s) | Grounded fact used |
|---|---|---|---|
| Ankylosing Spondylitis vs Kyphosis vs Scoliosis | P25 Radiology Restrictive Diseases RLS | (Causes of Scoliosis / Causes of Kyphosis slide) | Scoliosis = lateral curvature (Marfan, Down syndrome, Ehlers-Danlos, muscular dystrophy, idiopathic). Kyphosis = anteroposterior curvature, with Ankylosing Spondylitis listed as one of several specific causes (others: Scheuermann's disease, compression fracture, arthritis). Ankylosing Spondylitis itself = seronegative spondyloarthropathy causing spinal/SI-joint fusion ("bamboo spine"), a specific radiographic marker distinct from generic kyphosis. |
| CPAM Type 3 vs Type 4 CPAM/PPB vs CPAM+sequestration vs CPAM+emphysema vs large CPAM+hyperinflation | P36 Pulmonary Developmental Anomalies RLS | (Stocker CPAM Type classification slide; case vignette slides) | Stocker Type 3 = bronchiolar/alveolar-duct architecture, CXR resembling pneumonia in an infant (case vignette). Type 4 = large cysts lined by alveolar type I/II cells, with a recognized spectrum/overlap concern with pleuropulmonary blastoma if septal stroma is focally hypercellular. "CPAM with pulmonary sequestration" = a distinct hybrid lesion (multicystic + systemically-supplied sequestered tissue) from a separate case vignette (atelectasis + bronchiectasis on CT). "Large CPAM with right lung hyperinflation" = a single very large lesion causing mass effect, per its own case vignette. "CPAM and Emphysema" = a co-occurrence label with no specified Stocker subtype. **Correction**: the pre-pass `CONCEPT_SYNONYM_GROUPS` had incorrectly merged "CPAM Type 3" with "Type 4 CPAM versus pleuropulmonary blastoma" as synonyms -- these are different Stocker subtypes with different histology and prognosis (same class of error as the earlier Ghon-complex/Cavitary-TB mistake caught in an earlier pass); the merge was removed and both given distinct grounded clue text instead. |

Duplicate-clue questions after this follow-up pass: **0** (all 544 scored questions have 4 options that each resolve to a distinct auto-generated rationale clue).

## Methodology note

For each cluster, the fix was verified by: (1) reading the concept strings
programmatically from `data/question-bank.json` rather than guessing, (2)
extracting lecture text via `pypdf`/`pdftotext` and confirming the grounding
fact is actually present on the cited page, (3) regenerating the bank and
re-running a duplicate-clue scan (`feature_for()` applied to all 4 options of
every question) to confirm the fix took effect, (4) re-running
`scripts/validate_bank.py` (must show `PASS`) and the Node test suite (must
show 17/17) before committing.

## Comprehensive completion pass

Following a user request to "complete all the answer explanations," a deeper
audit was run beyond the live per-question duplicate scan: for all 365
distinct concepts in the bank, every pair that resolves to the *same*
auto-generated clue text was checked for whether it is also blocked from
co-occurring as distractors via `CONCEPT_SYNONYM_GROUPS` (a "latent"
duplicate -- one that hasn't shown up in the current question pool only by
chance of topic/family bucketing, not because it's actually been resolved).
This surfaced several real regex-ordering bugs and a large set of legitimate
same-finding/different-label pairs that had not yet been merged. Also
confirmed: 0 of 365 concepts fall through to the generic per-modality
fallback text (every concept matches a specific `FEATURE_RULES` entry).

### Regex-ordering bugs fixed (wrong text, unrelated to lecture content)

- `paracoccidio` was being swallowed by the broader `coccidio` match, so
  Paracoccidioidomycosis got the Coccidioides spherule description instead
  of its own pilot-wheel budding description -- reordered.
- `lymphoma` (mediastinal mass compressing the trachea) was being swallowed
  by the generic `trachea` (normal anatomy) match for "Lymphoma Compressing
  Trachea" -- reordered so the pathologic finding takes precedence over the
  normal-anatomy label.
- The UIP/honeycomb-specific rule added earlier in this pass was itself
  being swallowed by the generic `interstitial pneumonia` catch-all because
  it was positioned after it -- moved earlier so "Usual Interstitial
  Pneumonia" resolves to the UIP-specific text rather than the generic
  interstitial-pneumonia text.
- A pre-existing `pulmonary arterial hypertension` rule (older, generic)
  was intercepting both "Plexiform Lesion..." and bare "Pulmonary arterial
  hypertension" before they could reach this pass's plexiform/PAH split;
  removed the redundant rule and widened the generic PAH pattern to
  `pulmonary (arterial )?hypertension` so it still catches the "arterial"
  wording.
- Kerley-B/interstitial-stage cardiogenic edema was sharing the generic
  `cardiogenic|congestive heart failure|kerley` clue with alveolar-stage
  cardiogenic edema despite "kerley" being in the pattern; split into two
  rules (interstitial-stage vs alveolar-stage) using the CHF Stage
  II (Kerley B) vs Stage III (alveolar) distinction already present in the
  source image labels.

### New lecture-grounded FEATURE_RULES splits

| Concept(s) | Lecture source | Page(s) | Grounded fact used |
|---|---|---|---|
| Idiopathic Pulmonary Fibrosis (clinical) vs Usual Interstitial Pneumonia/honeycombing (pathologic) vs pleural cobblestoning vs drug-induced (bleomycin/amiodarone) fibrosis | P24 RLS | 60-66 | IPF = clinical term (insidious, progressive, ~20% 5-yr survival, older smokers). UIP = the "usual" pathologic pattern in IPF: temporally/spatially heterogeneous fibrosis (old scars + recent injury + normal lung coexisting), subpleural/lower-lobe honeycombing, cobblestone pleural surface. Drug-induced fibrosis (bleomycin/amiodarone) is listed as a *known*-cause category, distinct from IPF's definitionally *unknown* cause. |
| Epithelioid vs sarcomatoid (spindle) mesothelioma | P26.1 RLS | 42 | 3 recognized histologic subtypes: epithelial, sarcomatoid/spindle, biphasic |

### Synonym merges added this pass (same finding, no distinguishing content found)

Lung mass/nodule/peripheral tumor/NSCLC/primary lung cancer variants; TB
reactivation-pattern labels (cavitary/secondary/upper-lobe TB); Golden
S sign / post-obstructive atelectasis variants; "normal lung" labels;
generic ILD labels; ARDS/DAD labels; diaphragmatic hernia laterality
variants; Cryptococcus stain-context labels; invasive fungal
sinusitis/Aspergillus labels; pectus carinatum variants; lobar pneumonia
(non-phase-specific) labels; normal airway/bronchus/bronchi; generic
sarcoidosis labels; silicosis + progressive massive fibrosis (no PMF-specific
lecture content found); bacterial pneumonia/CAP/lung consolidation; normal
acinus; Ankylosing Spondylitis spine-context label; caseating granuloma
labels; necrotizing pneumonia +/- effusion; sarcoid hilar/mediastinal
adenopathy labels; bronchopneumonia extent labels; asbestosis +/- plaque
descriptor; sarcoid asteroid body labels; acute asthma attack/asthma;
Blastomyces yeast-form/blastomycosis; radiation damage regardless of
underlying cancer treated; viral nuclear inclusions/viral pneumonia; central
tumor/endobronchial tumor; pneumonia congestion-phase labels; remaining
mesothelioma non-subtype-specific labels; nasal polyp labels regardless of
associated condition (chronic rhinosinusitis, EGPA/Churg-Strauss, CF) --
lecture (P33 RLS, Nasal Polyps slide) states the pathophysiology
(chronic inflammation -> polypoid degeneration) is the same regardless of
the associated systemic condition; Coccidioidomycosis wording variants;
Trachea size-descriptor variants; TB-associated vs generic lymphadenopathy;
Pulmonary (arterial) hypertension wording variants; Plexiform Lesion wording
variants.

### Result

Live duplicate-clue questions: 0. Latent (not-yet-collided but
un-synonym-linked) duplicate-clue clusters: 0. Concepts falling through to
the generic per-modality fallback: 0 of 365. `validate_bank.py` PASS,
17/17 tests pass, production build succeeds.
