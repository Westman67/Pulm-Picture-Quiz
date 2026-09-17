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

## Full-pass FEATURE_RULES citation audit (all 215 rules)

Following the comprehensive completion pass above, a systematic audit was run against the full RLS (Reduced Lecture Slides) and Tran (transcript) corpus for every course lecture that has an RLS or Tran file (98 PDF files under `Desktop/Pulm/Lectures/`, extracted to text via `pdftotext -layout`). For each of the 215 `FEATURE_RULES` entries, the pattern's key terms were searched across every page of every file, and the best-matching page for each entry was read directly (not just keyword-matched) to confirm the page actually covers that finding or entity, and a handful of coincidental generic-word matches (e.g. "organized" matching an unrelated sentence) were caught this way and corrected to the real source page.

**What "confirmed" means here, precisely**: the cited lecture page discusses the named disease/finding/entity that the rule's clue text describes. For entries where the page states the exact descriptive fact used in the clue text (most of the high-confidence matches), the citation is a direct source for that fact. For entries where the page names and teaches the entity but the clue text's specific morphologic/radiographic phrasing is the generator's own synthesis of that same finding rather than a lecture quotation, the citation is a topic-location source, not a verbatim source -- both are listed together below since separating them exhaustively was outside this pass's scope, but none of the citations below are coincidental keyword matches; each was read and confirmed to be about the right disease/finding.

**Result: 172 of 215 rules trace to a specific, confirmed lecture page; 37 do not appear anywhere in the 98-file RLS/Tran corpus searched and are listed as open gaps below.**

### Confirmed against a specific lecture page

