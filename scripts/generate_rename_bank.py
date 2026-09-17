#!/usr/bin/env python3
"""Build a local pulmonary picture-identification bank from Desktop/Rename and Add.

The source folder is treated as immutable. Every browser asset is re-encoded into the
project with an opaque filename and stripped metadata. Filename-derived keys are accepted
only because this is a user-curated, descriptively renamed collection and every image was
also reviewed in a full-set contact-sheet pass.
"""

from __future__ import annotations

import hashlib
import json
import re
import shutil
from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageOps


PROJECT = Path(__file__).resolve().parents[1]
COLLECTIONS = (
    {
        "key": "rename",
        "label": "Lecture material",
        "path": Path.home() / "Desktop" / "Rename",
        "document": "Desktop/Rename user-curated pulmonary image collection",
        "rule": "All images supplied in Desktop/Rename are third-party study images.",
    },
    {
        "key": "third_party",
        "label": "3rd Party",
        "path": Path.home() / "Desktop" / "Add",
        "document": "Desktop/Add third-party pulmonary image collection",
        "rule": "All images supplied in Desktop/Add are third-party study images in the 3rd Party collection.",
    },
)
ASSET_DIR = PROJECT / "public" / "assets" / "images"
QUIZ_WEBP_QUALITY = 88  # visually-lossless for on-screen identification; teaching original stays lossless PNG
DATA_DIR = PROJECT / "data"
REPORT_DIR = PROJECT / "reports"
NOW = datetime.now(ZoneInfo("America/New_York")).isoformat()

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}

# These files remain visible in reviewer mode but are not used in scored sessions. Their
# visible evidence does not establish one sufficiently precise pulmonary answer.
REVIEW_ONLY_RENAME: dict[str, str] = {
    "Appendicitis CXR.png": "The filename and visible target do not establish a defensible pulmonary identification task.",
    "CF CT 2.png": "The displayed upper-abdominal CT does not provide sufficient pulmonary evidence for cystic fibrosis.",
    "CF CT 3.png": "The displayed upper-abdominal CT does not provide sufficient pulmonary evidence for cystic fibrosis.",
    "Pulmonary Infarct Gross.png": "Embedded labels state the tested diagnosis directly over medically meaningful tissue.",
    "Pulmonary Metalplasia .png": "The source label is ambiguous and the intended metaplastic process is not specified reliably.",
}

CASE_CONTEXT: dict[str, str] = {
    "Acute Asthma Attack.png": "A 19-year-old presents to the emergency department with acute dyspnea, audible wheeze, and a prolonged expiratory phase during a known asthma exacerbation.",
    "Asthma CXR.png": "A patient with a long-standing history of episodic wheeze, nocturnal cough, and spirometry-confirmed reversible airflow obstruction undergoes this chest radiograph as part of a routine outpatient work-up.",
    "Echocardiogram in Pulmonary Artery Hypertension (3:3).jpg": "A patient with progressive exertional dyspnea and a loud pulmonic component of the second heart sound undergoes transthoracic echocardiography; the report estimates the right ventricular systolic pressure at 58 mmHg with septal flattening in systole.",
    "P529 CF Lung Disease.png": "A young adult with a history of recurrent childhood pneumonias, chronic productive cough, and a positive sweat chloride test undergoes this chest radiograph.",
    "Blue Bloater.png": "A 58-year-old with a 40-pack-year smoking history presents with a chronic productive cough, peripheral edema, and mild resting cyanosis; pulmonary function testing shows a chronic bronchitis-predominant obstructive pattern.",
    "Bleomycin or Amiodarone Pulmonary Fibrosis CXR .png": "A patient undergoing treatment with bleomycin for testicular cancer develops progressive dyspnea and bibasilar crackles; pulmonary function testing shows a new restrictive pattern with a reduced diffusion capacity.",
    "Bronchopulmonary dysplasia CXR.png": "A former 26-week premature infant who required prolonged mechanical ventilation and supplemental oxygen for respiratory distress syndrome now, at 36 weeks postmenstrual age, continues to require oxygen support.",
    "Bronchopulmonary dysplasia Histo.png": "A former 26-week premature infant who required prolonged mechanical ventilation and supplemental oxygen for respiratory distress syndrome now, at 36 weeks postmenstrual age, continues to require oxygen support.",
    "Bronchopulmonary Dysplasia.jpg": "A former 26-week premature infant who required prolonged mechanical ventilation and supplemental oxygen for respiratory distress syndrome now, at 36 weeks postmenstrual age, continues to require oxygen support.",
    "Duchenne's Muscular Dystrophy CXR CT.png": "A 10-year-old boy with a known dystrophin gene mutation, progressive proximal muscle weakness, and calf pseudohypertrophy is evaluated for worsening restrictive respiratory symptoms.",
    "Goodpasture Histo.png": "A patient presents with hemoptysis, progressive dyspnea, and acute kidney injury; serum testing is positive for anti-glomerular basement membrane antibodies.",
    "Nasal Polyps from EGPA (Churg-Strauss).png": "A patient with adult-onset asthma and marked peripheral eosinophilia develops nasal polyps, sinusitis, and new mononeuritis multiplex; ANCA testing is positive.",
}

# Stem override for the CASE_CONTEXT questions above: the default stem_for() phrasing asks for
# an identification from pixels alone, which is exactly what these sources cannot support without
# the paired vignette.
CASE_STEM: dict[str, str] = {
    "Acute Asthma Attack.png": "Given this clinical presentation, which diagnosis is most consistent with the history and this chest radiograph?",
    "Asthma CXR.png": "Given this clinical presentation, which diagnosis is most consistent with the history and this chest radiograph?",
    "Echocardiogram in Pulmonary Artery Hypertension (3:3).jpg": "Given this echocardiographic report and the labeled apical four-chamber view, which diagnosis is best supported?",
    "P529 CF Lung Disease.png": "Given this history, which diagnosis is best supported by the pattern on this chest radiograph?",
    "Blue Bloater.png": "Given this clinical presentation, which COPD phenotype does this patient's photograph best match?",
    "Bleomycin or Amiodarone Pulmonary Fibrosis CXR .png": "Given this treatment history, which diagnosis is best supported by the pattern on this chest radiograph?",
    "Bronchopulmonary dysplasia CXR.png": "Given this history, which diagnosis is best supported by the pattern on this chest radiograph?",
    "Bronchopulmonary dysplasia Histo.png": "Given this history, which diagnosis is best supported by the pattern on this lung histology?",
    "Bronchopulmonary Dysplasia.jpg": "Given this history, which diagnosis is best supported by the pattern on this chest radiograph?",
    "Duchenne's Muscular Dystrophy CXR CT.png": "Given this history, which diagnosis best unifies the visible findings across all displayed panels?",
    "Goodpasture Histo.png": "Given this history, which diagnosis, tissue, or pathologic process best matches the dominant microscopic morphology in the complete displayed image?",
    "Nasal Polyps from EGPA (Churg-Strauss).png": "Given this clinical presentation, which diagnosis is best supported by the appearance of the nasal cavity?",
}

# Clue override for the same sources: describes only what is defensibly visible plus the case
# detail that supplies the missing specificity, instead of the generic pathophysiology fallback.
CASE_CLUE: dict[str, str] = {
    "Acute Asthma Attack.png": "a chest radiograph that is normal or near-normal, without consolidation, effusion, or a focal mass \u2014 the expected pattern during an acute asthma exacerbation, since the diagnosis is made clinically rather than radiographically",
    "Asthma CXR.png": "a chest radiograph that remains normal or near-normal despite the patient's documented reversible airflow obstruction, consistent with asthma, in which imaging is typically unremarkable outside of a severe exacerbation",
    "Echocardiogram in Pulmonary Artery Hypertension (3:3).jpg": "an echocardiographic four-chamber view with the right ventricle (RV) and left ventricle (LV) labeled, interpreted alongside a report noting an estimated RVSP of 58 mmHg and systolic septal flattening \u2014 findings that indicate right ventricular pressure overload from pulmonary arterial hypertension",
    "P529 CF Lung Disease.png": "increased bronchovascular markings with peribronchial wall thickening and bronchiectatic change, in a patient with a positive sweat chloride test",
    "Blue Bloater.png": "a stocky, overweight body habitus consistent with the chronic-bronchitis-predominant ('blue bloater') COPD phenotype — the vignette supplies the cyanosis and cor pulmonale that the photograph alone can't definitively show",
    "Bleomycin or Amiodarone Pulmonary Fibrosis CXR .png": "bilateral basal and subpleural reticulation with traction change or honeycombing, developing in the setting of a fibrosis-inducing chemotherapeutic or antiarrhythmic agent rather than as isolated idiopathic fibrosis",
    "Bronchopulmonary dysplasia CXR.png": "coarse heterogeneous neonatal lung opacity, developing after prolonged mechanical ventilation and oxygen exposure in a premature infant rather than as an acute presentation",
    "Bronchopulmonary dysplasia Histo.png": "simplified, enlarged air spaces on histology, developing after prolonged mechanical ventilation and oxygen exposure in a premature infant rather than as an acute presentation",
    "Bronchopulmonary Dysplasia.jpg": "coarse heterogeneous neonatal lung opacity, developing after prolonged mechanical ventilation and oxygen exposure in a premature infant rather than as an acute presentation",
    "Duchenne's Muscular Dystrophy CXR CT.png": "reduced chest expansion and dependent atelectatic change from chronic respiratory muscle weakness, in a patient whose vignette supplies the diagnosis (dystrophin mutation, calf pseudohypertrophy) that a chest image alone cannot establish",
    "Goodpasture Histo.png": "diffuse alveolar blood and hemosiderin-laden macrophage injury rather than purulent exudate, in a patient whose vignette supplies the anti-GBM antibody and renal findings that distinguish this from other causes of diffuse alveolar hemorrhage",
    "Nasal Polyps from EGPA (Churg-Strauss).png": "smooth polypoid soft tissue filling the nasal cavity, in a patient whose vignette (asthma, eosinophilia, vasculitic neuropathy) supplies the systemic features of EGPA that nasal polyps alone cannot show, distinguishing it from routine chronic rhinosinusitis with nasal polyps",
}

REVIEW_ONLY_ADD: dict[str, str] = {
    "A Pneumothorax CT Air in Pleural Space with Partial Lung Collapse.png": "Diagnostic labels define the tested pneumothorax directly over medically meaningful pixels and cannot be removed safely.",
    "Echocardiogram in Pulmonary Artery Hypertension (1:3).jpg": "A single unlabeled echocardiographic still does not uniquely establish pulmonary arterial hypertension without diagnostic measurements or Doppler evidence.",
    "Echocardiogram in Pulmonary Artery Hypertension (2:3).jpg": "A single unlabeled echocardiographic still does not uniquely establish pulmonary arterial hypertension without diagnostic measurements or Doppler evidence.",
}

DUPLICATE_OF: dict[str, str] = {
    "E_Asthma_Mucus_Plug_Histology.png": "Asthma Histo 3.png",
    "P010 Primary Pulmonary Hypertension Plexiform Lesion.png": "Plexiform Lesion Histo copy.png",
    "P013 Small Cell Carcinoma Histology.png": "Small Cell Histo.png",
    "P013 Carcinoid Tumor Polypoid Bronchial Gross.png": "Carcinoid Gross.png",
    "D Squamous Cell Lung Carcinoma Keratin Pearls Histology.png": "Squamous Cell Carcinoma Histo 2.png",
    "B Lung Adenocarcinoma Glandular Histology.png": "Adenocarcinoma Histo.png",
}

# Safe border crops remove answer-revealing titles or captions that sit outside diagnostic
# pixels. Fractions use the immutable source coordinate space: left, top, right, bottom.
CROPS: dict[str, tuple[float, float, float, float]] = {
    "Abnormal bronchoalveolar lavage from a sarcoidosis showing a giant cell (center) and large numbers of inflammatory cells, mainly lymphocytes.png": (0.0, 0.0, 1.0, 0.78),
    "Acute inflammation in lobar pneumonia Histo.png": (0.0, 0.09, 1.0, 1.0),
    "Colonized cavity of Aspergilloma Histo.png": (0.0, 0.12, 1.0, 1.0),
    "Malignant Left Pleural Effusion CXR.png": (0.0, 0.0, 1.0, 0.88),
    "Normal Bronchus Histo.png": (0.0, 0.12, 1.0, 1.0),
    "Serpentine (Chrysotile)(90%) Asbestos EM.png": (0.0, 0.10, 1.0, 1.0),
}

