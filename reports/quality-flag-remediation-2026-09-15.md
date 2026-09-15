# Pulmonary Picture Quality-Flag Remediation

Batch: `quality-review-2026-09-15`  
Reviewed: 2026-09-14T23:20:00-04:00

## Outcome

- Flags audited: 153
- Excluded from scoring: 56
- Isolated-panel crops: 13
- Other retained crops: 36
- Retained images with neutral-border/dead-space trim: 48
- Upstream lecture and Pulm Pictures libraries modified: no
- Upscaling, recoloring, mirroring, or generative reconstruction: none

Excluded items retain their source lineage in `source-manifest.json` and are not present in the scored bank. Retained items use a project-local derivative; the post-answer teaching original remains available separately.

## Item-level dispositions

| # | Flag | Action | Tested concept | Learner note | Resolution |
|---:|---|---|---|---|---|
| 1 | cropped-incomplete | exclude | Tracheoesophageal fistula on barium esophagram | Cropping, the picture isnt present | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 2 | irrelevant-content | exclude | Lung consolidation with air bronchograms | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 3 | cropped-incomplete | exclude | Pulmonary hyperinflation | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 4 | cropped-incomplete | trim | Acute respiratory distress syndrome | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 5 | cropped-incomplete | trim | Pressure-flow-volume cycle | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 6 | cropped-incomplete | trim | Viral pneumonia with nuclear inclusions | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 7 | cropped-incomplete | trim | Emphysema versus normal lung | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 8 | cropped-incomplete | trim | Peritonsillar abscess on physical examination | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 9 | cropped-incomplete | trim | Airless heavy dark-red neonatal lung | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 10 | blurry-low-quality | exclude | Fatal acute asthma | — | The source is too soft or degraded for a reliable identification question. |
| 11 | cropped-incomplete | crop | Croup with steeple sign and subglottic edema | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 12 | cropped-incomplete | exclude | Central pulmonary-artery enlargement with peripheral pruning | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 13 | cropped-incomplete | exclude | Necrotic invasive lung carcinoma | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 14 | cropped-incomplete | trim | Solitary pulmonary nodule | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 15 | cropped-incomplete | crop | Organizing pneumonia | — | A project-local crop preserves both complete histology panels while removing partial slide boxes and unrelated teaching prose. |
| 16 | cropped-incomplete | exclude | Fleischner sign of pulmonary embolism | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 17 | cropped-incomplete | trim | Tension pneumothorax | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 18 | cropped-incomplete | exclude | Acute respiratory distress syndrome (ARDS) | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 19 | cropped-incomplete | crop | Pulmonary carcinoid tumor | — | A project-local crop isolates the complete diagnostic histology field and removes the answer-revealing teaching box. |
| 20 | cropped-incomplete | exclude | Compressed low-volume lungs due to morbid obesity | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 21 | irrelevant-content | exclude | Barcode/stratosphere sign indicating absent lung sliding | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 22 | cropped-incomplete | trim | Central venous catheter | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 23 | answer-visible | exclude | Primary tuberculosis with a Ghon focus | — | The displayed teaching labels reveal or materially cue the keyed answer. |
| 24 | cropped-incomplete | exclude | Klebsiella pneumoniae | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 25 | cropped-incomplete | crop | Pectus excavatum | — | A project-local crop isolates one complete diagnostic panel and removes unrelated slide material. |
| 26 | cropped-incomplete | trim | Multiple pulmonary nodules or masses | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 27 | answer-visible | exclude | Pulmonary thromboembolism | — | The displayed teaching labels reveal or materially cue the keyed answer. |
| 28 | cropped-incomplete | trim | Situs inversus totalis with dextrocardia | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 29 | cropped-incomplete | exclude | Pulmonary sequestration | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 30 | cropped-incomplete | trim | Centriacinar emphysema | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 31 | irrelevant-content | exclude | Water-seal chest drainage system | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 32 | cropped-incomplete | exclude | Bullous emphysema | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 33 | cropped-incomplete | trim | Normal spirogram pressure-neutral points | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 34 | cropped-incomplete | exclude | Neonatal respiratory distress syndrome | Unclear which image is being tested only one should be | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 35 | cropped-incomplete | trim | Hyperinflated multicystic CPAM with contralateral mediastinal shift | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 36 | answer-visible | exclude | Metabolically active lung mass | — | The displayed teaching labels reveal or materially cue the keyed answer. |
| 37 | cropped-incomplete | trim | Right upper-lobe congenital lobar emphysema | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 38 | cropped-incomplete | exclude | Invasive fungal sinusitis | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 39 | cropped-incomplete | trim | Cardiogenic pulmonary edema | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 40 | cropped-incomplete | trim | Asbestos-related fibrous pleural plaques | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 41 | cropped-incomplete | trim | Pulmonary hypoplasia after congenital diaphragmatic hernia | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 42 | cropped-incomplete | trim | Pulmonary adenocarcinoma | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 43 | cropped-incomplete | crop | Apical lung mass | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 44 | cropped-incomplete | crop | Infected pulmonary sequestration | — | A project-local crop isolates the complete annotated chest radiograph and removes the clipped adjacent radiograph and blank slide space. |
| 45 | cropped-incomplete | trim | CPAM with sequestration hybrid lesion | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 46 | irrelevant-content | exclude | Right mainstem endotracheal-tube malposition | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 47 | cropped-incomplete | crop | High-probability V/Q scan for pulmonary embolism | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 48 | other | crop | Bilateral hilar lymphadenopathy | Should be cropped better | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 49 | cropped-incomplete | crop | Peritonsillar abscess | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 50 | blurry-low-quality | exclude | Asteroid body | — | The source is too soft or degraded for a reliable identification question. |
| 51 | cropped-incomplete | exclude | Venous thromboembolism (DVT with PE) | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 52 | cropped-incomplete | crop | Pulmonary infarction | — | A project-local crop isolates the complete gross-lung specimen and removes the clipped adjacent specimen. |
| 53 | other | crop | Dextrocardia | Should be cropped better | A project-local crop preserves the complete radiograph while removing the slide prompt, navigation arrows, and colored frame. |
| 54 | cropped-incomplete | trim | Asthma with hyperinflation | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 55 | cropped-incomplete | exclude | Mediastinal bronchogenic cyst causing airway compression | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 56 | cropped-incomplete | trim | Post-pneumonic lung abscess | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 57 | cropped-incomplete | trim | Scoliosis causing extrinsic restrictive lung disease | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 58 | cropped-incomplete | trim | Radiation fibrosis | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 59 | cropped-incomplete | trim | Pneumothorax | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 60 | irrelevant-content | exclude | Diagnostic spirometry | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 61 | cropped-incomplete | exclude | Pulmonary hamartoma | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 62 | cropped-incomplete | exclude | Empyema | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 63 | other | crop | Necrotizing pneumonia | Should be cropped better | A project-local crop isolates one complete diagnostic panel and removes unrelated slide material. |
| 64 | cropped-incomplete | trim | Asthmatic bronchoconstriction | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 65 | cropped-incomplete | trim | CPAM type 4 versus pleuropulmonary blastoma | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 66 | cropped-incomplete | crop | Small cell lung carcinoma | — | A project-local crop isolates the complete unlabeled H&E field and removes clipped teaching text and the labeled immunostain. |
| 67 | cropped-incomplete | trim | Bronchus | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 68 | cropped-incomplete | trim | Pulmonary infarction from pulmonary embolism | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 69 | cropped-incomplete | trim | Inspiratory pressure requirements | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 70 | irrelevant-content | exclude | Seashore sign indicating normal lung sliding | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 71 | cropped-incomplete | exclude | Lobar pneumonia with gray hepatization | Bad all around | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 72 | cropped-incomplete | crop | Loculated parapneumonic effusion on CT | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 73 | other | crop | Suppurative bronchopneumonia | Text should be cropped out | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 74 | cropped-incomplete | crop | Vanishing lung syndrome | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 75 | cropped-incomplete | trim | Viral interstitial pneumonia | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 76 | cropped-incomplete | trim | PaCO2 varies inversely with alveolar ventilation | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 77 | cropped-incomplete | trim | Pulmonary edema | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 78 | cropped-incomplete | exclude | Airway hyperresponsiveness to methacholine | — | The graph is clipped at the right source boundary, so its full scale and comparison cannot be restored without inventing content. |
| 79 | cropped-incomplete | trim | Obstructive apnea on polysomnography | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 80 | cropped-incomplete | trim | Caseous necrosis in tuberculosis | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 81 | other | crop | Red hepatization of lobar pneumonia | Photo should be cropped better to reduce dead space | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 82 | cropped-incomplete | trim | Angioinvasive pulmonary aspergillosis | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 83 | irrelevant-content | exclude | Right thoracostomy tube for pneumothorax | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 84 | irrelevant-content | exclude | External bracing for pectus carinatum | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 85 | blurry-low-quality | exclude | Emphysema with enlarged distal airspaces | — | The source is too soft or degraded for a reliable identification question. |
| 86 | cropped-incomplete | crop | Organizing pneumonia (BOOP/COP) | — | A project-local crop isolates the complete chest radiograph and removes the clipped adjacent teaching panel. |
| 87 | cropped-incomplete | exclude | Centriacinar emphysema | Only one photo should be there if only one is being tested | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 88 | irrelevant-content | exclude | Thoracentesis | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 89 | cropped-incomplete | trim | Congenital diaphragmatic hernia | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 90 | cropped-incomplete | crop | Pulmonary arterial hypertension arteriopathy | Photo should be cropped better to reduce dead space | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 91 | cropped-incomplete | trim | Malignant pleural mesothelioma | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 92 | cropped-incomplete | crop | Bronchopneumonia radiographic pattern | Only one picture should be present | A project-local crop isolates one complete diagnostic panel and removes unrelated slide material. |
| 93 | cropped-incomplete | trim | Diffuse ground-glass neonatal RDS | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 94 | irrelevant-content | exclude | Flexible bronchoscopy | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 95 | cropped-incomplete | exclude | Atypical or viral interstitial pneumonia | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 96 | answer-visible | crop | CT-guided lung biopsy | — | A project-local crop isolates one complete diagnostic panel and removes unrelated slide material. |
| 97 | cropped-incomplete | crop | Bronchopneumonia | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 98 | irrelevant-content | exclude | B-lines indicating an interstitial lung syndrome | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 99 | other | crop | Pulmonary arteriovenous malformation | Photo should be cropped better to reduce dead space | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 100 | cropped-incomplete | exclude | Duchenne muscular dystrophy with restrictive lung disease | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 101 | irrelevant-content | exclude | Endotracheal and nasogastric tubes, both appropriately positioned | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 102 | cropped-incomplete | exclude | Terminal bronchiole transitioning to respiratory bronchioles and alveolar ducts | — | The quiz-safe source contains a large opaque label mask over the tissue, so the complete histology field cannot be recovered locally. |
| 103 | cropped-incomplete | exclude | Scaphoid abdomen in congenital diaphragmatic hernia | Blurry as well | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 104 | cropped-incomplete | exclude | Post-obstructive atelectasis | One picture per question if only one picture is being tested | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 105 | other | crop | Septic pulmonary emboli | One picture per question if only one picture is being tested | A project-local crop isolates one complete diagnostic panel and removes unrelated slide material. |
| 106 | cropped-incomplete | crop | Dynamic tracheal collapse on bronchoscopy | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 107 | cropped-incomplete | crop | Silicosis | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 108 | cropped-incomplete | crop | Trachea, bronchi, and bronchioles | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 109 | cropped-incomplete | crop | Expiratory air trapping | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 110 | cropped-incomplete | exclude | Nasal polyps | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 111 | answer-visible | exclude | Westermark sign | — | The displayed teaching labels reveal or materially cue the keyed answer. |
| 112 | irrelevant-content | exclude | Peak-flow meter | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 113 | cropped-incomplete | exclude | Choanal atresia | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 114 | irrelevant-content | exclude | Bucket-handle movement of the ribs | — | The image tests equipment, technique, or a non-diagnostic teaching aside rather than pulmonary visual identification. |
| 115 | other | exclude | Legionella pneumophila | One picture per question if only one picture is being tested | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 116 | cropped-incomplete | crop | Bronchiectasis | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 117 | cropped-incomplete | exclude | Flow volume loop pattern | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 118 | other | crop | Alveoli of different sizes | Photo should be cropped better to reduce dead space | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 119 | cropped-incomplete | exclude | Ankylosing spondylitis | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 120 | cropped-incomplete | crop | CPAM type 3 | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 121 | cropped-incomplete | exclude | PA versus AP chest radiograph | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 122 | other | exclude | Staphylococcus aureus | One picture per question if only one picture is being tested | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 123 | other | crop | Longitudinal fixed obstruction in bronchopulmonary dysplasia | Cropping should be better | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 124 | other | crop | Patchy confluent bronchopneumonia | Photo should be cropped better to reduce dead space | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 125 | other | crop | Asbestos-related restrictive lung disease | Photo should be cropped better to reduce dead space | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 126 | cropped-incomplete | trim | Bronchial mucus cast in asthma | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 127 | cropped-incomplete | crop | Pulmonary embolism | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 128 | cropped-incomplete | exclude | Ventilator pressure waveforms | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 129 | cropped-incomplete | crop | Cough artifact during spirometry | — | A project-local crop isolates the complete cough-artifact flow-volume loop and removes the clipped adjacent graph. |
| 130 | cropped-incomplete | trim | Respiratory bronchiolitis | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 131 | cropped-incomplete | trim | Obstructing endobronchial mass | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 132 | cropped-incomplete | crop | Obliterative bronchiolitis | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 133 | cropped-incomplete | trim | COPD/emphysema hyperinflation | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 134 | cropped-incomplete | crop | Pulmonary hyperinflation from severe obstruction | — | A project-local crop isolates one complete diagnostic panel and removes unrelated slide material. |
| 135 | cropped-incomplete | crop | Chronic thromboembolic pulmonary hypertension (CTEPH) | — | A project-local crop isolates the complete upper four-view perfusion set and removes the clipped partial set below it. |
| 136 | cropped-incomplete | trim | Small-airway obstructive flow-volume loop | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 137 | cropped-incomplete | crop | Acute epiglottitis | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 138 | cropped-incomplete | exclude | Emphysema histopathology | Answer choices semantically similar | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 139 | cropped-incomplete | exclude | Breathing patterns after brainstem transection | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 140 | cropped-incomplete | crop | Interstitial lung pattern | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 141 | cropped-incomplete | exclude | Nuss repair of pectus excavatum | — | The image is incomplete, non-diagnostic, redundant with a stronger retained item, or cannot be repaired without inventing missing content. |
| 142 | cropped-incomplete | crop | Recurrent respiratory papillomatosis | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 143 | cropped-incomplete | trim | Lobar consolidation | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 144 | cropped-incomplete | crop | Acute pneumonia | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 145 | cropped-incomplete | crop | Acquired subglottic stenosis | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 146 | cropped-incomplete | crop | Smoking-related emphysema | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 147 | cropped-incomplete | crop | Cystic fibrosis with bronchiectasis | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 148 | cropped-incomplete | crop | Hypersensitivity pneumonitis | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 149 | cropped-incomplete | trim | Carbon dioxide is much more soluble than oxygen | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 150 | cropped-incomplete | trim | Asbestos bodies | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 151 | cropped-incomplete | trim | Right upper lobe pneumonia | — | The diagnostic content is complete; neutral border and dead space are trimmed without changing or upscaling the source pixels. |
| 152 | cropped-incomplete | crop | Pulmonary hyperinflation in persistent asthma | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
| 153 | cropped-incomplete | crop | Pulmonary sequestration supplied by the aorta | — | A project-local crop preserves the complete tested view or comparison while removing dead space and unrelated slide material. |