| FEATURE_RULES pattern | Lecture source | Page |
|---|---|---|
| `(?<!non-)(?<!non )small cell` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 32 |
| `^atelectasis$` | P27.1 Radiology Pulm Infections & Cancer of Lung Tran | 10 |
| `^bronchiole$` | P2 Respiration Basics RLS | 14 |
| `^bronchus$\|^bronchi$` | P1 Review Histology of the Lungs Tran | 4 |
| `^normal$` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 8 |
| `^pneumonia$\|pneumonia hist` | P26.2 Diseases of the Respiratory Tract Supplementary Review RLS | 4 |
| `acid.fast bacilli` | P13 Pulmonary Problem Solving Exercise Part 1 - (Patient Care) Tran | 9 |
| `acute infectious bronchiolitis` | P20 Radiology of Obstructive Disease Tran | 10 |
| `acute pneumonia` | P30 Microbiology of Pneumonia - Fungal Infections Tran | 4 |
| `acute respiratory distress\|acute diffuse alveolar damage` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 73 |
| `adenocarcinoma` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 22 |
| `air bronchogram` | P27.1 Enriched RLS | 9 |
| `alveolar hemorrhage` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 69 |
| `ankylosing spondylitis` | P25 Radiology Restrictive Diseases Tran | 4 |
| `anthracotic pigment\|coal worker` | P15 Approach to a Patient with Respiratory Disease & Preventative Care (Pathophysiology) RLS | 13 |
| `ards.*hyaline membrane\|hyaline membrane.*ards\|ards intraalveolar hyaline` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 78 |
| `ards\|diffuse alveolar damage` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 78 |
| `asbestos body` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) Tran | 15 |
| `asbestosis` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) Tran | 15 |
| `aspergilloma\|fungal ball` | P27.1 Enriched RLS | 18 |
| `aspergillus.*conidiophore` | P30 Microbiology of Pneumonia - Fungal Infections RLS | 22 |
| `aspergillus.*hyphae` | P30 Microbiology of Pneumonia - Fungal Infections RLS | 22 |
| `aspiration pneumonia` | P31 Review of Pneumonia (Pathology:Pharmacology) RLS | 8 |
| `asteroid body` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 44 |
| `asthma` | P22-23 Drugs Used for Treatment of Asthma and COPD RLS | 7 |
| `atypical\|mycoplasma` | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | 12 |
| `av malformation` | P10-11 Interactive Workshop Physiologist & Physician Mini-Case Study Review (Physiology) Tran | 11 |
| `bacterial pneumonia\|community acquired pneumonia\|lung consolidation pneumonia` | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | 12 |
| `blastomyc` | P30 Microbiology of Pneumonia - Fungal Infections RLS | 17 |
| `bleomycin\|amiodarone` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 30 |
| `bleomycin\|amiodarone` | P25 Radiology Restrictive Diseases Tran | 6 |
| `blue bloater` | P34 Respiratory Medicine Clinical Case Studies - Obstructive Diseases (Pathophysiology) RLS | 36 |
| `bronchiectasis` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 73 |
| `bronchiectasis.*chronic bronchitis` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 32 |
| `bronchiectasis.*cystic fibrosis\|cystic fibrosis.*bronchiectasis` | P20 Radiology of Obstructive Disease RLS | 22 |
| `bronchiectasis.*fibrosis and inflammation` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 68 |
| `bronchiectasis.*situs invert\|situs invert.*bronchiectasis\|kartagener` | P14 Intro To Pulmonary Pathology RLS | 3 |
| `bronchiectasis.*squamous metaplasia` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 12 |
| `bronchogenic cyst` | P36 Pulmonary Developmental Anomalies RLS | 18 |
| `bronchopneumonia` | P26.2 Diseases of the Respiratory Tract Supplementary Review RLS | 9 |
| `bronchopulmonary dysplasia` | P36 Pulmonary Developmental Anomalies Tran | 1 |
| `carcinoid` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 37 |
| `cardiogenic\|congestive heart failure` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 23 |
| `cavitary tb\|secondary tb\|old right upper lobe\|\btb\b` | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | 31 |
| `central tumor\|endobronchial tumor` | P18 Radiology - Basic Interpretation of Chest X-Ray RLS | 27 |
| `centri.?acinar emphysema` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 49 |
| `chiari` | P33 ENT:Airway Diseases Tran | 8 |
| `chronic bronchitis` | P34 Respiratory Medicine Clinical Case Studies - Obstructive Diseases (Pathophysiology) RLS | 28 |
| `coccidio` | P30 Microbiology of Pneumonia - Fungal Infections RLS | 9 |
| `complicated sinusitis` | P33 ENT:Airway Diseases RLS | 14 |
| `congenital lobar emphysema` | P36 Pulmonary Developmental Anomalies RLS | 7 |
| `congestion phase of pneumonia\|acute inflammation in lobar pneumonia` | P31 Review of Pneumonia (Pathology:Pharmacology) RLS | 49 |
| `consolidative tb` | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | 31 |
| `contraction atelectasis` | P27.1 Radiology Pulm Infections & Cancer of Lung Tran | 5 |
| `contraction atelectasis.*tb\|tb.*contraction atelectasis` | P27.1 Radiology Pulm Infections & Cancer of Lung Tran | 5 |
| `cpam` | P36 Pulmonary Developmental Anomalies Tran | 10 |
| `cpam.*emphysema\|emphysema.*cpam` | P36 Pulmonary Developmental Anomalies Tran | 2 |
| `cpam.*pulmonary sequestration\|pulmonary sequestration.*cpam` | P36 Pulmonary Developmental Anomalies RLS | 33 |
| `croup\|steeple` | P33 ENT:Airway Diseases RLS | 35 |
| `cryptococcus\|encapsulated cryptococcus` | P30 Microbiology of Pneumonia - Fungal Infections RLS | 28 |
| `deep venous thrombosis` | P13 Pulmonary Problem Solving Exercise Part 1 - (Patient Care) Tran | 16 |
| `dextrocardia\|situs invert` | P18 Radiology - Basic Interpretation of Chest X-Ray Tran | 10 |
| `diaphragmatic eventration` | P36 Pulmonary Developmental Anomalies RLS | 66 |
| `diaphragmatic hernia\|scaphoid abdomen` | P36 Pulmonary Developmental Anomalies RLS | 62 |
| `duchenne` | P13 Pulmonary Problem Solving Exercise Part 1 - (Patient Care) Tran | 9 |
| `emphysema with primary lung cancer\|emphysema.*lung cancer` | P13 Pulmonary Problem Solving Exercise Part 1 - (Patient Care) Tran | 6 |
| `emphysema\|vanishing lung\|\bcopd\b` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 Tran | 12 |
| `empyema` | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | 25 |
| `epiglott` | P10-11 Interactive Workshop Physiologist & Physician Mini-Case Study Review (Physiology) Tran | 19 |
| `erythema nodosum` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) Tran | 19 |
| `extralobar.*sequestration` | P36 Pulmonary Developmental Anomalies RLS | 40 |
| `ferruginous bod\|asbestos bodies` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) Tran | 15 |
| `fleischner` | P25 Radiology Restrictive Diseases Tran | 12 |
| `foreign bod` | P20 Radiology of Obstructive Disease Tran | 4 |
| `ghon complex` | P26.2 Diseases of the Respiratory Tract Supplementary Review RLS | 16 |
| `ghon focus` | P26.2 Diseases of the Respiratory Tract Supplementary Review RLS | 16 |
| `golden s\|post-obstructive\|resorption atelectasis` | P27.1 Enriched RLS | 25 |
| `goodpasture` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 69 |
| `gr[ae]y hepatization` | P31 Review of Pneumonia (Pathology:Pharmacology) Tran | 2 |
| `granuloma.*tuberc\|necrotizing granuloma` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) Tran | 17 |
| `granulomatosis with polyangiitis` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 22 |
| `hamartoma` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 4 |
| `hampton` | P25 Radiology Restrictive Diseases Tran | 12 |
| `hemosiderin.laden macrophage` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 69 |
| `histoplas` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) Tran | 17 |
| `histoplasma.*mold` | P30 Microbiology of Pneumonia - Fungal Infections RLS | 22 |
| `honeycomb` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 62 |
| `honeycomb.*idiopathic pulmonary fibrosis\|honeycomb.*\bipf\b\|honeycomb.*usual interstitial\|\buip\b\|usual interstitial pneumonia` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 61 |
| `hyaline membrane\|neonatal respiratory` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 23 |
| `hypersensitivity pneumonitis` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 28 |
| `interstitial fibrosis\|interstitial lung disease` | P3 - Airway and Vascular Flow - Enriched RLS | 94 |
| `interstitial pneumonia` | P25 Radiology Restrictive Diseases RLS | 27 |
| `intralobar.*sequestration` | P36 Pulmonary Developmental Anomalies RLS | 40 |
| `invasive asperg\|invasive fungal` | P26.2 Diseases of the Respiratory Tract Supplementary Review RLS | 23 |
| `jeune syndrome` | P36 Pulmonary Developmental Anomalies RLS | 16 |
| `kerley\|interstitial.*cardiogenic\|interstitial.*congestive heart failure` | P25 Radiology Restrictive Diseases Tran | 10 |
| `klebsiella pneumonia` | P28 Microbiology of Pneumonia - Bacterial Infection RLS | 4 |
| `kyphosis` | P25 Radiology Restrictive Diseases RLS | 11 |
| `large cell.*carcinoma\|pulmonary large cell` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 2 |
| `large cpam.*hyperinflation\|cpam.*hyperinflation` | P36 Pulmonary Developmental Anomalies RLS | 29 |
| `laryngomalacia` | P37 Advanced Spirometry Review - Interactive Workshop (Physiology) Tran | 10 |
| `lines of zahn` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 49 |
| `lll silhouette\|rll silhouette\|lower lobe silhouette` | P27.1 Enriched RLS | 2 |
| `lobar pneumonia\|hepatization\|lobar consolidation` | P26.2 Diseases of the Respiratory Tract Supplementary Review RLS | 9 |
| `lymphadenopathy` | P18 Radiology - Basic Interpretation of Chest X-Ray Tran | 4 |
| `lymphan?gitic metasta` | P27.1 Enriched RLS | 21 |
| `lymphocytic infiltrate.*airway` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 16 |
| `lymphoma` | P33 ENT:Airway Diseases RLS | 42 |
| `mesothelioma` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) Tran | 13 |
| `metasta\|lymphangitic` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 Tran | 4 |
| `miliary` | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | 35 |
| `nasal polyp\|polyposis` | P33 ENT:Airway Diseases RLS | 10 |
| `necrotizing pneumonia` | P27.1 Enriched RLS | 18 |
| `normal (acinus\|alveol)` | P26.2 Diseases of the Respiratory Tract Supplementary Review RLS | 5 |
| `normal (bronchus\|airway\|bronchi\|bronchiole)` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 Tran | 11 |
| `normal (ct\|infant\|lung)` | P35 Acute Respiratory Failure (Pathology) Tran | 8 |
| `normal carina` | P37 Advanced Spirometry Review - Interactive Workshop (Physiology) Tran | 12 |
| `normal mesothelium` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 41 |
| `obliterative bronchiolitis` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 81 |
| `organized (?:venous )?(?:thromboembol\|embol)` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 19 |
| `organized (thrombo\|embol)\|vte` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 4 |
| `organizing pneumonia\|\bboop\b\|\bcop\b` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 16 |
| `papillomatosis` | P33 ENT:Airway Diseases RLS | 32 |
| `paracoccidio` | P30 Microbiology of Pneumonia - Fungal Infections RLS | 19 |
| `parapneumonic effusion` | P31 Review of Pneumonia (Pathology:Pharmacology) RLS | 79 |
| `pectus carinatum\|pectus arcuatum` | P36 Pulmonary Developmental Anomalies RLS | 59 |
| `pectus excavatum\|haller` | P12 Approach to Pulmonary Abnormalities Lecture (Patient Care) Tran | 8 |
| `peripheral tumor\|lung mass\|lung nodule\|primary lung cancer\|non-small cell` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 30 |
| `peritonsillar` | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | 33 |
| `pink puffer` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 61 |
| `pleural effusion` | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | 12 |
| `pleural plaque` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 33 |
| `plexiform` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 22 |
| `pneumothorax` | P18 Radiology - Basic Interpretation of Chest X-Ray Tran | 7 |
| `pores of kohn` | P27.1 Enriched RLS | 11 |
| `pulmonary (arterial )?hypertension` | P36 Pulmonary Developmental Anomalies RLS | 63 |
| `pulmonary abscess` | P31 Review of Pneumonia (Pathology:Pharmacology) Tran | 10 |
| `pulmonary agenesis` | P36 Pulmonary Developmental Anomalies RLS | 7 |
| `pulmonary edema` | P9 Pulmonary Physiology Lecture Review (Physiology) RLS | 36 |
| `pulmonary effusion.*(?:chf\|heart failure)\|bilateral pulmonary effusion` | P13 Pulmonary Problem Solving Exercise Part 1 - (Patient Care) Tran | 4 |
| `pulmonary embol\|pulmonary thromboembol` | P25 Radiology Restrictive Diseases Tran | 12 |
| `pulmonary fibrosis\|\bipf\b` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 60 |
| `pulmonary infarct` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 53 |
| `pulmonary sequestration` | P36 Pulmonary Developmental Anomalies RLS | 39 |
| `red hepatization` | P31 Review of Pneumonia (Pathology:Pharmacology) RLS | 18 |
| `respiratory bronchiolitis` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 51 |
| `rheumatoid` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 23 |
| `round atelectasis` | P27.1 Enriched RLS | 12 |
| `round pneumonia` | P27.1 Radiology Pulm Infections & Cancer of Lung Tran | 4 |
| `saddle` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 49 |
| `sarcoid.*lymphocytic bronchoalveolar\|bronchoalveolar lavage.*sarcoid` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 47 |
| `sarcoid\|asteroid body` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 44 |
| `sarcomatoid.*mesothelioma` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 42 |
| `schaumann` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) RLS | 45 |
| `scoliosis` | P25 Radiology Restrictive Diseases RLS | 10 |
| `septic embol` | P27.1 Radiology Pulm Infections & Cancer of Lung RLS | 35 |
| `silhouette sign` | P27.1 Enriched RLS | 6 |
| `silico\|silicosis` | P19 Diseases of the Respiratory Tract - Part 1 - Obstructive Diseases : Airway Diseases (Pathology) - Part 1 RLS | 22 |
| `smaller,? peripheral pulmonary thromboembol` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) RLS | 50 |
| `squamous cell` | P27.1 Radiology Pulm Infections & Cancer of Lung Tran | 10 |
| `squamous metaplasia` | P26.1 Diseases of the Respiratory Tract-Part 3 - Vascular, Cancer, Other Disease (Pathology) Tran | 12 |
| `streptococcus pneumoniae\|pneumococci` | P28 Microbiology of Pneumonia - Bacterial Infection RLS | 5 |
| `syringomyelia` | P33 ENT:Airway Diseases RLS | 26 |
| `tension pneumothorax` | P18 Radiology - Basic Interpretation of Chest X-Ray Tran | 4 |
| `trachea` | P2 Respiration Basics - Part 1 - Structure And Volumes (Physiology) - Part 2 Tran | 8 |
| `tracheomalacia` | P37 Advanced Spirometry Review - Interactive Workshop (Physiology) RLS | 34 |
| `trichrome.*sarcoid` | P24 Diseases of the Respiratory Tract - Part 2 - Restrictive Disease (Pathology) Tran | 19 |
| `tumor.?thick wall` | P27.1 Enriched RLS | 18 |
| `type 4 cpam\|type 4.*pleuropulmonary blastoma\|pleuropulmonary blastoma` | P36 Pulmonary Developmental Anomalies RLS | 27 |
| `viral pneumonia\|viral nuclear` | P26.2 Diseases of the Respiratory Tract Supplementary Review RLS | 13 |
| `vocal fold` | P37 Advanced Spirometry Review - Interactive Workshop (Physiology) Tran | 10 |
| `wedge shaped pulmonary embol\|wedge.shaped.*pulmonary embol` | P26.2 Diseases of the Respiratory Tract Supplementary Review RLS | 24 |
| `\bacinus\b` | P17 Enriched | 16 |
| `bilateral pneumothoraces` | P27.2 CXR Final Review | 12 |
| `broken ribs` | P27.2 Enriched | 8 |
| `dvt` | P17 Introduction to Respiratory Pathophysiology (Pathology) Lecture Slides | 5 |
| `kartagener` | P27.2 Enriched | 15 |
| `large right.sided pulmonary effusion` | P27.2 Enriched | 22 |
| `nonspecific interstitial pneumonia\|\bnsip\b` | P24 Enriched | 2 |
| `patchy ground.glass opacity` | P25 Radiology Restrictive Diseases Lecture Slides | 29 |
| `pleural mesothelioma` | P27.2 Enriched | 19 |
| `pulmonary contusion` | P0 USMLE Content | 2 |
| `vocal cord nodule` | P33 Enriched | 25 |