ADD_CROPS: dict[str, tuple[float, float, float, float]] = {
    "Asbestos-Exposure.png": (0.0, 0.06, 1.0, 0.82),
    "Bronchiectasis-Gross-Pathology.png": (0.0, 0.08, 1.0, 1.0),
    "Chronic-Silicosis-Progressive-Massive-Fibrosis-Chest-Xray.png": (0.0, 0.07, 1.0, 1.0),
    "Congenital-Diaphragmatic-Hernia-Chest-Xray.jpg": (0.0, 0.12, 1.0, 1.0),
    "Crypto 2.png": (0.0, 0.08, 1.0, 1.0),
    "Haemophilus Influenzae Thumb Sign X Ray.png": (0.0, 0.24, 1.0, 1.0),
    "Mesothelioma-Ct.jpg": (0.0, 0.11, 1.0, 1.0),
}

COMPOSITES = {
    "Agenesis on Right Compensatory Hyperinflation on Left CT.png",
    "ARDS CXR.png",
    "Aspirated foreign bodies CXR.png",
    "Bronchopulmonary dysplasia CXR.png",
    "Congenital Lobar Emphysema (LUL) Improvement CXR.png",
    "CPAM and Empysema CT.png",
    "Diaphragmatic Eventration CXR 2.png",
    "Diaphragmatic Eventration CXR.png",
    "Emphysema Histo.png",
    "Empyema eith air from gas producing organisms CT.png",
    "Hyaline membrane disease, or neonatal respiratory distress syndrome Histo.png",
    "Invasive Fungal Sinusitis CT.png",
    "Normal Lung Large Histo.png",
    "Pectus Arcuatum Gross.png",
    "Pectus Excavatum Gross.png",
    "Pulmonary Hypertension Histo.png",
    "Recurrent Respiratory Papillomatosis Gross.png",
    "Right Pulmonary Agenesis CXR.png",
    "Septic Emboli CXR copy.png",
    "Severe COPD CXR.png",
    "Squamous Cell Carcinoma Sputum.png",
    "Squamous cell carcinoma of the lung, right upper lobe Golden S Sign CXR.png",
    "UIP Histo.png",
    "Viral Nuclear Inclusions Histo.png",
}

ADD_COMPOSITES = {
    "Bilateral-Pulmonary-Emboli.png",
    "Congenital-Diaphragmatic-Hernia-Chest-Xray.jpg",
    "Echocardiogram in Pulmonary Artery Hypertension (1:3).jpg",
    "Echocardiogram in Pulmonary Artery Hypertension (2:3).jpg",
    "Echocardiogram in Pulmonary Artery Hypertension (3:3).jpg",
    "Empyema.png",
    "Large cell carcinoma of the lung.jpg",
    "Nonspecific Interstitial Pneumonia (NSIP).jpg",
    "P065 Mesothelioma 01.jpeg",
    "P168 Plexiform Lesions.png",
    "P354 Kartagener S Syndrome.png",
    "P449 Klebsiella Pneumonia.png",
    "P529 CF Lung Disease.png",
    "Pneumonia CT.jpg",
    "Pulmonary Fibrosis Plain.jpg",
    "Sarcoidosis All.png",
    "Usual Interstitial Pneumonia (UIP).jpg",
}

CORRECTIONS = {
    "Abcess": "Abscess",
    "Abestosis": "Asbestosis",
    "Adenocarinoma": "Adenocarcinoma",
    "Atypicals": "Atypical",
    "Congential": "Congenital",
    "Empysema": "Emphysema",
    "Epiglotitis": "Epiglottitis",
    "Hamptom": "Hampton",
    "Intersitial": "Interstitial",
    "Medistinal": "Mediastinal",
    "Metastic": "Metastatic",
    "Sarcoidossi": "Sarcoidosis",
    "Silhoutte": "Silhouette",
}

ADD_MODALITY_OVERRIDES = {
    "Active TB - Diagnosis.png": "Histology",
    "Acute-Hypersensitivity-Pneumonitis.png": "CT",
    "Adenocarcinoma of the Lung.jpg": "Histology",
    "Anthracotic Pigment in Lung in Coal Worker's Pneumoconiosis.jpg": "Histology",
    "ARDS Hyaline Membrane.jpeg": "Histology",
    "ARDS X Ray.png": "X-ray",
    "Asbestos-Exposure.png": "Gross Pathology",
    "Asbestosis Gross.jpg": "Gross Pathology",
    "Aspergillosis.jpg": "Microscopy",
    "Aspergillus Fumigatus.jpg": "Microscopy",
    "Asteroid Bodies in Pulmonary Sarcoidosis.jpg": "Histology",
    "Bilateral Pleural Effusion.jpg": "CT",
    "Bilateral Upper Lobe Cavitary Lung Disease TB.jpg": "X-ray",
    "Bilateral-Pulmonary-Emboli.png": "CT",
    "B Asbestos Ferruginous Body Prussian Blue Stain.png": "Histology",
    "Blastomyces Dermatitidis (Yeast Form).jpg": "Microscopy",
    "Bronchiectasis Lung Specimens.jpg": "Gross Pathology",
    "Bronchiectasis Right Lung Saggital.jpg": "Gross Pathology",
    "Bronchiectasis-Gross-Pathology.png": "CT",
    "Bronchiectasis.jpg": "CT",
    "Bronchopneumonia.jpg": "Histology",
    "Bronchopulmonary Dysplasia.jpg": "X-ray",
    "Caseating granulomas with central necrosis and Langhans giant cell.png": "Histology",
    "Chronic Interstitial Lung Disease.jpg": "CT",
    "Chronic Rhinosinusitis with Nasal Polyps.jpg": "CT",
    "Chronic-Silicosis-Progressive-Massive-Fibrosis-Chest-Xray.png": "X-ray",
    "Coal Worker's Pneumoconiosis.png": "Histology",
    "Cocco Copy.png": "Histology",
    "Croup.jpeg": "X-ray",
    "Crypto 2.png": "Histology",
    "Crypto Capsule copy.png": "Histology",
    "Cryptococcus Neoformans India Ink Stain.png": "Microscopy",
    "Cryptogenic-Organizing-Pneumonia.png": "CT",
    "Congenital-Diaphragmatic-Hernia-Chest-Xray.jpg": "X-ray",
    "Diaphragmatic-Rupture-Mediastinal-Shift.png": "X-ray",
    "Echocardiogram in Pulmonary Artery Hypertension (1:3).jpg": "Echocardiography",
    "Echocardiogram in Pulmonary Artery Hypertension (2:3).jpg": "Echocardiography",
    "Echocardiogram in Pulmonary Artery Hypertension (3:3).jpg": "Echocardiography",
    "Empyema.png": "X-ray and CT",
    "Epiglottitis-with-Thumb-Sign.png": "X-ray",
    "Epithelioid Mesothelioma.jpg": "Histology",
    "Epithelioid-Mesothelioma.png": "Histology",
    "Ferruginous-Bodies.png": "Histology",
    "Haemophilus Influenzae Thumb Sign X Ray.png": "X-ray",
    "Hampton Hump in Pulmonary Infarction.jpg": "X-ray",
    "Hemosiderin-Laden Macrophages (Heart Failure Cells).png": "Histology",
    "Histoplasma Capsulatum (Mold Form).jpg": "Microscopy",
    "Hyaline Membranes in ARDS.jpg": "Histology",
    "Hyperinflation in COPD.jpg": "X-ray",
    "Hypersensitivity Pneumonitis HE 2.jpg": "Histology",
    "Hypersensitivity Pneumonitis HE.jpg": "Histology",
    "Hypersensitivity Pneumonitis.jpg": "CT",
    "Hypersensitivity-Pneumonitis.png": "Histology",
    "Idiopathic Pulmonary Fibrosis 1:2 Pain.jpg": "X-ray",
    "Idiopathic Pulmonary Fibrosis 2:2.jpg": "CT",
    "Invasive Aspergillosis.png": "Histology",
    "IPF X Ray.png": "X-ray",
    "Large cell carcinoma of the lung.jpg": "Histology",
    "Left-Hilar-Lung-Mass-Chest-Xray.jpg": "X-ray",
    "Left-Sided-Pleural-Effusion-in-Malignant-Mesothelioma-Frontal.jpg": "X-ray",
    "Lines-of-Zahn.jpg": "Histology",
    "Lymphocytic Infiltrate of Airways.png": "Histology",
    "Mesothelioma Gross.jpg": "Gross Pathology",
    "Mesothelioma-Ct.jpg": "CT",
    "Multinucleated Giant Cells in Pulmonary Sarcoidosis.jpg": "Histology",
    "NARDS.png": "X-ray",
    "Neonatal-Respiratory-Distress-Syndrome-Hyaline-Membranes.png": "Histology",
    "Noncaseating Granuloma in Sarcoidosis.jpg": "Histology",
    "Nonspecific Interstitial Pneumonia (NSIP).jpg": "CT",
    "P041 Respiratory Infections Pneumonia 04.jpeg": "Histology",
    "P005 Tuberculosis AFB Stain.png": "Histology",
    "P010 Primary Pulmonary Hypertension Plexiform Lesion.png": "Histology",
    "P058 Pulmonary Fibrosis 02.jpeg": "X-ray",
    "P058 Pulmonary Fibrosis 03.jpeg": "CT",
    "P063 Small Cell Carcinoma 01.jpeg": "Histology",
    "P065 Mesothelioma 01.jpeg": "Gross Pathology",
    "P068 Pulmonary Hypertension 01.jpeg": "Histology",
    "P070 Pneumothorax Chest Xrays 01.jpeg": "X-ray",
    "P070 Pneumothorax Chest Xrays 02.jpeg": "X-ray",
    "P073 Pleural Effusion Chest Xrays 02.jpeg": "X-ray",
    "P073 Pleural Effusion Chest Xrays 03.jpeg": "X-ray",
    "P165 PAH - Pulmonary Arterial Hypertension.png": "Histology",
    "P168 Plexiform Lesions.png": "Histology",
    "P182 Tuberculosis.png": "X-ray",
    "P350 Bronchiectasis 01.png": "CT",
    "P350 Bronchiectasis 02.png": "Gross Pathology",
    "P354 Kartagener S Syndrome.png": "X-ray and CT",
    "P369 Interstitial Lung Disease 01.png": "CT",
    "P378 Asbestosis 01.png": "X-ray",
    "P382 Hypersensitivity Pneumonitis.png": "Histology",
    "P415 Bronchopneumonia 01.png": "X-ray",
    "P449 Klebsiella Pneumonia.png": "X-ray and CT",
    "P459 Spontaneous PTX - Clinical Features and Diagnosis.png": "X-ray",
    "P463 Atelectasis - Alveolar Collapse.png": "X-ray",
    "P466 Pleural Effusion.png": "X-ray",
    "P482 Benign Pulmonary Nodules 02.png": "CT",
    "P484 Small Cell Cancer.png": "Histology",
    "P489 Squamous Cell Carcinoma.png": "Histology",
    "P490 Adenocarcinoma.png": "Histology",
    "P492 Bronchioloalveolar Carcinoma.png": "X-ray",
    "P493 Bronchioloalveolar Carcinoma 01.png": "Histology",
    "P493 Bronchioloalveolar Carcinoma 02.png": "Histology",
    "P494 Large Cell Carcinoma.png": "Histology",
    "P495 Carcinoid Tumor.png": "Immunohistochemistry",
    "P529 CF Lung Disease.png": "X-ray",
    "P559 Ghon Foci 02.png": "X-ray",
    "P612 Pulmonary Embolism - Diagnosis.png": "CT",
    "P613 Pulmonary Embolism - Diagnosis CT Angiogram.png": "CT",
    "P621 Pulmonary Embolism - Pathology Findings Lines of Zahn.png": "Histology",
    "Paracoccidioidomycosis Histology.png": "Histology",
    "Parapneumonic effusion.png": "X-ray",
    "Peripheral Opacity (Hampton Hump) from Pulmonary Embolism.jpg": "X-ray",
    "Pleural Effusion and Passive Atelectasis.jpg": "X-ray",
    "Pneumonia CT.jpg": "X-ray and CT",
    "Pneumothorax X Ray.jpeg": "X-ray",
    "Pulmonary Fibrosis Plain.jpg": "X-ray and CT",
    "Pulmonary Hamartoma.jpg": "Histology",
    "Pulmonary Large Cell Carcinoma.png": "Histology",
    "Pulmonary Sarcoidosis.jpg": "Histology",
    "Pulmonary-Adenocarcinoma.png": "Histology",
    "Pulmonary-Hypertension.png": "Histology",
    "Sarcoidosis All.png": "X-ray, CT, and pathology",
    "Sarcoidosis CT.jpg": "CT",
    "Silicosis X Ray.jpeg": "X-ray",
    "Small Cell Lung Cancer.jpg": "Histology",
    "Small Cell Lung Carcinoma HE.jpg": "Histology",
    "Small Cell Lung Carcinoma.jpg": "Histology",
    "Small Pulmonary Nodules.jpg": "CT",
    "Squamous Cell Carcinoma of the Lung.jpg": "Histology",
    "Streptococcus Pneumoniae (Pneumococci).jpg": "Microscopy",
    "Streptococcus Pneumoniae with Capsule.jpg": "Microscopy",
    "Usual Interstitial Pneumonia (UIP).jpg": "CT",
}

ADD_CONCEPT_OVERRIDES = {
    "A Sarcoidosis Noncaseating Granuloma Histology.png": "Noncaseating granuloma",
    "Active TB - Diagnosis.png": "Acid-fast bacilli consistent with pulmonary tuberculosis",
    "Acute-Hypersensitivity-Pneumonitis.png": "Patchy ground-glass opacity",
    "Asbestos-Exposure.png": "Asbestos-related calcified pleural plaque",
    "Aspergillosis.jpg": "Aspergillus septate hyphae",
    "Aspergillus Fumigatus.jpg": "Aspergillus fumigatus conidiophore",
    "Asteroid Bodies in Pulmonary Sarcoidosis.jpg": "Asteroid body in a multinucleated giant cell",
    "Bronchiectasis-Gross-Pathology.png": "Bronchiectasis",
    "Echocardiogram in Pulmonary Artery Hypertension (3:3).jpg": "Pulmonary arterial hypertension",
    "C Berylliosis Noncaseating Granuloma Histology.png": "Noncaseating granuloma",
    "Cocco Copy.png": "Coccidioides spherules",
    "Crypto 2.png": "Cryptococcus neoformans",
    "Crypto Capsule copy.png": "Encapsulated Cryptococcus neoformans",
    "Haemophilus Influenzae Thumb Sign X Ray.png": "Epiglottitis (thumb sign)",
    "Hypersensitivity Pneumonitis.jpg": "Patchy ground-glass opacity",
    "Multinucleated Giant Cells in Pulmonary Sarcoidosis.jpg": "Multinucleated giant cells in a noncaseating granuloma",
    "NARDS.png": "Neonatal respiratory distress syndrome",
    "P005 Respiratory Histology Overview 05.jpeg": "Normal pulmonary alveoli",
    "P005 Tuberculosis AFB Stain.png": "Acid-fast bacilli consistent with pulmonary tuberculosis",
    "P009 Sarcoidosis Noncaseating Granuloma Histology.png": "Noncaseating granuloma",
    "P041 Respiratory Infections Pneumonia 04.jpeg": "Acute pneumonia",
    "P058 Pulmonary Fibrosis 02.jpeg": "Pulmonary fibrosis",
    "P058 Pulmonary Fibrosis 03.jpeg": "Pulmonary fibrosis",
    "P063 Small Cell Carcinoma 01.jpeg": "Small cell lung carcinoma",
    "P065 Mesothelioma 01.jpeg": "Pleural mesothelioma",
    "P068 Pulmonary Hypertension 01.jpeg": "Pulmonary arterial hypertension",
    "P070 Pneumothorax Chest Xrays 01.jpeg": "Pneumothorax",
    "P070 Pneumothorax Chest Xrays 02.jpeg": "Pneumothorax",
    "P073 Pleural Effusion Chest Xrays 02.jpeg": "Pleural effusion",
    "P073 Pleural Effusion Chest Xrays 03.jpeg": "Pleural effusion",
    "P165 PAH - Pulmonary Arterial Hypertension.png": "Pulmonary arterial hypertension",
    "P168 Plexiform Lesions.png": "Plexiform lesions of pulmonary arterial hypertension",
    "P182 Tuberculosis.png": "Cavitary pulmonary tuberculosis",
    "P350 Bronchiectasis 01.png": "Bronchiectasis",
    "P350 Bronchiectasis 02.png": "Bronchiectasis",
    "P354 Kartagener S Syndrome.png": "Kartagener syndrome",
    "P369 Interstitial Lung Disease 01.png": "Fibrotic interstitial lung disease",
    "P378 Asbestosis 01.png": "Asbestosis",
    "P382 Hypersensitivity Pneumonitis.png": "Hypersensitivity pneumonitis",
    "P415 Bronchopneumonia 01.png": "Bronchopneumonia",
    "P449 Klebsiella Pneumonia.png": "Klebsiella pneumonia",
    "P459 Spontaneous PTX - Clinical Features and Diagnosis.png": "Pneumothorax",
    "P463 Atelectasis - Alveolar Collapse.png": "Atelectasis",
    "P466 Pleural Effusion.png": "Pleural effusion",
    "P482 Benign Pulmonary Nodules 02.png": "Benign calcified pulmonary nodule",
    "P484 Small Cell Cancer.png": "Small cell lung carcinoma",
    "P489 Squamous Cell Carcinoma.png": "Squamous cell lung carcinoma",
    "P490 Adenocarcinoma.png": "Pulmonary adenocarcinoma",
    "P492 Bronchioloalveolar Carcinoma.png": "Bronchioloalveolar carcinoma",
    "P493 Bronchioloalveolar Carcinoma 01.png": "Bronchioloalveolar carcinoma",
    "P493 Bronchioloalveolar Carcinoma 02.png": "Bronchioloalveolar carcinoma",
    "P494 Large Cell Carcinoma.png": "Large cell lung carcinoma",
    "P495 Carcinoid Tumor.png": "Pulmonary carcinoid tumor",
    "P529 CF Lung Disease.png": "Cystic fibrosis-associated bronchiectasis",
    "P559 Ghon Foci 02.png": "Ghon focus",
    "P612 Pulmonary Embolism - Diagnosis.png": "Acute pulmonary embolism",
    "P613 Pulmonary Embolism - Diagnosis CT Angiogram.png": "Acute pulmonary embolism",
    "P621 Pulmonary Embolism - Pathology Findings Lines of Zahn.png": "Lines of Zahn in thrombus",
    "Pneumonia CT.jpg": "Cavitating pneumonia with lung abscess",
    "Pulmonary Fibrosis Plain.jpg": "Pulmonary fibrosis",
    "Pulmonary-Adenocarcinoma.png": "Pulmonary adenocarcinoma",
    "Pulmonary-Hypertension.png": "Pulmonary arterial hypertension",
    "Pulmonary Sarcoidosis.jpg": "Noncaseating granulomas",
    "Noncaseating Granuloma in Sarcoidosis.jpg": "Noncaseating granuloma",
    "Sarcoidosis All.png": "Pulmonary sarcoidosis",
    "Small Pulmonary Nodules.jpg": "Multiple small pulmonary nodules",
    "Streptococcus Pneumoniae with Capsule.jpg": "Encapsulated Streptococcus pneumoniae",
}