### Not found in the searched RLS/Tran corpus (open gaps)

These rule patterns were searched across the original 98-file RLS/Tran corpus and, in an extended pass, a further 89 non-RLS/Tran lecture files (full Lecture Slides decks, Enriched decks, case-review PDFs, notes, and the USMLE content outline -- effectively the full `Desktop/Pulm/Lectures/` folder). 11 of the original 37 gaps were located in that extended search and moved into the confirmed table above (several under a related lecture term, e.g. "vocal cord nodule" -> the lecture's "vocal fold nodule"). The following 26 still do not appear anywhere in the full lecture folder searched. Their text is the generator's own morphologic/radiographic phrasing (consistent with general pathology/radiology teaching, e.g. Robbins-level descriptions used elsewhere in this course) rather than content located in any lecture file. Per the citation requirement, these remain flagged as **unverified against lecture material**.

| FEATURE_RULES pattern | Text |
|---|---|
| `amphibole asbestos` | straight, rigid needle-like mineral fibers rather than curled serpentine fibers |
| `bronchioloalveolar carcinoma` | neoplastic cells growing along pre-existing alveolar septa in a lepidic pattern |
| `calcified pulmonary nodule` | a sharply marginated pulmonary nodule containing dense central or laminated calcification |
| `caseating granuloma` | central granular caseous necrosis rimmed by epithelioid histiocytes and Langhans-type giant cells |
| `cavitary pulmonary tuberculosis` | upper-lung cavitary destructive opacity with surrounding fibrotic or infiltrative change |
| `cavitating pneumonia` | air-space consolidation containing a thick-walled cavity or abscess |
| `chrysotile asbestos` | curled, flexible serpentine mineral fibers rather than straight rigid amphibole fibers |
| `compression atelectasis` | passive lung collapse immediately adjacent to pleural air or fluid |
| `diaphragmatic rupture` | intrathoracic abdominal viscera with mediastinal displacement through a disrupted hemidiaphragm |
| `healed fibrocalcific granuloma` | a densely fibrotic old granuloma containing central dystrophic calcification |
| `interstitial lung filling` | reticular or linear opacity involving the supporting interstitium |
| `lymph node sarcoid` | non-necrotizing granulomatous replacement of nodal architecture on lymph node biopsy |
| `multinucleated giant cells` | large fused histiocytes containing numerous nuclei within an organized granulomatous reaction |
| `multiple small pulmonary nodules` | numerous discrete small rounded opacities distributed through both lungs |
| `near normal lung filling` | preserved lung lucency without a dominant alveolar, interstitial, or nodular filling pattern |
| `nodular lung filling` | multiple discrete rounded pulmonary opacities rather than confluent air-space disease |
| `noncaseating granuloma` | a compact collection of epithelioid histiocytes and multinucleated giant cells without central caseous necrosis |
| `normal pulmonary alveoli` | delicate open alveolar spaces separated by very thin septa without inflammatory filling, fibrosis, or architectural destruction |
| `pleural cobbleston` | a cobblestone-appearing pleural surface, the gross correlate of underlying honeycomb parenchymal remodeling |
| `pulmonary alveolus with alveolar macrophages` | large macrophages lying freely within otherwise thin-walled alveolar spaces |
| `radiation damage` | sharply geographic consolidation or fibrosis conforming to a prior radiation field |
| `recent thromboembol` | a fresh occlusive thrombus with preserved red-cell and fibrin laminations but no mature recanalization |
| `right lung agenesis\|lung agenesis` | absence of the right lung with ipsilateral volume loss and compensatory hyperinflation of the left lung |
| `rml silhouette\|lingula silhouette` | silhouetting (loss of the sharp border) of the heart, since RML/lingula disease abuts and effaces the cardiac silhouette |
| `spleen sarcoid` | non-necrotizing granulomas within splenic parenchyma, reflecting extrapulmonary sarcoid organ involvement beyond the lung |
| `alveolar lung filling` | fluffy confluent air-space opacities with indistinct margins and possible air bronchograms |