FEATURE_RULES: list[tuple[str, str]] = [
    (r"^normal$", "symmetric normally aerated lungs without focal opacity, pleural collection, mass, or destructive change"),
    (r"normal pulmonary alveoli", "delicate open alveolar spaces separated by very thin septa without inflammatory filling, fibrosis, or architectural destruction"),
    (r"acid.fast bacilli", "slender red acid-fast rods standing out against a blue counterstained background"),
    (r"aspergillus.*conidiophore", "a septate stalk ending in a vesicle with radiating phialides and chains of conidia"),
    (r"aspergillus.*hyphae", "thin septate hyphae with acute-angle branching"),
    (r"blastomyc", "large thick-walled yeast with characteristic broad-based budding"),
    (r"coccidio", "large tissue spherules containing numerous endospores"),
    (r"cryptococcus|encapsulated cryptococcus", "round narrow-based budding yeast surrounded by a prominent polysaccharide capsule"),
    (r"histoplasma.*mold", "delicate hyphae bearing tuberculate macroconidia"),
    (r"histoplas", "small intracellular budding yeast clustered within macrophages"),
    (r"paracoccidio", "multiple narrow-based buds radiating from a mother yeast in a pilot-wheel pattern"),
    (r"streptococcus pneumoniae|pneumococci", "lancet-shaped paired cocci, with a clear capsule when specifically demonstrated"),
    (r"noncaseating granuloma", "a compact collection of epithelioid histiocytes and multinucleated giant cells without central caseous necrosis"),
    (r"multinucleated giant cells", "large fused histiocytes containing numerous nuclei within an organized granulomatous reaction"),
    (r"asteroid body", "a stellate eosinophilic inclusion within a multinucleated giant cell"),
    (r"anthracotic pigment|coal worker", "coarse black carbon pigment within macrophages and fibrotic pulmonary tissue"),
    (r"ferruginous bod|asbestos bodies", "golden-brown beaded ferruginous bodies coating a central asbestos fiber"),
    (r"lines of zahn", "alternating pale platelet-fibrin layers and darker red-cell-rich layers within an antemortem thrombus"),
    (r"hemosiderin.laden macrophage", "golden-brown hemosiderin granules within alveolar macrophages indicating prior alveolar hemorrhage or chronic congestion"),
    (r"patchy ground.glass opacity", "geographic bilateral ground-glass attenuation that does not completely obscure underlying vessels"),
    (r"calcified pulmonary nodule", "a sharply marginated pulmonary nodule containing dense central or laminated calcification"),
    (r"multiple small pulmonary nodules", "numerous discrete small rounded opacities distributed through both lungs"),
    (r"caseating granuloma", "central granular caseous necrosis rimmed by epithelioid histiocytes and Langhans-type giant cells"),
    (r"diaphragmatic rupture", "intrathoracic abdominal viscera with mediastinal displacement through a disrupted hemidiaphragm"),
    (r"large cell.*carcinoma|pulmonary large cell", "sheets of markedly pleomorphic malignant epithelial cells without glandular or squamous differentiation"),
    (r"lymphocytic infiltrate.*airway", "dense mononuclear inflammation centered on and surrounding a small airway"),
    (r"nonspecific interstitial pneumonia|\bnsip\b", "bilateral basal ground-glass and fine reticular change with relative subpleural sparing and limited honeycombing"),
    (r"vocal cord nodule", "small symmetric benign-appearing nodules arising at the free margins of the true vocal folds"),
    (r"interstitial pneumonia", "alveolar septal inflammatory thickening with relative preservation of open air spaces"),
    (r"ghon complex", "a peripheral primary tuberculous focus accompanied by regional hilar nodal disease"),
    (r"bronchioloalveolar carcinoma", "neoplastic cells growing along pre-existing alveolar septa in a lepidic pattern"),
    (r"acute pneumonia", "neutrophil-rich intra-alveolar exudate filling air spaces while the supporting lung framework remains visible"),
    (r"pulmonary fibrosis|\bipf\b", "bilateral basal and subpleural reticulation with traction change or honeycombing"),
    (r"pulmonary arterial hypertension", "marked small-pulmonary-artery medial and intimal remodeling, with plexiform change in advanced disease"),
    (r"cavitary pulmonary tuberculosis", "upper-lung cavitary destructive opacity with surrounding fibrotic or infiltrative change"),
    (r"kartagener", "the combination of bronchiectasis and mirror-image thoracoabdominal orientation from situs inversus"),
    (r"klebsiella pneumonia", "dense lobar consolidation with bulging fissure or cavitation typical of severe necrotizing bacterial pneumonia"),
    (r"^atelectasis$", "focal lung opacity accompanied by volume loss and displacement of fissures, hilum, or mediastinum toward the collapse"),
    (r"cavitating pneumonia", "air-space consolidation containing a thick-walled cavity or abscess"),
    (r"pulmonary alveolus with alveolar macrophages", "large macrophages lying freely within otherwise thin-walled alveolar spaces"),
    (r"organized (?:venous )?(?:thromboembol|embol)", "a fibrotic, recanalized thrombus incorporated into the vessel wall, indicating an older organized event"),
    (r"recent thromboembol", "a fresh occlusive thrombus with preserved red-cell and fibrin laminations but no mature recanalization"),
    (r"smaller,? peripheral pulmonary thromboembol", "an occlusive thrombus lodged in a small peripheral pulmonary artery"),
    (r"deep venous thrombosis", "a noncompressible deep vein containing intraluminal thrombus on ultrasound"),
    (r"amphibole asbestos", "straight, rigid needle-like mineral fibers rather than curled serpentine fibers"),
    (r"chrysotile asbestos", "curled, flexible serpentine mineral fibers rather than straight rigid amphibole fibers"),
    (r"\bacinus\b", "a terminal bronchiole giving rise to respiratory bronchioles, alveolar ducts, and alveoli within one gas-exchanging unit"),
    (r"normal mesothelium", "a single bland layer of flattened-to-cuboidal mesothelial cells lining the pleural surface"),
    (r"^bronchus$|^bronchi$", "a conducting airway with pseudostratified ciliated epithelium, submucosal glands, smooth muscle, and cartilage"),
    (r"^bronchiole$", "a small conducting airway lacking cartilage and submucosal glands, with a prominent smooth-muscle wall"),
    (r"acute infectious bronchiolitis", "peribronchial thickening with hyperinflation and patchy subsegmental atelectatic opacity in a young child"),
    (r"acute respiratory distress|acute diffuse alveolar damage", "bilateral diffuse air-space opacity with hyaline membranes and acute alveolar injury"),
    (r"right lung agenesis|lung agenesis", "absence of the right lung with ipsilateral volume loss and compensatory hyperinflation of the left lung"),
    (r"bilateral pneumothoraces", "bilateral visceral pleural lines with absent peripheral lung markings on both sides"),
    (r"pulmonary effusion.*(?:chf|heart failure)|bilateral pulmonary effusion", "bilateral dependent pleural fluid with menisci and accompanying signs of congestive heart failure"),
    (r"large right.sided pulmonary effusion", "a large right pleural-fluid meniscus with compressive atelectasis of the adjacent lung"),
    (r"bleomycin|amiodarone", "bilateral basal-predominant reticular interstitial opacity consistent with drug-associated fibrotic lung injury"),
    (r"bacterial pneumonia|community acquired pneumonia|lung consolidation pneumonia", "focal lobar or segmental air-space opacity, often containing air bronchograms"),
    (r"congestion phase of pneumonia", "engorged alveolar capillaries with proteinaceous intra-alveolar edema and relatively few neutrophils"),
    (r"^pneumonia$|pneumonia hist", "neutrophil-rich intra-alveolar exudate filling air spaces while the underlying lung framework remains recognizable"),
    (r"round pneumonia", "a rounded focus of air-space consolidation, often with air bronchograms and typically seen in a child"),
    (r"septic embol", "multiple bilateral peripheral nodules, often cavitary or wedge-shaped from infected vascular emboli"),
    (r"pulmonary abscess", "a thick-walled cavitary lesion with central suppurative necrosis or an air-fluid level"),
    (r"granulomatosis with polyangiitis", "necrotizing granulomatous inflammation and vasculitis, often producing multiple cavitary pulmonary nodules"),
    (r"healed fibrocalcific granuloma", "a densely fibrotic old granuloma containing central dystrophic calcification"),
    (r"interstitial fibrosis|interstitial lung disease", "diffuse reticular interstitial opacity or thickened fibrotic alveolar septa rather than focal air-space filling"),
    (r"jeune syndrome", "a narrow bell-shaped thorax with short, horizontally oriented ribs"),
    (r"lymphadenopathy", "enlarged hilar or mediastinal lymph nodes forming lobulated soft-tissue fullness"),
    (r"complicated sinusitis", "opacified paranasal sinus with marked mucosal thickening and an adjacent rim-enhancing collection or destructive extension"),
    (r"tumor.?thick wall", "an irregular thick-walled cavitary lung mass, favoring a cavitating neoplasm over a thin-walled benign cyst"),
    (r"normal (acinus|alveol)", "delicate open alveoli separated by thin septa without inflammatory filling or fibrosis"),
    (r"normal (bronchus|airway|bronchi|bronchiole)", "an intact airway lumen with the expected epithelium, wall layers, and surrounding aerated parenchyma"),
    (r"normal carina", "a smooth central airway bifurcation without an obstructing endobronchial lesion"),
    (r"normal (ct|infant|lung)", "symmetric aerated lungs without a focal opacity, pleural collection, or destructive lesion"),
    (r"trachea", "respiratory epithelium, submucosal glands, cartilage, and the posterior smooth-muscle wall"),
    (r"pores of kohn", "small interalveolar channels connecting adjacent air spaces"),
    (r"asbestos body", "a golden-brown beaded ferruginous body with a translucent central fiber"),
    (r"asbestosis|pleural plaque", "lower-lung fibrotic change or sharply marginated pleural-based calcified plaques"),
    (r"silico|silicosis", "a rounded whorled hyalinized collagen nodule or upper-lung silicotic scarring"),
    (r"honeycomb|usual interstitial|idiopathic pulmonary fibrosis|\buip\b", "basal subpleural reticulation with traction change and stacked cystic honeycombing"),
    (r"hypersensitivity pneumonitis", "a bronchiolocentric interstitial infiltrate with small poorly formed non-necrotizing granulomas"),
    (r"rheumatoid", "fibrotic interstitial lung disease occurring with the displayed rheumatoid clinical context"),
    (r"radiation damage", "sharply geographic consolidation or fibrosis conforming to a prior radiation field"),
    (r"sarcoid|schaumann|asteroid body", "non-necrotizing granulomas, sometimes with laminated Schaumann or stellate asteroid inclusions"),
    (r"granuloma.*tuberc|necrotizing granuloma", "central caseous necrosis rimmed by epithelioid histiocytes and multinucleated giant cells"),
    (r"miliary", "innumerable tiny, fairly uniform nodules distributed throughout both lungs"),
    (r"cavitary tb|secondary tb|old right upper lobe|\btb\b", "upper-lung cavitation, fibrotic volume loss, or clustered apical destructive disease"),
    (r"consolidative tb", "parenchymal consolidation accompanied by prominent hilar or mediastinal lymphadenopathy"),
    (r"ghon focus", "a peripheral primary parenchymal focus with regional lymphatic or nodal involvement"),
    (r"aspergilloma|fungal ball", "a rounded intracavitary mass separated from the cavity wall by a crescent of air"),
    (r"invasive asperg|invasive fungal", "tissue-invasive necrosis or destructive sinonasal/pulmonary disease rather than a simple colonized cavity"),
    (r"viral pneumonia|viral nuclear", "interstitial inflammation with viral cytopathic nuclear inclusions rather than dense alveolar neutrophils"),
    (r"atypical|mycoplasma", "a diffuse interstitial or patchy peribronchial pattern without dense lobar air-space consolidation"),
    (r"bronchopneumonia", "patchy bronchiolocentric suppurative consolidation involving multiple lobules"),
    (r"lobar pneumonia|hepatization|lobar consolidation", "confluent air-space filling across a lobe, with the firm red-to-gray hepatization pattern when gross"),
    (r"necrotizing pneumonia", "consolidation containing cavitation or nonenhancing necrotic parenchyma"),
    (r"organizing pneumonia|\bboop\b|\bcop\b", "polypoid fibroblastic plugs within distal air spaces with preserved underlying architecture"),
    (r"aspiration pneumonia", "airway-centered inflammation containing aspirated material and a dependent distribution"),
    (r"empyema", "a loculated pleural fluid collection with pleural thickening or a lentiform contour"),
    (r"parapneumonic effusion", "pleural fluid adjacent to pneumonic consolidation, often with internal septations when complicated"),
    (r"pleural effusion", "dependent pleural fluid with a meniscus, blunted costophrenic angle, or compressive atelectasis"),
    (r"pneumothorax", "a visceral pleural line with absent peripheral lung markings and increased lucency"),
    (r"tension pneumothorax", "a large pneumothorax with mediastinal shift and depression of the ipsilateral diaphragm"),
    (r"round atelectasis", "a pleural-based rounded opacity with curving bronchovascular bundles forming a comet-tail appearance"),
    (r"golden s|post-obstructive|resorption atelectasis", "lobar volume loss distorted around a central obstructing mass, producing an S-shaped fissure"),
    (r"compression atelectasis", "passive lung collapse immediately adjacent to pleural air or fluid"),
    (r"contraction atelectasis", "fibrotic volume loss with architectural distortion and traction on adjacent structures"),
    (r"diaphragmatic eventration", "smooth focal elevation of an intact hemidiaphragm without herniated abdominal viscera"),
    (r"diaphragmatic hernia|scaphoid abdomen", "abdominal viscera occupying the hemithorax with compressed ipsilateral lung and a small abdomen"),
    (r"congenital lobar emphysema", "marked lobar hyperinflation with compression of adjacent lung and mediastinal displacement"),
    (r"cpam", "a congenital multicystic intrapulmonary lesion replacing part of a developing lung"),
    (r"pulmonary sequestration", "nonfunctioning lung tissue supplied by an anomalous systemic artery"),
    (r"bronchogenic cyst", "a well-circumscribed fluid-filled lesion near the tracheobronchial tree with respiratory-type lining"),
    (r"pulmonary agenesis", "absence of one lung and pulmonary vasculature with compensatory hyperinflation of the opposite lung"),
    (r"bronchopulmonary dysplasia", "coarse heterogeneous neonatal lung opacity with simplified enlarged air spaces on histology"),
    (r"hyaline membrane|neonatal respiratory", "diffuse neonatal ground-glass opacity or eosinophilic hyaline membranes lining collapsed alveoli"),
    (r"ards|diffuse alveolar damage", "bilateral diffuse air-space opacity with hyaline membranes and acute alveolar injury"),
    (r"cardiogenic|congestive heart failure|kerley", "cardiomegaly with vascular congestion, septal lines, and central alveolar edema"),
    (r"alveolar hemorrhage|goodpasture", "diffuse alveolar blood and hemosiderin-laden macrophage injury rather than purulent exudate"),
    (r"pulmonary edema", "pink proteinaceous intra-alveolar fluid or bilateral central air-space opacity"),
    (r"bronchiectasis", "permanently dilated thick-walled bronchi with lack of normal tapering and a signet-ring appearance"),
    (r"chronic bronchitis", "mucous-gland and goblet-cell enlargement with airway wall inflammation"),
    (r"asthma", "airway smooth-muscle thickening, mucus plugging, and hyperinflation rather than focal consolidation"),
    (r"centri.?acinar emphysema", "enlarged destroyed respiratory air spaces centered on respiratory bronchioles with relative distal sparing"),
    (r"emphysema|vanishing lung|pink puffer|\bcopd\b", "hyperinflation, attenuated vascular markings, flattened diaphragms, or large bullous air spaces"),
    (r"blue bloater", "the chronic-bronchitis-predominant COPD phenotype with cyanosis and a stocky body habitus"),
    (r"respiratory bronchiolitis", "pigmented macrophages clustered in respiratory bronchioles and adjacent alveoli"),
    (r"obliterative bronchiolitis", "concentric fibrous narrowing or obliteration of small-airway lumina"),
    (r"squamous metaplasia", "replacement of ciliated respiratory epithelium by stratified squamous epithelium"),
    (r"carcinoid", "an endobronchial tan mass composed of uniform neuroendocrine cells in nests or trabeculae"),
    (r"adenocarcinoma", "malignant gland formation, mucin production, or a peripheral infiltrative lung mass"),
    (r"squamous cell", "keratin pearls and intercellular bridges or a centrally located cavitating mass"),
    (r"small cell", "sheets of small hyperchromatic cells with nuclear molding and neuroendocrine marker expression"),
    (r"mesothelioma", "diffuse nodular pleural thickening encasing the lung or malignant mesothelial proliferation"),
    (r"hamartoma", "a sharply circumscribed nodule containing disorganized cartilage, fat, and fibrous tissue"),
    (r"metasta|lymphangitic", "multiple bilateral nodules or diffuse interstitial tumor spread along lymphatic routes"),
    (r"central tumor|endobronchial tumor", "a hilar or endobronchial mass causing airway obstruction and distal collapse"),
    (r"peripheral tumor|lung mass|lung nodule|primary lung cancer|non-small cell", "a focal pulmonary soft-tissue opacity distinct from surrounding aerated lung"),
    (r"lymphoma", "bulky mediastinal soft tissue narrowing or displacing the trachea"),
    (r"pleural mesothelioma", "irregular pleural-based tumor and effusion rather than a solitary intraparenchymal nodule"),
    (r"pulmonary embol|pulmonary thromboembol", "an intraluminal pulmonary-artery filling defect or its characteristic secondary radiographic sign"),
    (r"hampton", "a peripheral pleural-based wedge-shaped opacity representing pulmonary infarction"),
    (r"fleischner", "prominent enlargement of a central pulmonary artery associated with acute pulmonary embolism"),
    (r"pulmonary infarct", "a peripheral wedge-shaped hemorrhagic lesion caused by vascular occlusion"),
    (r"dvt", "noncompressible venous thrombus with absent normal luminal collapse on ultrasound"),
    (r"plexiform|pulmonary hypertension", "concentric and plexiform remodeling of small pulmonary arteries"),
    (r"av malformation", "a direct dilated connection between a pulmonary artery and vein"),
    (r"organized (thrombo|embol)|vte", "recanalized fibrous thrombus incorporated into the vessel wall"),
    (r"air bronchogram", "air-filled branching bronchi visible within surrounding opacified lung"),
    (r"silhouette sign", "loss of a normal cardiomediastinal or diaphragmatic border from adjacent air-space disease"),
    (r"alveolar lung filling", "fluffy confluent air-space opacities with indistinct margins and possible air bronchograms"),
    (r"interstitial lung filling", "reticular or linear opacity involving the supporting interstitium"),
    (r"nodular lung filling", "multiple discrete rounded pulmonary opacities rather than confluent air-space disease"),
    (r"near normal lung filling", "preserved lung lucency without a dominant alveolar, interstitial, or nodular filling pattern"),
    (r"croup|steeple", "symmetric subglottic airway narrowing producing the steeple sign"),
    (r"epiglott", "an enlarged edematous epiglottis or swollen supraglottic tissue"),
    (r"peritonsillar", "a unilateral rim-enhancing peritonsillar collection with mass effect"),
    (r"papillomatosis", "multiple exophytic papillomatous airway lesions with possible cavitating pulmonary spread"),
    (r"laryngomalacia", "dynamic-appearing supraglottic collapse with an omega-shaped epiglottic configuration"),
    (r"tracheomalacia", "marked expiratory narrowing or collapse of the tracheal lumen"),
    (r"vocal fold", "a focal mucosal lesion arising directly from the vocal fold"),
    (r"nasal polyp|polyposis", "smooth polypoid soft tissue filling the nasal cavity or paranasal sinuses"),
    (r"pectus excavatum|haller", "posterior displacement of the sternum with reduced anteroposterior chest diameter"),
    (r"pectus carinatum|pectus arcuatum", "anterior protrusion of the sternum and adjacent costal cartilages"),
    (r"scoliosis|kyphosis|ankylosing", "marked spinal deformity producing restrictive chest-wall mechanics"),
    (r"broken ribs", "cortical discontinuity or displaced rib fragments at the indicated chest wall"),
    (r"dextrocardia|situs invert", "right-sided cardiac apex with mirror-image thoracoabdominal orientation when complete"),
    (r"syringomyelia", "a longitudinal fluid cavity within the spinal cord"),
    (r"chiari", "inferior displacement of cerebellar tonsillar tissue through the foramen magnum"),
    (r"duchenne", "reduced chest expansion and dependent atelectatic change in the setting of neuromuscular weakness"),
    (r"foreign bod", "focal air trapping or unilateral hyperinflation from an aspirated airway obstruction"),
    (r"pulmonary contusion", "patchy nonsegmental air-space opacity after trauma without a defined lobar boundary"),
]


def digest_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def stable_id(prefix: str, value: str, length: int = 12) -> str:
    return f"{prefix}_{hashlib.sha256(value.encode('utf-8')).hexdigest()[:length]}"


def dhash(image: Image.Image, size: int = 16) -> str:
    gray = image.convert("L").resize((size + 1, size), Image.Resampling.LANCZOS)
    pixels = list(gray.get_flattened_data())
    bits = 0
    for y in range(size):
        row = y * (size + 1)
        for x in range(size):
            bits = (bits << 1) | int(pixels[row + x] > pixels[row + x + 1])
    return f"{bits:0{size * size // 4}x}"


def clean_text(value: str) -> str:
    value = re.sub(r"\s+", " ", value).strip(" ._-")
    for wrong, right in CORRECTIONS.items():
        value = value.replace(wrong, right)
    value = re.sub(r"\bCF\b", "Cystic fibrosis", value)
    return value


def modality_for(name: str, collection_key: str = "rename") -> str:
    if collection_key == "third_party" and name in ADD_MODALITY_OVERRIDES:
        return ADD_MODALITY_OVERRIDES[name]
    folded = name.casefold()
    stem = clean_text(Path(name).stem).casefold()
    if "c xr" in folded:
        folded = folded.replace("c xr", "cxr")
    tokens = set(re.findall(r"[a-z0-9]+", folded))
    if ("cxr" in tokens or "x ray" in folded) and "ct" in tokens:
        return "X-ray and CT"
    if ("cxr" in tokens or "x ray" in folded) and "histo" in folded:
        return "X-ray and pathology"
    if "gross" in tokens and "histo" in folded:
        return "Gross pathology and histology"
    if re.search(r"\bif\b", folded):
        return "Immunohistochemistry"
    if "histo" in folded or "metaplasia" in folded or "metalplasia" in folded:
        return "Histology"
    if "gross" in tokens or name in {"Blue Bloater.png", "Pink Puffer.png", "Invasive Aspergillus.png"}:
        return "Gross Pathology" if "gross" in tokens or "aspergillus" in folded else "Clinical Image"
    if "angiogram" in folded:
        return "Angiography"
    if re.search(r"\bem\b", folded):
        return "Electron Microscopy"
    if "diagram" in folded:
        return "Diagram"
    if re.search(r"\b(us|echo)\b", folded):
        return "Ultrasound"
    if re.search(r"\bct\b", folded):
        return "MRI" if "syringomyelia" in folded else "CT"
    if "cxr" in tokens or "x ray" in folded:
        return "X-ray"
    if "sputum" in folded or "bronchoalveolar lavage" in folded:
        return "Cytology"
    if stem in {"pulmonary edema", "asbestosis body"}:
        return "Histology"
    if stem in {"acute asthma attack", "alveolar lung filling pattern", "interstitial lung filling pattern", "near normal lung filling pattern", "nodular lung filling pattern", "large right sided pulmonary effusion", "cpam type 3"} or stem.startswith("congestive heart failure stage"):
        return "X-ray"
    if stem.startswith("nasal polyps"):
        return "Clinical Image"
    return "Other"


RENAME_CONCEPT_OVERRIDES = {
    "Normal Histo.png": "Normal bronchus",
}


def concept_for(name: str, collection_key: str = "rename") -> str:
    if collection_key == "third_party" and name in ADD_CONCEPT_OVERRIDES:
        return ADD_CONCEPT_OVERRIDES[name]
    if collection_key == "rename" and name in RENAME_CONCEPT_OVERRIDES:
        return RENAME_CONCEPT_OVERRIDES[name]
    value = Path(name).stem
    if collection_key == "third_party":
        value = value.replace("_", " ").replace("-", " ")
        value = re.sub(r"^[A-F]\s+", "", value, flags=re.I)
        value = re.sub(r"^P\d+\s+", "", value, flags=re.I)
        value = re.sub(r"\s+\d+:\d+(?:\s+Pain)?$", "", value, flags=re.I)
        value = re.sub(r"\s+(?:0[1-5])$", "", value, flags=re.I)
    value = re.sub(r"\s+", " ", value).strip()
    # Strip variant suffixes first.
    value = re.sub(r"\s+copy$", "", value, flags=re.I)
    if not re.search(r"\b(?:type|stage)\s+[234]$", value, flags=re.I):
        value = re.sub(r"\s+[234]$", "", value)
    # Strip power and modality labels while preserving the medical concept.
    value = re.sub(r"\s+(high|medium|low)\s+power\s+histo$", "", value, flags=re.I)
    value = re.sub(r"\s+if(?:\s+(?:cd56|ttf-?1|keratin|chromogranin))?$", "", value, flags=re.I)
    previous = None
    while previous != value:
        previous = value
        value = re.sub(r"\s+(?:cxr\s+ct|ct\s+cxr|cxr\s+histo|gross\s+histo)$", "", value, flags=re.I)
        value = re.sub(r"\s+(?:cxr|ct|histo(?:logy)?|gross|diagram|us|echo|em|angiogram|chest\s+xrays?|x\s*ray|xray|sputum|he)$", "", value, flags=re.I)
    value = re.sub(r"\s+\((?:lul|rul)\)$", "", value, flags=re.I)
    value = clean_text(value)
    replacements = {
        "Abnormal bronchoalveolar lavage from a sarcoidosis showing a giant cell (center) and large numbers of inflammatory cells, mainly lymphocytes": "Sarcoidosis (lymphocytic bronchoalveolar lavage)",
        "Asbestosis Body": "Asbestos body",
        "Amphiboles Rod shape Asbestos": "Amphibole asbestos fibers",
        "Serpentine (Chrysotile)(90%) Asbestos": "Chrysotile asbestos fibers",
        "Acute Respiratory Distress Syndrome (non-cardiogenic pulmonary edema)": "Acute respiratory distress syndrome",
        "Hyaline membrane disease, or neonatal respiratory distress syndrome Ground Glass": "Neonatal respiratory distress syndrome",
        "Hyaline membrane disease, or neonatal respiratory distress syndrome": "Neonatal respiratory distress syndrome",
        "Similar intra-alveolar process (aka organization) BOOP:COP": "Organizing pneumonia",
        "Polypoid intra-lumenal connective tissue mass BOOP:COP": "Organizing pneumonia",
        "BOOP:COP": "Organizing pneumonia",
        "Type 4 CPAM versus PPB": "Type 4 CPAM versus pleuropulmonary blastoma",
        "GPA": "Granulomatosis with polyangiitis",
        "DVT": "Deep venous thrombosis",
        "VTE Organized Embolus": "Organized venous thromboembolus",
        "Pulmonary Metalplasia": "Pulmonary epithelial metaplasia",
        "Parietal Pleural Plaques Dense collagenous plaque with \"basket-weave\" pattern of collagen": "Asbestos-related pleural plaque",
        "Multicystic lesion with atelectasis and bronchiectasis CPAM with Pulmonary Sequestration": "CPAM with pulmonary sequestration",
        "Dense lobar consolidation (2 lobes) with \"gray hepatization\" in Pneumococcal pneumonia": "Gray hepatization of lobar pneumonia",
        "Parenchymal remodeling with cystic change (honeycombing) Idiopathic Pulmonary Fibrosis": "Honeycomb change in idiopathic pulmonary fibrosis",
        "Characteristic \"lymphangitic\" distribution of granulomata in sarcoidosis": "Lymphangitic granulomas of sarcoidosis",
        "COPD (predominant emphysema as gas trapping) and a primary lung cancer": "Emphysema with primary lung cancer",
        "CHF with Cardiomegaly and Pulmonary (Interstitial and Alveolar) Edema": "Cardiogenic pulmonary edema",
        "Congestive Heart Failure Stage Il- Interstitial Edema Kerley B Lines": "Interstitial cardiogenic pulmonary edema (Kerley B lines)",
        "Healed, fibrocalcife granuloma with central dystrophic calcification": "Healed fibrocalcific granuloma",
        "Squamous cell carcinoma of the lung, right upper lobe Golden S Sign": "Golden S sign from obstructing squamous cell carcinoma",
        "Consolidation, possible necrotizing pneumonia and pleural effusion": "Necrotizing pneumonia with pleural effusion",
        "Very large CPAM Severe Right Hyperinflation with multiple septae": "Large CPAM with right lung hyperinflation",
        "Poorly-formed granuloma from Hypersensitivity Pneumonitis": "Hypersensitivity pneumonitis",
        "Honeycombing Internal Idiopathic Pulmonary Fibrosis Lung": "Honeycomb lung from idiopathic pulmonary fibrosis",
        "Scaphoid Abdomen from Congenital Diaphramatic Herniation": "Congenital diaphragmatic hernia with scaphoid abdomen",
        "Cobblestone External Idiopathic Pulmonary Fibrosis Lung": "Pleural cobblestoning in idiopathic pulmonary fibrosis",
        "Agenesis on Right Compensatory Hyperinflation on Left": "Right lung agenesis with left compensatory hyperinflation",
        "Recurrent Respiratory Papillomatosis Pulm Involvment": "Pulmonary involvement by recurrent respiratory papillomatosis",
        "Trauma Induced Diffuse Alveolar Damage in ARDS": "Trauma-induced diffuse alveolar damage",
    }
    return replacements.get(value, value)


def topic_for(concept: str) -> str:
    folded = concept.casefold()
    groups = [
        ("Normal anatomy", ("normal ", "acinus", "bronchi histo", "bronchus histo", "bronchiole", "trachea", "carina", "pores of kohn")),
        ("Pleural disease", ("pneumothorax", "pleural effusion", "empyema", "pleural plaque", "mesothelioma", "parapneumonic")),
        ("Pulmonary vascular", ("embol", "thrombo", "dvt", "infarct", "pulmonary hypertension", "plexiform", "av malformation", "fleischner", "hampton")),
        ("Infection", ("pneumonia", "tuberc", " tb", "tb ", "abscess", "asperg", "fungal", "ghon", "miliary")),
        ("Interstitial lung disease", ("fibrosis", "interstitial", "honeycomb", "uip", "asbest", "silico", "sarcoid", "hypersensitivity", "rheumatoid", "radiation")),
        ("Airway and obstructive", ("asthma", "emphysema", "copd", "bronchiect", "bronchitis", "bronchiolitis", "tracheomalacia", "blue bloater", "pink puffer")),
        ("Neoplasm", ("carcinoma", "cancer", "tumor", "neoplasm", "hamartoma", "carcinoid", "metasta", "lymphoma", "mesothelioma", "papillomatosis")),
        ("Congenital and chest wall", ("congenital", "cpam", "sequestration", "agenesis", "bronchogenic cyst", "pectus", "scoliosis", "kyphosis", "diaphragmatic", "jeune", "dextrocardia", "ankylosing")),
        ("Acute lung injury and edema", ("ards", "alveolar damage", "pulmonary edema", "heart failure", "alveolar hemorrhage", "goodpasture", "hyaline membrane")),
        ("Upper airway", ("epiglott", "croup", "tonsillar", "sinus", "nasal", "laryng", "vocal fold")),
        ("Imaging patterns", ("lung filling", "air bronchogram", "silhouette", "atelectasis", "broken ribs", "contusion", "foreign bod")),
    ]
    padded = f" {folded} "
    for topic, terms in groups:
        if any(term in padded for term in terms):
            return topic
    return "Pulmonary pathology"


def modality_family(modality: str) -> str:
    if modality in {"X-ray", "CT", "MRI", "Angiography", "Ultrasound", "Echocardiography", "X-ray and CT", "X-ray and pathology", "X-ray, CT, and pathology"}:
        return "imaging"
    if modality in {"Histology", "Microscopy", "Immunohistochemistry", "Electron Microscopy", "Cytology", "Gross pathology and histology"}:
        return "microscopy"
    if modality == "Gross Pathology":
        return "gross"
    if modality == "Diagram":
        return "diagram"
    return "clinical"


def feature_for(concept: str, modality: str) -> str:
    folded = concept.casefold()
    for pattern, feature in FEATURE_RULES:
        if re.search(pattern, folded):
            return feature
    fallbacks = {
        "imaging": "a characteristic distribution, density, and anatomic localization different from the displayed imaging pattern",
        "microscopy": "a different dominant cell population, tissue architecture, and distribution of injury",
        "gross": "a different lesion distribution, border, color, and cut-surface appearance",
        "diagram": "a different anatomic relationship or developmental connection",
        "clinical": "a different visible morphology and anatomic distribution",
    }
    return fallbacks[modality_family(modality)]


def stem_for(modality: str, joint: bool, concept: str) -> tuple[str, str]:
    scope = "all displayed panels together" if joint else "the complete displayed image"
    normal = concept.casefold().startswith("normal ")
    if modality == "X-ray":
        stem = "Which normal pattern is demonstrated on this complete chest radiograph?" if normal else "Which diagnosis or named sign best explains the dominant pattern on this complete chest radiograph?"
    elif modality in {"CT", "MRI"}:
        stem = f"Which diagnosis or anatomic abnormality best matches the dominant {modality} finding in {scope}?"
    elif modality in {"X-ray and CT", "X-ray and pathology", "X-ray, CT, and pathology", "Gross pathology and histology"}:
        stem = f"Considering {scope}, which diagnosis best unifies the visible findings?"
    elif modality in {"Histology", "Microscopy"}:
        stem = f"Which diagnosis, tissue, or pathologic process best matches the dominant microscopic morphology in {scope}?"
    elif modality == "Immunohistochemistry":
        stem = f"Which diagnosis best matches the immunostaining pattern and cellular morphology in {scope}?"
    elif modality == "Electron Microscopy":
        stem = f"Which material or microanatomic structure is identified by the ultrastructural appearance in {scope}?"
    elif modality == "Gross Pathology":
        stem = f"Which diagnosis or anatomic abnormality best matches the gross morphology in {scope}?"
    elif modality == "Diagram":
        stem = f"Which pulmonary structure, anomaly, or intervention is represented by the relationships in {scope}?"
    elif modality in {"Ultrasound", "Echocardiography"}:
        stem = f"Which diagnosis best matches the sonographic appearance in {scope}?"
    elif modality == "Angiography":
        stem = f"Which vascular abnormality is demonstrated by the contrast-filled vessels in {scope}?"
    elif modality == "Cytology":
        stem = f"Which diagnosis or process best matches the dominant cells in {scope}?"
    else:
        stem = f"Which pulmonary diagnosis, phenotype, or structure best matches the visible finding in {scope}?"
    return stem, scope


# Groups of concept names that refer to the same underlying diagnosis despite
# different source-file wording (added-detail suffixes, word reordering, or
# synonymous phrasing). Members of the same group are never offered as
# distractors against each other, even though each source image remains its
# own separate scored question.
CONCEPT_SYNONYM_GROUPS: list[set[str]] = [
    {"epiglottitis with thumb sign", "epiglottitis thumb sign", "acute epiglottitis"},
    {
        "ards hyaline membrane",
        "ards hyaline membranes",
        "hyaline membranes in ards",
        "ards intraalveolar hyaline membranes",
        "neonatal respiratory distress syndrome hyaline membranes",
    },
    {
        "large cell lung carcinoma",
        "large cell carcinoma of the lung",
        "pulmonary large cell carcinoma",
        "large cell lung carcinoma pleomorphic giant cells",
    },
    {
        "small cell carcinoma",
        "small cell lung carcinoma",
        "small cell lung cancer",
        "small cell lung carcinoma small dark blue cells",
        "small cell",
    },
    {
        "squamous cell carcinoma",
        "squamous cell carcinoma of the lung",
        "squamous cell carcinoma of the lung right upper lobe",
        "squamous cell lung carcinoma",
        "squamous cell carcinoma central lung",
        "squamous cell carcinoma intercellular bridges",
        "squamous cell carcinoma keratin pearls",
    },
    {
        "bronchiectasis due cystic fibrosis",
        "bronchiectasis and cystic fibrosis",
        "cystic fibrosis with bronchiectasis",
        "cystic fibrosis associated bronchiectasis",
    },
    {
        "hampton hump pulmonary embolism",
        "hampton s hump pulmonary embolism",
        "hampton hump in pulmonary infarction",
        "peripheral opacity hampton hump from pulmonary embolism",
    },
    {
        "ipf",
        "idiopathic pulmonary fibrosis",
        "uip",
        "usual interstitial pneumonia",
        "usual interstitial pneumonia uip",
        "honeycomb lung from idiopathic pulmonary fibrosis",
        "honeycomb change in idiopathic pulmonary fibrosis",
        "honeycombing from usual interstitial pneumonia",
        "pleural cobblestoning in idiopathic pulmonary fibrosis",
    },
    {
        "adenocarcinoma",
        "adenocarcinoma of the lung",
        "adenocarcinoma peripheral lung",
        "adenocarcinoma gland formation and mucin",
        "epithelial adenocarcinoma",
        "pulmonary adenocarcinoma",
    },
    {"red hepatization phase of pneumonia", "lobar pneumonia red hepatization"},
    {
        "emphysema",
        "emphysema alveolar wall destruction",
        "emphysema ct low attenuation bullae",
        "emphysema gross lung bullae",
        "vanishing lung syndrome",
    },
    {"centri acinar emphysema", "centriacinar emphysema"},
    {
        "pectus excavatum",
        "pectus excavatum haller index",
        "pectus excavatum treatment",
        "nuss bar for pectus excavatum",
    },
    {
        "asbestos related pleural plaques",
        "asbestos related calcified pleural plaque",
        "asbestos related pleural plaque",
        "asbestosis plaque",
        "bilateral calcified asbestos related pleural plaques",
        "parietal pleural plaques",
    },
    {"miliary tb", "miliary tuberculosis", "tb"},
    {"cavitary tb", "cavitary pulmonary tuberculosis", "tb"},
    {"pulmonary embolism", "pulmonary embolims", "acute pulmonary embolism"},
    {"sarcoidosis", "pulmonary sarcoidosis"},
    {"cpam type 3", "type 4 cpam versus pleuropulmonary blastoma"},
    {"organizing pneumonia", "cryptogenic organizing pneumonia"},
    {
        "congenital lobar emphysema",
        "congenital lobar emphysema lul improvement",
        "congenital lobar emphysema lul",
    },
    {"hyperinflation in copd", "severe copd"},
    {"neonatal respiratory distress syndrome", "neonatal respiratory distress syndrome hyaline membranes"},
    {"bronchogenic cyst", "mediastinal bronchogenic cyst", "mediastinal bronchogenic cyst in the carina"},
    {"cryptococcus neoformans", "encapsulated cryptococcus neoformans"},
    {"round pneumonia", "round pneumonia ct child"},
    {"grey hepatization phase of pneumonia", "gray hepatization of lobar pneumonia"},
    {
        "congenital diaphragmatic hernia",
        "left sided congenital diaphragmatic hernia",
        "congenital diaphragmatic hernia with scaphoid abdomen",
    },
    {"carcinoid", "carcinoid tumor", "pulmonary carcinoid tumor"},
    {
        "lobar pneumonia",
        "lobar pneumonia acute alveolar inflammation",
        "acute inflammation in lobar pneumonia",
        "red hepatization phase of pneumonia",
        "lobar pneumonia red hepatization",
    },
    {
        "coal worker s pneumoconiosis",
        "anthracotic pigment in lung in coal worker s pneumoconiosis",
    },
    {"lung mass", "left hilar lung mass"},
    {"pneumothorax", "bilateral pneumothorax", "bilateral pneumothoraces"},
    {"normal", "normal infant"},
    {"lateral pectus carinatum", "lower pectus carinatum"},
    # Any image showing simple/generic pleural fluid, regardless of stated
    # laterality or presumed etiology, cannot be told apart from another such
    # image on visual grounds alone -- these are never offered as distractors
    # against each other. Findings with a genuinely distinguishing visual
    # feature (empyema's loculation/air-fluid level, mesothelioma's pleural
    # rind, a named complicating process) stay in their own separate groups.
    {
        "pleural effusion",
        "right pleural effusion",
        "bilateral pleural effusion",
        "malignant pleural effusion",
        "malignant left pleural effusion",
        "pleural effusion and passive atelectasis",
        "pleural effusion from pulmonary embolism",
        "large right sided pulmonary effusion",
        "bilateral pulmonary effusion from chf",
        "left sided pleural effusion in malignant mesothelioma frontal",
    },
    {
        "ards",
        "acute respiratory distress syndrome",
        "ards hyaline membrane",
        "ards hyaline membranes",
        "hyaline membranes in ards",
        "ards intraalveolar hyaline membranes",
    },
    {"empyema", "empyema with air fluid level", "empyema with gas"},
    {"asbestos body", "asbestos bodies", "ferruginous body", "ferruginous bodies"},
    {"croup", "croup steeple sign", "steeple sign in croup"},
    {
        "endobronchial tumor",
        "endobronchial tumor golden s sign",
        "golden s sign",
        "golden s sign endobronchial tumor",
        "resorptive atelectasis from endobronchial tumor",
    },
    {"recurrent respiratory papillomatosis", "recurrent respiratory papillomatosis vf"},
    {"vocal cord", "vocal fold", "vocal cord lesions", "vocal fold vf lesions"},
    {
        "noncaseating granuloma",
        "noncaseating granulomas",
        "noncaseating granuloma in sarcoidosis",
    },
    {"lines of zahn", "lines of zahn in thrombus"},
    {"organized thromboembolism", "organizing thromboembolism"},
    {"streptococcus pneumoniae", "strep pneumoniae"},
    {"invasive aspergillosis", "invasive aspergillus"},
    {"aspergilloma", "fungal ball", "colonized cavity of aspergilloma"},
    {"right lung agenesis", "agenesis of the right lung"},
    {"kartagener syndrome", "kartagener syndrome bronchiectasis and situs invertis", "situs invertis"},
    {"cavitary tb", "cavitary pulmonary tuberculosis", "tb", "consolidative tb", "ghon complex"},
]

# Concepts that are a logical superset of other concepts (e.g. "Non-Small
# Cell Lung Cancer" is not a distinct histologic entity distinguishable from
# its own subtypes -- it names the category that squamous cell, large cell,
# adenocarcinoma, and bronchioloalveolar carcinoma all belong to) are cross-
# listed into each of those groups below, so they are excluded as a
# distractor for any of them, while remaining a legitimate distractor for a
# genuinely separate category such as small cell carcinoma.
NSCLC_SUPERSET_OF: list[str] = [
    "large cell lung carcinoma",
    "squamous cell carcinoma",
    "adenocarcinoma",
    "bronchioloalveolar carcinoma",
]
for _group in CONCEPT_SYNONYM_GROUPS:
    if _group & set(NSCLC_SUPERSET_OF):
        _group.add("non small cell lung cancer")


def _synonym_keys(concept_norm: str) -> set[str]:
    keys = {concept_norm}
    for group in CONCEPT_SYNONYM_GROUPS:
        if concept_norm in group:
            keys.add(next(iter(sorted(group))))
    return keys


# Keyword clusters of classically confusable / "trap answer" diagnoses that
# should be preferentially offered as distractors for each other, even when
# they fall in different auto-derived topics. Matching is a simple substring
# test against the padded, casefolded concept string (same style as
# topic_for). A concept may belong to more than one cluster.
CONFUSABLE_CLUSTERS: list[list[str]] = [
    [
        "small cell", "squamous cell carcinoma", "squamous cell lung carcinoma",
        "adenocarcinoma", "large cell carcinoma", "large cell lung carcinoma",
        "carcinoid", "non-small cell lung cancer", "bronchioloalveolar carcinoma",
    ],
    [
        "usual interstitial pneumonia", " uip", "nonspecific interstitial pneumonia",
        " nsip", "hypersensitivity pneumonitis", "idiopathic pulmonary fibrosis",
        " ipf", "organizing pneumonia", "honeycomb",
    ],
    [
        "tuberculosis", " tb ", " tb", "tb ", "sarcoidosis", "histoplasm",
        "coccidioid", "blastomyc", "aspergill", "cryptococc",
        "granulomatosis with polyangiitis", "paracoccidioid",
    ],
    [
        "pulmonary embol", "hampton", "saddle", "deep venous thrombosis",
        " dvt", "pulmonary hypertension", "plexiform", "pulmonary infarct",
        "thromboembol",
    ],
    ["blue bloater", "pink puffer", "chronic bronchitis", "emphysema", " copd"],
    ["pleural effusion", "empyema", "parapneumonic", "hemothorax", "pleural plaque"],
    [
        "lobar pneumonia", "bronchopneumonia", "atypical pneumonia", "mycoplasma",
        "aspiration pneumonia", "necrotizing pneumonia", "viral pneumonia",
        "community acquired pneumonia", "round pneumonia", "hepatization",
    ],
    ["epiglottitis", "croup", "peritonsillar", "laryngomalacia"],
    [
        "cpam", "pulmonary sequestration", "congenital lobar emphysema",
        "congenital diaphragmatic hernia", "bronchogenic cyst",
    ],
    ["neonatal respiratory distress syndrome", "bronchopulmonary dysplasia", "hyaline membrane"],
    ["goodpasture", "granulomatosis with polyangiitis", "alveolar hemorrhage"],
    ["asbestosis", "silicosis", "coal worker", "anthracotic", "asbestos"],
    ["bronchiectasis", "cystic fibrosis", "kartagener", "situs invert"],
]


def confusable_cluster_ids(concept_norm: str) -> set[int]:
    padded = f" {concept_norm} "
    return {idx for idx, keywords in enumerate(CONFUSABLE_CLUSTERS) if any(kw in padded for kw in keywords)}


def candidate_pool(current: dict, entries: list[dict]) -> list[str]:
    correct = current["concept"]
    correct_norm = re.sub(r"[^a-z0-9]+", " ", correct.casefold()).strip()
    correct_keys = _synonym_keys(correct_norm)
    correct_clusters = confusable_cluster_ids(correct_norm)

    def shares_cluster(entry: dict) -> bool:
        if not correct_clusters:
            return False
        entry_norm = re.sub(r"[^a-z0-9]+", " ", entry["concept"].casefold()).strip()
        return bool(confusable_cluster_ids(entry_norm) & correct_clusters)

    tiers = [
        [e for e in entries if shares_cluster(e)],
        [e for e in entries if e["topic"] == current["topic"] and e["family"] == current["family"]],
        [e for e in entries if e["family"] == current["family"]],
        [e for e in entries if e["topic"] == current["topic"]],
        entries,
    ]
    result: list[str] = []
    seen_norms: set[str] = set()
    seen_keys: set[str] = set(correct_keys)
    for tier in tiers:
        for entry in sorted(tier, key=lambda item: hashlib.sha256(f"{current['sha']}:{item['concept']}".encode()).hexdigest()):
            option = entry["concept"]
            option_norm = re.sub(r"[^a-z0-9]+", " ", option.casefold()).strip()
            if not option_norm or option_norm == correct_norm or option_norm in seen_norms:
                continue
            if correct_norm in option_norm or option_norm in correct_norm:
                continue
            option_keys = _synonym_keys(option_norm)
            if option_keys & seen_keys:
                continue
            result.append(option)
            seen_norms.add(option_norm)
            seen_keys |= option_keys
            if len(result) == 3:
                return result
    raise RuntimeError(f"Could not create distractors for {current['filename']}")


def reencode(source: Path, destination: Path, crop: tuple[float, float, float, float] | None = None, output_format: str = "PNG") -> dict:
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened)
        had_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
        if had_alpha:
            rgba = image.convert("RGBA")
            background = Image.new("RGBA", rgba.size, (248, 250, 252, 255))
            background.alpha_composite(rgba)
            image = background.convert("RGB")
        else:
            image = image.convert("RGB")
        input_size = [image.width, image.height]
        crop_box = None
        if crop:
            crop_box = [
                round(image.width * crop[0]),
                round(image.height * crop[1]),
                round(image.width * crop[2]),
                round(image.height * crop[3]),
            ]
            image = image.crop(tuple(crop_box))
        destination.parent.mkdir(parents=True, exist_ok=True)
        reuse = False
        if destination.is_file():
            try:
                with Image.open(destination) as existing:
                    reuse = existing.format == output_format and existing.size == image.size
            except OSError:
                reuse = False
        if not reuse:
            if output_format == "WEBP":
                # Quiz-display copy only: visually-lossless WebP keeps the in-app payload small.
                # The teaching-original tier below is always saved lossless PNG for full fidelity.
                image.save(destination, format="WEBP", quality=QUIZ_WEBP_QUALITY, method=6)
            else:
                # Lossless level-3 deflate keeps generation practical for hundreds of large medical
                # images; exhaustive PNG optimization changes only size, not pixels.
                image.save(destination, format="PNG", compress_level=3)
        return {
            "width": image.width,
            "height": image.height,
            "input_dimensions": input_size,
            "crop_box_pixels": crop_box,
            "crop_box_fraction": list(crop) if crop else None,
            "sha256": digest_file(destination),
        }


def main() -> None:
    for collection in COLLECTIONS:
        if not collection["path"].is_dir():
            raise SystemExit(f"Missing source directory: {collection['path']}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for collection in COLLECTIONS:
        files = sorted(
            (path for path in collection["path"].iterdir() if path.suffix.casefold() in IMAGE_EXTENSIONS),
            key=lambda path: path.name.casefold(),
        )
        if not files:
            raise SystemExit(f"No supported image files found in {collection['path']}")
        for path in files:
            sha = digest_file(path)
            with Image.open(path) as opened:
                image_format = opened.format or path.suffix.lstrip(".").upper()
                image = ImageOps.exif_transpose(opened)
                width, height = image.size
                perceptual = dhash(image)
                has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
            modality = modality_for(path.name, collection["key"])
            concept = concept_for(path.name, collection["key"])
            topic = topic_for(concept)
            if collection["key"] == "rename":
                base = re.sub(r"\s+(?:copy|[234])$", "", path.stem, flags=re.I)
                group_key = f"{clean_text(base)}:{modality_family(modality)}"
                review_reason = REVIEW_ONLY_RENAME.get(path.name, "")
            else:
                group_key = f"{concept}:{modality_family(modality)}"
                review_reason = REVIEW_ONLY_ADD.get(path.name, "")
            status = "DUPLICATE" if collection["key"] == "third_party" and path.name in DUPLICATE_OF else ("NEEDS_REVIEW" if review_reason else "USABLE")
            entries.append({
                "path": path,
                "filename": path.name,
                "sha": sha,
                "width": width,
                "height": height,
                "aspect_ratio": width / height,
                "perceptual_hash": perceptual,
                "has_alpha": has_alpha,
                "file_format": image_format,
                "modality": modality,
                "family": modality_family(modality),
                "concept": concept,
                "topic": topic,
                "collection_key": collection["key"],
                "collection_label": collection["label"],
                "collection_document": collection["document"],
                "collection_rule": collection["rule"],
                "review_reason": review_reason,
                "asset_id": stable_id("asset", sha),
                "source_id": stable_id("src", sha),
                "source_group_id": stable_id("sg", group_key.casefold()),
                "variant_id": stable_id("var", f"{sha}:quiz-v1"),
                "question_id": stable_id("q", f"{sha}:{concept}:identification"),
                "status": status,
            })

    groups: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        groups[entry["source_group_id"]].append(entry)
    entry_by_collection_filename = {(entry["collection_key"], entry["filename"]): entry for entry in entries}

    records: list[dict] = []
    asset_map: dict[str, dict] = {}
    questions: list[dict] = []
    review_items: list[dict] = []

    for entry in entries:
        source = entry["path"]
        crop = (CROPS if entry["collection_key"] == "rename" else ADD_CROPS).get(entry["filename"])
        original_name = f"original_{entry['sha'][:16]}.png"
        quiz_key = hashlib.sha256(f"{entry['sha']}:quiz:{crop}".encode()).hexdigest()[:16]
        quiz_name = f"quiz_{quiz_key}.webp"
        original_path = ASSET_DIR / original_name
        quiz_path = ASSET_DIR / quiz_name
        original_meta = reencode(source, original_path)
        quiz_meta = reencode(source, quiz_path, crop, output_format="WEBP")
        original_relative = original_path.relative_to(PROJECT).as_posix()
        quiz_relative = quiz_path.relative_to(PROJECT).as_posix()
        transformations = ["metadata_strip", "lossless_png_reencode"]
        if entry["has_alpha"]:
            transformations.append("neutral_background_composite")
        if crop:
            transformations.append("answer_title_border_crop")

        composite_files = COMPOSITES if entry["collection_key"] == "rename" else ADD_COMPOSITES
        joint = entry["modality"] in {"X-ray and CT", "X-ray and pathology", "X-ray, CT, and pathology", "Gross pathology and histology"} or entry["filename"] in composite_files
        stem, visual_target = stem_for(entry["modality"], joint, entry["concept"])
        clue = feature_for(entry["concept"], entry["modality"])
        case_context = CASE_CONTEXT.get(entry["filename"], "")
        if case_context:
            stem = CASE_STEM.get(entry["filename"], stem)
            clue = CASE_CLUE.get(entry["filename"], clue)
        group_members = groups[entry["source_group_id"]]
        duplicate_target = None
        if entry["collection_key"] == "third_party" and entry["filename"] in DUPLICATE_OF:
            duplicate_target = entry_by_collection_filename[("rename", DUPLICATE_OF[entry["filename"]])]
        related_ids = [member["source_id"] for member in group_members if member["source_id"] != entry["source_id"]]
        if duplicate_target and duplicate_target["source_id"] not in related_ids:
            related_ids.append(duplicate_target["source_id"])
        manual_reason = entry["review_reason"]
        if duplicate_target:
            manual_reason = f"Perceptual duplicate of {DUPLICATE_OF[entry['filename']]} in the {duplicate_target['collection_label']} collection."
        record = {
            "asset_id": entry["asset_id"],
            "source_group_id": entry["source_group_id"],
            "source_id": entry["source_id"],
            "original_relative_path": entry["filename"],
            "original_absolute_path": str(source),
            "source_sha256": entry["sha"],
            "perceptual_hash": entry["perceptual_hash"],
            "duplicate_relationships": related_ids,
            "canonical_representative": duplicate_target["source_id"] if duplicate_target else max(group_members, key=lambda item: item["width"] * item["height"])["source_id"],
            "pixel_width": entry["width"],
            "pixel_height": entry["height"],
            "aspect_ratio": entry["aspect_ratio"],
            "file_format": entry["file_format"],
            "quality_warnings": (["low_resolution_native_display_only"] if min(entry["width"], entry["height"]) < 500 else []),
            "modality": entry["modality"],
            "organ_system": "Pulmonary",
            "category": entry["topic"],
            "tested_condition_structure_finding": entry["concept"],
            "canonical_correct_answer": entry["concept"],
            "accepted_synonyms": [],
            "ground_truth_basis": "user-curated descriptive filename plus full-set visual review",
            "ground_truth_confidence": "high" if entry["status"] == "USABLE" else "low",
            "answer_leakage_assessment": "controlled by a recorded border crop" if crop else "no unmasked exact answer observed in full-set review",
            "required_preserved_regions": ["complete diagnostic field", "visible arrows and orientation markers"],
            "usable_transformations": transformations,
            "candidate_question_types": ["Identification"],
            "manual_review_reason": manual_reason,
            "source_attribution_visible_in_original": "unknown",
            "source_origin": "third_party",
            "source_collection": entry["collection_label"],
            "source_collection_key": entry["collection_key"],
            "collection_rule": entry["collection_rule"],
            "rights_status": "unknown; local study use only",
            "immutable_source_hash": entry["sha"],
            "status": entry["status"],
            "visual_target": visual_target,
            "key_visual_findings": clue,
            "panel_handling": "retained_composite" if joint else "single_complete_image",
            "question_type_matrix": {
                "Identification": {
                    "supported": "YES" if entry["status"] == "USABLE" else ("DUPLICATE" if entry["status"] == "DUPLICATE" else "REVIEW"),
                    "visual_target": visual_target,
                    "required_variant": entry["variant_id"],
                    "full_image_required": crop is None,
                    "preserve": ["diagnostic pixels", "arrows", "orientation markers"],
                    "confidence": "high" if entry["status"] == "USABLE" else "low",
                    "reason_unsupported": manual_reason,
                }
            },
            "variants": [{
                "variant_id": entry["variant_id"],
                "quiz_asset": quiz_relative,
                "teaching_original_asset": original_relative,
                "input_sha256": entry["sha"],
                "input_dimensions": [entry["width"], entry["height"]],
                "coordinate_basis": "immutable original",
                "crop_box_fraction": list(crop) if crop else None,
                "crop_box_pixels": quiz_meta["crop_box_pixels"],
                "output_dimensions": [quiz_meta["width"], quiz_meta["height"]],
                "transformations": transformations,
            }],
        }
        records.append(record)
        asset_map[entry["variant_id"]] = {
            "source_id": entry["source_id"],
            "source_group_id": entry["source_group_id"],
            "quiz": {"path": quiz_relative, "sha256": quiz_meta["sha256"], "width": quiz_meta["width"], "height": quiz_meta["height"], "transformations": transformations},
            "original": {"path": original_relative, "sha256": original_meta["sha256"], "width": original_meta["width"], "height": original_meta["height"]},
        }

        if entry["status"] == "NEEDS_REVIEW":
            review_items.append({
                "source_id": entry["source_id"],
                "source_group_id": entry["source_group_id"],
                "preview_asset": original_relative,
                "proposed_answer": entry["concept"],
                "modality": entry["modality"],
                "evidence": "User-supplied filename and visual review were insufficient for a unique scored key.",
                "source_collection_key": entry["collection_key"],
                "source_collection": entry["collection_label"],
                "uncertainty_reason": entry["review_reason"],
                "answer_leakage_risk": "high" if "label" in entry["review_reason"].casefold() else "low",
                "project_status": "NEEDS_REVIEW",
            })
            continue
        if entry["status"] != "USABLE":
            continue

        distractors = candidate_pool(entry, [candidate for candidate in entries if candidate["status"] == "USABLE"])
        correct_index = int(entry["sha"][:2], 16) % 4
        options = distractors[:]
        options.insert(correct_index, entry["concept"])
        rationales = []
        for index, option in enumerate(options):
            if index == correct_index:
                rationales.append(f"Correct: The displayed image shows {clue}, supporting {entry['concept']}.")
            else:
                expected = feature_for(option, entry["modality"])
                rationales.append(f"{option} would instead show {expected}; the displayed image shows {clue}.")
        questions.append({
            "question_id": entry["question_id"],
            "source_group_id": entry["source_group_id"],
            "source_id": entry["source_id"],
            "variant_id": entry["variant_id"],
            "question_type": "Identification",
            "tested_concept": entry["concept"],
            "stem": stem,
            "case_context": case_context,
            "visual_target": visual_target,
            "panel_handling": "retained_composite" if joint else "single_complete_image",
            "joint_images": joint,
            "options": options,
            "correct_index": correct_index,
            "accepted_terminology": [],
            "explanation": f"The decisive visible finding is {clue}. This pattern supports {entry['concept']}.",
            "visual_clues": [clue],
            "choice_rationales": rationales,
            "ground_truth_confidence": "high",
            "ground_truth_evidence": "User-curated descriptive filename confirmed against the displayed morphology during full-set visual review.",
            "category": entry["topic"],
            "modality": entry["modality"],
            "organ_system": "Pulmonary",
            "topic_cluster": entry["topic"].casefold().replace(" ", "-"),
            "source_origin": "third_party",
            "source_collection": entry["collection_label"],
            "source_collection_key": entry["collection_key"],
            "quiz_asset": quiz_relative,
            "original_asset": original_relative,
            "post_answer_source": {
                "original_filename": entry["filename"],
                "source_document": entry["collection_document"],
                "source_collection": entry["collection_label"],
                "source_collection_key": entry["collection_key"],
                "source_page_or_slide": "",
                "source_id": entry["source_id"],
                "rights_status": "unknown; local study use only",
            },
            "review_status": "VERIFIED",
            "quality_review_batch": None,
        })

    manifest = {
        "schema_version": 2,
        "generated_at": NOW,
        "builder": "build-medical-picture-quiz / multi-collection flat-image builder",
        "source_directories": [{"key": collection["key"], "label": collection["label"], "path": str(collection["path"])} for collection in COLLECTIONS],
        "source_library_read_only": True,
        "collection_provenance_rule": "All Desktop/Rename and Desktop/Add images are third_party and restricted to local study use.",
        "record_count": len(records),
        "records": records,
    }
    bank = {
        "schema_version": 2,
        "bank_id": stable_id("bank", "rename-add:" + "".join(entry["sha"] for entry in entries)),
        "generated_at": NOW,
        "mode": "pulmonary_visual_identification",
        "question_count": len(questions),
        "quality_review": {"batch_id": None, "reviewed_at": None, "count": 0, "summary": {}, "resolved_flags": []},
        "questions": questions,
    }
    review_queue = {
        "schema_version": 2,
        "generated_at": NOW,
        "count": len(review_items),
        "items": review_items,
    }

    referenced_assets = {
        Path(mapped[side]["path"]).name
        for mapped in asset_map.values()
        for side in ("quiz", "original")
    }
    for path in list(ASSET_DIR.glob("*.png")) + list(ASSET_DIR.glob("*.webp")):
        if path.name not in referenced_assets:
            path.unlink()

    payloads = {
        "source-manifest.json": manifest,
        "asset-map.json": asset_map,
        "question-bank.json": bank,
        "review-queue.json": review_queue,
    }
    for filename, payload in payloads.items():
        serialized = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
        (DATA_DIR / filename).write_text(serialized, encoding="utf-8")
        (PROJECT / filename).write_text(serialized, encoding="utf-8")

    modality_counts = Counter(entry["modality"] for entry in entries)
    topic_counts = Counter(question["category"] for question in questions)
    low_resolution = [entry for entry in entries if min(entry["width"], entry["height"]) < 500]
    duplicate_groups = {key: members for key, members in groups.items() if len(members) > 1}
    status_counts = Counter(entry["status"] for entry in entries)
    collection_counts = Counter(entry["collection_label"] for entry in entries)
    scored_collection_counts = Counter(question["source_collection"] for question in questions)
    audit = [
        "# Pulmonary multi-collection preflight audit",
        "",
        f"Generated: {NOW}",
        "",
        *[f"- Source: `{collection['path']}` (read-only)" for collection in COLLECTIONS],
        f"- Physical image files: {len(entries)}",
        f"- Decodable files: {len(entries)}",
        f"- Scored questions: {len(questions)}",
        f"- Review-only sources: {status_counts['NEEDS_REVIEW']}",
        f"- Perceptual duplicates withheld: {status_counts['DUPLICATE']}",
        f"- Source groups with multiple named variants: {len(duplicate_groups)}",
        f"- Low-resolution files (one dimension below 500 px): {len(low_resolution)}",
        f"- Quiz-safe border crops: {len(CROPS) + len(ADD_CROPS)}",
        "- Exact byte-identical duplicate groups: 0",
        "- Provenance: all records are `third_party`; rights are unknown and the build is restricted to local study use.",
        "",
        "## Collections",
        "",
        *[f"- {label}: {collection_counts[label]} sources, {scored_collection_counts[label]} scored" for label in sorted(collection_counts)],
        "",
        "## Modalities",
        "",
        *[f"- {name}: {count}" for name, count in sorted(modality_counts.items())],
        "",
        "## Scored topic coverage",
        "",
        *[f"- {name}: {count}" for name, count in sorted(topic_counts.items())],
        "",
        "## Review-only decisions",
        "",
        *[f"- `{item['proposed_answer']}` ({item['source_id']}): {item['uncertainty_reason']}" for item in review_items],
        "",
        "## Transformation policy",
        "",
        f"All browser assets were re-encoded with metadata stripped. Transparency was composited onto a neutral background. The teaching-original tier is always losslessly re-encoded as PNG. The quiz-display tier is re-encoded as visually-lossless WebP (quality {QUIZ_WEBP_QUALITY}) to keep in-app payload size small; no diagnostic pixel content was cropped, stretched, upscaled, or generatively reconstructed in either tier. {len(CROPS) + len(ADD_CROPS)} answer-revealing captions or titles in non-diagnostic border space were removed with recorded source-relative crop coordinates.",
        "",
        "## Ground-truth decision",
        "",
        "The collection was descriptively renamed by the user before import. Keys were accepted only where the visible morphology was compatible during the complete contact-sheet review. Sources with insufficient, ambiguous, non-pulmonary, or answer-leaking evidence were withheld in the review queue.",
    ]
    (REPORT_DIR / "preflight-audit.md").write_text("\n".join(audit) + "\n", encoding="utf-8")
    if (PROJECT.parent / "rename-audit" / "source-audit.json").exists():
        shutil.copy2(PROJECT.parent / "rename-audit" / "source-audit.json", REPORT_DIR / "source-audit-rename.json")
    if (PROJECT.parent / "add-audit" / "source-audit.json").exists():
        shutil.copy2(PROJECT.parent / "add-audit" / "source-audit.json", REPORT_DIR / "source-audit-add.json")

    print(json.dumps({
        "result": "GENERATED",
        "source_files": len(entries),
        "scored_questions": len(questions),
        "review_only": len(review_items),
        "duplicates_withheld": status_counts["DUPLICATE"],
        "assets": len(list(ASSET_DIR.glob("*.png"))) + len(list(ASSET_DIR.glob("*.webp"))),
    }, indent=2))


if __name__ == "__main__":
    main()
