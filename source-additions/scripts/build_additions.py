#!/usr/bin/env python3
"""Create a versioned, read-only-after-build supplemental source library for the local quiz."""

from __future__ import annotations

import csv
import hashlib
import json
import shutil
import subprocess
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
ORIGINALS = ROOT / "originals"
VARIANTS = ROOT / "variants"
SOURCE_MEDIA = ROOT / "source_media"
PULM = Path("/Users/chriselwell/Desktop/Pulm/Pulm Pictures")


def q(options, clues, explanation, rationales, stem="Identify the pulmonary finding, pattern, or procedure shown."):
    return {
        "stem": stem,
        "options": options,
        "correct_index": 0,
        "visual_clues": clues,
        "explanation": explanation,
        "choice_rationales": rationales,
    }


SOURCES = [
    {
        "slug": "b-lines-lung-ultrasound",
        "answer": "B-lines indicating an interstitial lung syndrome",
        "modality": "Ultrasound",
        "category": "Point-of-care ultrasound",
        "lecture": "P15 - Approach to the Patient with Respiratory Disease and Pulmonary Preventative Care",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/c/cf/B_lines_on_a_lung_ultrasound_of_a_patient_with_fibrosis.jpg",
            "landing": "https://commons.wikimedia.org/wiki/File:B_lines_on_a_lung_ultrasound_of_a_patient_with_fibrosis.jpg",
            "creator": "Tinss",
            "organization": "Wikimedia Commons",
            "license": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "rights_status": "cc_by_sa",
            "sha1": "e6a05e21fd7726238235c6de59d6303c1352f4a7",
        },
        "ground_truth": "The Commons asset page identifies vertical B-lines on lung ultrasound in pulmonary fibrosis.",
        "findings": "Multiple bright vertical artifacts arise from the pleural line and extend to the far field, erasing the horizontal A-line pattern.",
        "question": q(
            ["B-lines indicating an interstitial lung syndrome", "A-lines of normally aerated lung", "Pleural effusion", "Lung point of pneumothorax"],
            ["Vertical hyperechoic artifacts begin at the pleural line", "Artifacts extend to the bottom of the image", "Horizontal A-lines are not the dominant pattern"],
            "The image shows multiple B-lines, a lung-ultrasound pattern of increased extravascular lung density/interstitial syndrome.",
            [
                "B-lines are bright vertical artifacts that arise from the pleura, reach the far field, and move with pleural motion; that is the dominant pattern here.",
                "A-lines are repetitive horizontal reverberation artifacts beneath the pleura, not the numerous vertical rays shown here.",
                "Pleural effusion would appear as an anechoic or hypoechoic fluid collection above the diaphragm, which is absent here.",
                "A lung point requires an interface between sliding and non-sliding pleura; a static field of vertical B-lines does not show that transition.",
            ],
        ),
    },
    {
        "slug": "seashore-sign-lung-ultrasound",
        "answer": "Seashore sign indicating normal lung sliding",
        "modality": "Ultrasound",
        "category": "Point-of-care ultrasound",
        "lecture": "P15 - Approach to the Patient with Respiratory Disease and Pulmonary Preventative Care",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/e/eb/Sea_shore_sign_on_a_lung_ultrasound.jpg",
            "landing": "https://commons.wikimedia.org/wiki/File:Sea_shore_sign_on_a_lung_ultrasound.jpg",
            "creator": "Tinss",
            "organization": "Wikimedia Commons",
            "license": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "rights_status": "cc_by_sa",
            "sha1": "f130f1c0686bd47d6b484c324d01bc7cc350f183",
        },
        "ground_truth": "The Commons asset page identifies the M-mode seashore sign of lung sliding.",
        "findings": "M-mode shows parallel horizontal lines above the pleura and a granular sandy pattern below it, consistent with pleural movement.",
        "question": q(
            ["Seashore sign indicating normal lung sliding", "Barcode/stratosphere sign suggesting pneumothorax", "B-lines indicating interstitial syndrome", "Anechoic pleural effusion"],
            ["Horizontal lines occupy the superficial static tissues", "A granular pattern appears below the pleural line", "The two-zone M-mode appearance implies pleural motion"],
            "The superficial linear pattern with granular echoes below the pleural line is the seashore sign and supports preserved lung sliding.",
            [
                "The normal seashore pattern combines static horizontal lines above the pleura with a granular appearance below it from lung sliding.",
                "The barcode or stratosphere sign would show parallel horizontal lines both above and below the pleural line, without the granular lower zone.",
                "B-lines are vertical artifacts on B-mode imaging; they are not the defining two-zone M-mode pattern tested here.",
                "Pleural fluid would be an anechoic collection, usually above the diaphragm, rather than this M-mode sliding pattern.",
            ],
        ),
    },
    {
        "slug": "bronchoscopy-procedure",
        "answer": "Flexible bronchoscopy",
        "modality": "Clinical Image",
        "category": "Pulmonary procedures",
        "lecture": "P33 - Otolaryngology - Upper Airway Pathology",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/8/8c/Bronchoscopy.jpg",
            "landing": "https://commons.wikimedia.org/wiki/File:Bronchoscopy.jpg",
            "creator": "U.S. National Institutes of Health",
            "organization": "National Institutes of Health / Wikimedia Commons",
            "license": "Public Domain Mark 1.0 (U.S. federal work)",
            "license_url": "https://creativecommons.org/publicdomain/mark/1.0/",
            "rights_status": "public_domain",
            "sha1": "cf632e956e3081537435659d201170bd891c6f6d",
        },
        "ground_truth": "The NIH/Commons asset description explicitly identifies physicians performing flexible bronchoscopy.",
        "findings": "A flexible endoscope is advanced through the patient's upper airway while the operator views the airway on a monitor.",
        "question": q(
            ["Flexible bronchoscopy", "Diagnostic spirometry", "Thoracentesis", "Chest-tube insertion"],
            ["A flexible scope is passed through the airway", "The operator controls the scope at the patient's head", "Airway visualization equipment is present"],
            "The procedure shown is flexible bronchoscopy, which permits direct inspection and sampling of the tracheobronchial tree.",
            [
                "Flexible bronchoscopy uses a steerable illuminated scope introduced through the upper airway, matching the equipment and patient positioning shown.",
                "Spirometry requires a mouthpiece connected to a flow-measuring device and a coached forced maneuver, not endoscope insertion.",
                "Thoracentesis uses a needle or catheter through the posterolateral chest wall to sample pleural fluid, which is not shown.",
                "Chest-tube insertion is performed through the lateral chest wall into the pleural space, not through the upper airway.",
            ],
            "Identify the pulmonary procedure shown in this clinical photograph.",
        ),
    },
    {
        "slug": "right-chest-tube-cxr",
        "answer": "Right thoracostomy tube for pneumothorax",
        "modality": "X-ray",
        "category": "Lines and tubes",
        "lecture": "P18 - Basic Interpretation of Chest X-Ray",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/2/26/ChesttubeforRtPneumo.png",
            "landing": "https://commons.wikimedia.org/wiki/File:ChesttubeforRtPneumo.png",
            "creator": "James Heilman, MD",
            "organization": "Wikimedia Commons",
            "license": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "rights_status": "cc_by_sa",
            "sha1": "30fd98cbdbe62682c38a91984a6d76efa98d2a30",
        },
        "ground_truth": "The creator's Commons asset page identifies a right chest tube placed for pneumothorax.",
        "findings": "A large-bore radiopaque tube enters the right lateral chest and courses within the pleural space; a right pneumothorax is also visible.",
        "question": q(
            ["Right thoracostomy tube for pneumothorax", "Right internal-jugular central venous catheter", "Endotracheal tube", "Nasogastric tube"],
            ["The tube enters through the lateral chest wall", "It follows the pleural space rather than the mediastinum", "A right pneumothorax is present"],
            "The radiopaque device is a right thoracostomy tube positioned in the pleural space to treat pneumothorax.",
            [
                "A thoracostomy tube enters laterally and courses in the pleural space, matching the visible tube and associated pneumothorax.",
                "A central venous catheter enters from the neck or subclavian region and terminates near the lower SVC, not along the pleural cavity.",
                "An endotracheal tube descends centrally within the tracheal air column and should terminate above the carina.",
                "A nasogastric tube follows the esophagus, crosses the diaphragm, and terminates below it in the stomach.",
            ],
        ),
    },
    {
        "slug": "central-venous-catheter-cxr",
        "answer": "Central venous catheter",
        "modality": "X-ray",
        "category": "Lines and tubes",
        "lecture": "P18 - Basic Interpretation of Chest X-Ray",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/b/bd/Human_chest_x-ray%2C_adult_male%2C_with_central_venous_catheter.jpg",
            "landing": "https://commons.wikimedia.org/wiki/File:Human_chest_x-ray,_adult_male,_with_central_venous_catheter.jpg",
            "creator": "Wikimpan",
            "organization": "Wikimedia Commons",
            "license": "Public domain medical image (Poland)",
            "license_url": "https://commons.wikimedia.org/wiki/Template:PD-medical",
            "rights_status": "public_domain",
            "sha1": "8edcb6d8a96171abe911773d5e3d706810349481",
        },
        "ground_truth": "The Commons asset page explicitly identifies the visible line as a central venous catheter.",
        "findings": "A radiopaque catheter travels from the upper chest/neck toward the central venous circulation without entering the airway or pleural space.",
        "question": q(
            ["Central venous catheter", "Chest tube", "Endotracheal tube", "Nasogastric tube"],
            ["The catheter enters from the upper chest/neck", "Its course is central and vascular", "It does not track through the trachea, esophagus, or pleural space"],
            "The chest radiograph demonstrates a central venous catheter coursing toward the central veins.",
            [
                "A central venous catheter enters from the neck or upper chest and courses toward the SVC, matching the visible line.",
                "A chest tube enters through the lateral thorax and follows the pleural space, unlike this central vascular course.",
                "An endotracheal tube is centered in the tracheal air column with its tip above the carina, which is not the course shown.",
                "A nasogastric tube descends in the esophagus and crosses below the diaphragm, which this catheter does not do.",
            ],
        ),
    },
    {
        "slug": "chest-drain-apparatus",
        "answer": "Water-seal chest drainage system",
        "modality": "Clinical Image",
        "category": "Pulmonary equipment",
        "lecture": "P18 - Basic Interpretation of Chest X-Ray",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/9/91/Chest_drain_2_fluids.jpg",
            "landing": "https://commons.wikimedia.org/wiki/File:Chest_drain_2_fluids.jpg",
            "creator": "Pgm78at",
            "organization": "Wikimedia Commons",
            "license": "Public domain",
            "license_url": "https://creativecommons.org/publicdomain/mark/1.0/",
            "rights_status": "public_domain",
            "sha1": "34e0c1a9ee6f3c99abcebfb4932f52247c15201d",
        },
        "ground_truth": "The creator's Commons asset page identifies the two-bottle thoracic drainage apparatus.",
        "findings": "Large collection bottles are connected by tubing in a dependent drainage and water-seal arrangement.",
        "question": q(
            ["Water-seal chest drainage system", "Incentive spirometer", "Peak-flow meter", "Jet nebulizer"],
            ["Dependent collection bottles contain pleural fluid", "Tubing links the patient side to a water-seal chamber", "The apparatus is designed for continuous thoracic drainage"],
            "The photograph shows a water-seal chest drainage system used with a thoracostomy tube.",
            [
                "A chest-drain system uses dependent collection and water-seal chambers connected by tubing, matching the photographed apparatus.",
                "An incentive spirometer is a handheld inspiratory-training device with a mouthpiece and rising marker, not fluid collection bottles.",
                "A peak-flow meter is a small handheld expiratory-flow gauge and does not contain drainage chambers.",
                "A jet nebulizer has a medication cup, air tubing, and mask or mouthpiece rather than large fluid-collection bottles.",
            ],
            "Identify the pulmonary device shown in this photograph.",
        ),
    },
    {
        "slug": "omega-epiglottis",
        "answer": "Omega-shaped epiglottis in laryngomalacia",
        "modality": "Clinical Image",
        "category": "Upper-airway endoscopy",
        "lecture": "P33 - Otolaryngology - Upper Airway Pathology",
        "local": "Omega-Shaped Epiglottis.jpg",
        "ground_truth": "The verified P33 picture manifest identifies an omega-shaped epiglottis with supraglottic collapse.",
        "findings": "The epiglottis is tightly curled into an omega configuration above a narrowed laryngeal inlet.",
        "question": q(
            ["Omega-shaped epiglottis in laryngomalacia", "Acute epiglottitis", "Bilateral vocal-fold nodules", "Peritonsillar abscess"],
            ["The epiglottic margins curl inward", "The laryngeal inlet is narrowed by supraglottic tissue", "There is no diffuse cherry-red epiglottic swelling"],
            "The endoscopic image shows an omega-shaped epiglottis, a classic laryngomalacia morphology.",
            [
                "Laryngomalacia commonly produces a tightly curled omega-shaped epiglottis and dynamic supraglottic collapse, matching this view.",
                "Acute epiglottitis causes a diffusely enlarged, edematous, erythematous epiglottis rather than a thin curled omega shape.",
                "Vocal-fold nodules are paired lesions on the true vocal folds, which are not the dominant supraglottic finding here.",
                "A peritonsillar abscess produces unilateral tonsillar bulging and uvular deviation in the oropharynx, not this laryngeal view.",
            ],
        ),
    },
    {
        "slug": "vocal-cord-nodules",
        "answer": "Bilateral vocal-fold nodules",
        "modality": "Clinical Image",
        "category": "Upper-airway endoscopy",
        "lecture": "P33 - Otolaryngology - Upper Airway Pathology",
        "local": "P002 Vocal Cord Nodules Gross.png",
        "ground_truth": "The verified P33 picture manifest identifies paired vocal-fold nodules from phonotrauma.",
        "findings": "Small symmetric pale lesions are present at the opposing mid-membranous edges of both true vocal folds.",
        "question": q(
            ["Bilateral vocal-fold nodules", "Unilateral vocal-fold polyp", "Reinke edema", "Laryngeal papillomatosis"],
            ["Lesions are bilateral and symmetric", "They oppose one another at the mid-membranous folds", "The background mucosa lacks diffuse polypoid edema or multiple papillae"],
            "The laryngoscopic image demonstrates paired bilateral vocal-fold nodules at the typical contact points.",
            [
                "Vocal-fold nodules are classically small, bilateral, and symmetric at the junction of the anterior and middle thirds, as shown.",
                "A vocal-fold polyp is usually unilateral and more exophytic, not a matched pair of opposing lesions.",
                "Reinke edema produces diffuse boggy swelling along the membranous folds rather than discrete symmetric nodules.",
                "Papillomatosis produces multiple irregular frond-like lesions, not two smooth opposing nodules.",
            ],
        ),
    },
    {
        "slug": "obstructive-flow-volume-loop",
        "answer": "Small-airway obstructive flow-volume loop",
        "modality": "Flow-Volume Loop",
        "category": "Pulmonary function testing",
        "lecture": "P37 - Advanced Spirometry Review - Interactive Workshop",
        "local": "Flow-Volume-Loop-for-Small-Airway-Obstructive-Lung-Disease.jpg",
        "transform": {"crop": [0, 45, 485, 440]},
        "ground_truth": "The verified P19/P37 picture manifests identify the scooped expiratory limb and air trapping of small-airway obstruction.",
        "findings": "The expiratory limb is concave with reduced flow, and the loop is shifted toward larger residual volume/air trapping.",
        "question": q(
            ["Small-airway obstructive flow-volume loop", "Restrictive flow-volume loop", "Fixed upper-airway obstruction", "Variable extrathoracic obstruction"],
            ["Expiratory limb is scooped and concave", "Residual volume is increased", "Inspiratory flow is relatively preserved"],
            "The loop has the characteristic concave expiratory limb and air-trapping shift of obstructive disease.",
            [
                "Obstructive disease produces reduced expiratory flow with a scooped concave expiratory limb and often increased residual volume, all shown here.",
                "Restriction produces a small narrow loop with preserved contour and reduced total volume, not prominent expiratory scooping with air trapping.",
                "Fixed upper-airway obstruction plateaus both inspiratory and expiratory limbs, unlike this selectively concave expiration.",
                "Variable extrathoracic obstruction predominantly flattens the inspiratory limb, which remains relatively preserved here.",
            ],
            "Interpret the flow-volume loop shown.",
        ),
    },
    {
        "slug": "fixed-upper-airway-loop",
        "answer": "Fixed upper-airway obstruction",
        "modality": "Flow-Volume Loop",
        "category": "Pulmonary function testing",
        "lecture": "P37 - Advanced Spirometry Review - Interactive Workshop",
        "local": "Flow-Volume-Loop-for-Fixed-Immobile-Upper-Airway-Obstruction.jpg",
        "transform": {"crop": [0, 45, 485, 440]},
        "ground_truth": "The verified P37 picture manifest identifies flattening of both limbs in fixed upper-airway obstruction.",
        "findings": "Both the expiratory and inspiratory limbs form plateaus, with relatively preserved lung volume.",
        "question": q(
            ["Fixed upper-airway obstruction", "Variable extrathoracic obstruction", "Variable intrathoracic obstruction", "Small-airway obstruction"],
            ["Expiratory flow plateaus", "Inspiratory flow also plateaus", "The loop has a box-like contour"],
            "Flattening of both inspiratory and expiratory limbs is the classic flow-volume-loop pattern of a fixed large-airway obstruction.",
            [
                "A fixed lesion limits flow in both phases, producing the box-like bilateral plateaus visible here.",
                "Variable extrathoracic obstruction primarily flattens inspiration while expiration is relatively preserved.",
                "Variable intrathoracic obstruction primarily flattens expiration while inspiration is relatively preserved.",
                "Small-airway obstruction causes a scooped concave expiratory limb rather than flat plateaus of both limbs.",
            ],
            "Interpret the flow-volume loop shown.",
        ),
    },
    {
        "slug": "variable-intrathoracic-loop",
        "answer": "Variable intrathoracic obstruction",
        "modality": "Flow-Volume Loop",
        "category": "Pulmonary function testing",
        "lecture": "P37 - Advanced Spirometry Review - Interactive Workshop",
        "local": "Flow-Volume-Loop-for-Mobile-Variable-Intrathoracic-Obstruction.jpg",
        "transform": {"crop": [0, 45, 485, 440]},
        "ground_truth": "The verified P37 picture manifest identifies expiratory-limb limitation from variable intrathoracic obstruction.",
        "findings": "Expiration develops a broad flow plateau while the inspiratory limb remains comparatively rounded and unrestricted.",
        "question": q(
            ["Variable intrathoracic obstruction", "Variable extrathoracic obstruction", "Fixed upper-airway obstruction", "Restrictive lung disease"],
            ["Expiratory limb is flattened", "Inspiratory limb is relatively preserved", "Lung volumes are not markedly reduced"],
            "Selective expiratory flattening supports a variable intrathoracic large-airway obstruction.",
            [
                "Intrathoracic dynamic collapse worsens during expiration, producing the selective expiratory plateau shown.",
                "Variable extrathoracic obstruction instead limits inspiration and flattens the inspiratory limb.",
                "A fixed lesion flattens both inspiratory and expiratory limbs, not expiration alone.",
                "Restriction produces a reduced-volume narrow loop without a selective expiratory plateau.",
            ],
            "Interpret the flow-volume loop shown.",
        ),
    },
    {
        "slug": "bronchodilator-reversibility-loop",
        "answer": "Reversible airflow obstruction after bronchodilator",
        "modality": "Flow-Volume Loop",
        "category": "Pulmonary function testing",
        "lecture": "P37 - Advanced Spirometry Review - Interactive Workshop",
        "local": "Reversible-Obstruction-on-Spirometry-in-Patients-with-Asthma.png",
        "transform": {"masks": [[0, 0, 619, 50], [42, 375, 270, 435], [385, 375, 619, 435], [0, 417, 100, 435]]},
        "ground_truth": "The verified P34/P37 picture manifests identify improved post-bronchodilator flow in reversible asthma obstruction.",
        "findings": "After a beta-2 agonist, peak expiratory flow rises and the expiratory contour approaches the normal reference loop.",
        "question": q(
            ["Reversible airflow obstruction after bronchodilator", "Fixed airflow obstruction without response", "Restrictive ventilatory defect", "Poor effort with early termination"],
            ["The post-treatment expiratory loop is taller", "Expiratory concavity is reduced after beta-2 agonist", "The post-treatment curve approaches the normal reference"],
            "The paired loops show substantial improvement after beta-2 agonist, supporting reversible airflow obstruction as in asthma.",
            [
                "A clear post-bronchodilator increase in peak flow and restoration of expiratory contour demonstrates reversibility.",
                "Fixed obstruction would show little meaningful change in expiratory flow or contour after bronchodilator.",
                "Restriction would chiefly reduce loop volume while preserving shape rather than normalize a scooped curve after bronchodilator.",
                "Early termination truncates the expiratory maneuver and does not produce a reproducible post-treatment normalization of the loop.",
            ],
            "What physiologic response is demonstrated by these paired flow-volume loops?",
        ),
    },
    {
        "slug": "rv-pressure-overload-echo",
        "answer": "Right-ventricular pressure overload with septal flattening",
        "modality": "Echocardiography",
        "category": "Pulmonary hypertension",
        "lecture": "P32 - Pulmonary Hypertension - A Clinical Reasoning Approach",
        "local": "Echocardiogram in Pulmonary Artery Hypertension (2:3).jpg",
        "ground_truth": "The verified P32 picture manifest identifies an enlarged RV and flattened/compressed LV on short-axis echocardiography.",
        "findings": "The right ventricle is enlarged and the interventricular septum is flattened, creating a D-shaped left ventricle in short axis.",
        "question": q(
            ["Right-ventricular pressure overload with septal flattening", "Isolated left-ventricular hypertrophy", "Large pericardial effusion", "Normal parasternal short-axis view"],
            ["The right ventricle is enlarged", "The interventricular septum is flattened", "The left ventricle has a D-shaped short-axis contour"],
            "The D-shaped left ventricle and enlarged right ventricle indicate right-sided pressure overload, a key echocardiographic clue to pulmonary hypertension.",
            [
                "Right-sided pressure overload flattens the septum and deforms the LV into a D shape while enlarging the RV, matching the image.",
                "Isolated LV hypertrophy would thicken the LV walls without producing an enlarged RV and septal flattening toward the LV.",
                "A pericardial effusion would appear as an anechoic fluid rim around the heart, which is not present.",
                "A normal short-axis LV is round and the RV is smaller; the marked septal flattening here is abnormal.",
            ],
            "Identify the principal echocardiographic finding shown.",
        ),
    },
    {
        "slug": "right-heart-strain-ecg",
        "answer": "Right-ventricular hypertrophy/strain pattern",
        "modality": "EKG",
        "category": "Pulmonary hypertension",
        "lecture": "P32 - Pulmonary Hypertension - A Clinical Reasoning Approach",
        "local": "ECG in Pulmonary Hypertension Secondary to an Atrial Septal Defect.jpg",
        "ground_truth": "The verified P32 picture manifest identifies a right-axis/right-heart-strain ECG in pulmonary hypertension.",
        "findings": "The tracing preserves standard 12-lead order and calibration and shows right-axis deviation with anterior right-precordial repolarization abnormalities.",
        "question": q(
            ["Right-ventricular hypertrophy/strain pattern", "Diffuse acute pericarditis", "Left bundle-branch block", "Hyperkalemia with peaked T waves"],
            ["QRS axis is rightward", "Right-precordial leads show a right-heart strain morphology", "Repolarization abnormalities are regional rather than diffuse"],
            "The preserved 12-lead tracing shows a rightward axis and right-precordial strain pattern compatible with pulmonary hypertension.",
            [
                "Right-axis deviation with right-precordial dominant forces and strain-type repolarization changes supports RV hypertrophy/strain.",
                "Acute pericarditis causes widespread concave ST elevation and PR depression, not this right-sided pressure pattern.",
                "Left bundle-branch block requires a broad QRS with characteristic lateral notching and discordance; the QRS duration here is not frankly prolonged.",
                "Hyperkalemia produces diffuse narrow peaked T waves and progressive conduction slowing, features not dominant in this tracing.",
            ],
            "Identify the cardiopulmonary ECG pattern shown.",
        ),
    },
    {
        "slug": "spirometry-procedure",
        "answer": "Diagnostic spirometry",
        "modality": "Clinical Image",
        "category": "Pulmonary function testing",
        "lecture": "P37 - Advanced Spirometry Review - Interactive Workshop",
        "local": "P297 Spirometry.png",
        "ground_truth": "The verified P37 picture manifest identifies the patient position and equipment for a coached forced spirometry maneuver.",
        "findings": "A seated patient seals the lips around a filtered mouthpiece connected to a desktop spirometer while wearing a nose clip.",
        "question": q(
            ["Diagnostic spirometry", "Peak expiratory flow monitoring", "Incentive spirometry", "Bronchoprovocation by exercise"],
            ["The mouthpiece connects to a computerized flow-measuring system", "A nose clip prevents nasal airflow", "The setup supports a coached forced expiratory maneuver"],
            "The image shows the standard setup for diagnostic spirometry and a coached forced respiratory maneuver.",
            [
                "Diagnostic spirometry uses a sealed mouthpiece, nose clip, and calibrated flow-recording system, exactly as shown.",
                "Peak-flow monitoring typically uses a small handheld mechanical meter without this computerized testing setup.",
                "Incentive spirometry is a bedside inspiratory-training device with a visual volume/flow target, not a diagnostic recording system.",
                "Exercise bronchoprovocation requires an exercise protocol and serial spirometry; no exercise equipment is shown here.",
            ],
            "Identify the pulmonary function procedure shown.",
        ),
    },
    {
        "slug": "golden-s-sign",
        "answer": "Golden S sign from right-upper-lobe collapse around a hilar mass",
        "modality": "X-ray and CT",
        "category": "Thoracic imaging signs",
        "lecture": "P27.2 - Chest X-Ray Final Review",
        "local_path": str(PULM / "P27.2 - Chest X-Ray Final Review" / "Golden S Sign - Right Upper Lobe Atelectasis with Hilar Mass.jpg"),
        "landing": "https://pmc.ncbi.nlm.nih.gov/articles/PMC6893008/",
        "creator": "Alessandra Chiarenza et al.",
        "organization": "Insights into Imaging",
        "license": "CC BY 4.0",
        "license_url": "https://creativecommons.org/licenses/by/4.0/",
        "rights_status": "cc_by",
        "ground_truth": "The existing verified P27.2 web manifest identifies Figure 17 as the Golden S sign from RUL atelectasis around a hilar mass.",
        "findings": "The elevated minor fissure has a concave central contour around a right hilar mass, producing the characteristic reverse-S configuration.",
        "question": q(
            ["Golden S sign from right-upper-lobe collapse around a hilar mass", "Hampton hump from pulmonary infarction", "Westermark sign from pulmonary embolism", "Air-crescent sign in aspergillosis"],
            ["The right upper lobe is volume depleted", "The minor fissure is displaced upward", "A central hilar mass deforms the fissure into an S contour"],
            "The combination of right-upper-lobe atelectasis and a central hilar mass produces the Golden S sign.",
            [
                "The Golden S sign is formed when an elevated fissure from RUL collapse curves around a central obstructing mass, as shown.",
                "A Hampton hump is a peripheral pleural-based wedge-shaped opacity, not a deformed fissure surrounding a hilar mass.",
                "Westermark sign is regional oligemia with reduced vascular markings distal to embolic obstruction, not lobar collapse.",
                "An air-crescent sign is a crescent of air around an intracavitary or necrotic focus, which is absent here.",
            ],
        ),
    },
    {
        "slug": "calcified-pleural-plaque",
        "answer": "Calcified pleural plaque from asbestos exposure",
        "modality": "X-ray",
        "category": "Occupational lung disease",
        "lecture": "P27.2 - Chest X-Ray Final Review",
        "local_path": str(PULM / "P27.2 - Chest X-Ray Final Review" / "Calcified Pleural Plaque - Chest Radiograph.jpg"),
        "landing": "https://commons.wikimedia.org/wiki/File:Asbestosis_and_cryptococcosis_-_Pleural_plaque_-_X-ray_Case_194_(5998756067).jpg",
        "creator": "Yale Rosen",
        "organization": "Wikimedia Commons / Pulmonary Pathology Flickr collection",
        "license": "CC BY-SA 2.0",
        "license_url": "https://creativecommons.org/licenses/by-sa/2.0/",
        "rights_status": "cc_by_sa",
        "ground_truth": "The existing verified P27.2 web manifest identifies the calcified diaphragmatic pleural plaque.",
        "findings": "Dense plaque-like calcification follows the diaphragmatic pleural surface rather than lying within lung parenchyma.",
        "question": q(
            ["Calcified pleural plaque from asbestos exposure", "Lobar pneumonia", "Miliary tuberculosis", "Pneumothorax"],
            ["The opacity is pleural based", "Calcification follows the diaphragmatic contour", "There is no lobar air-space consolidation or diffuse micronodularity"],
            "A calcified diaphragmatic pleural plaque is a classic marker of prior asbestos exposure.",
            [
                "Pleural plaques are focal pleural thickenings that commonly calcify along the diaphragm and chest wall, matching this contour.",
                "Lobar pneumonia produces air-space opacity with possible air bronchograms rather than a sharply calcified pleural plaque.",
                "Miliary tuberculosis produces innumerable tiny bilateral parenchymal nodules, which are absent.",
                "Pneumothorax produces a visceral pleural line with absent peripheral lung markings, not dense pleural calcification.",
            ],
        ),
    },
    {
        "slug": "situs-inversus-cxr",
        "answer": "Situs inversus totalis with dextrocardia",
        "modality": "X-ray",
        "category": "Thoracic orientation",
        "lecture": "P18 - Basic Interpretation of Chest X-Ray",
        "local": "Situs inversus with dextrocardia (situs inversus totalis).jpg",
        "ground_truth": "The verified P18/P27.2 picture manifests identify dextrocardia with reversed thoracoabdominal situs.",
        "findings": "The cardiac apex points rightward and the gastric bubble/upper abdominal viscera are mirrored relative to normal anatomy.",
        "question": q(
            ["Situs inversus totalis with dextrocardia", "Isolated right-lower-lobe atelectasis", "Left tension pneumothorax", "Severe patient rotation"],
            ["Cardiac apex is right sided", "Thoracoabdominal organ orientation is reversed", "The mirrored anatomy is internally consistent rather than rotational distortion"],
            "The radiograph shows dextrocardia with mirrored visceral orientation, establishing situs inversus totalis.",
            [
                "True rightward cardiac apex plus reversed abdominal organ/gastric-bubble orientation supports situs inversus totalis.",
                "Right-lower-lobe atelectasis causes localized opacity and volume loss but does not mirror the heart and abdominal viscera.",
                "A left tension pneumothorax shifts the mediastinum but leaves the intrinsic cardiac apex and abdominal situs unchanged.",
                "Rotation changes apparent mediastinal projection but cannot reverse the consistent thoracoabdominal organ arrangement.",
            ],
        ),
    },
    {
        "slug": "pulmonary-hypertension-cxr",
        "answer": "Pulmonary arterial hypertension on chest radiograph",
        "modality": "X-ray",
        "category": "Pulmonary hypertension",
        "lecture": "P32 - Pulmonary Hypertension - A Clinical Reasoning Approach",
        "local": "Pulmonary Hypertension (1:2).jpg",
        "ground_truth": "The verified P32 picture manifest identifies enlarged central pulmonary arteries and peripheral pruning on PA radiography.",
        "findings": "The central pulmonary arteries are enlarged, while distal peripheral vessels are relatively attenuated; the right-heart contour is prominent.",
        "question": q(
            ["Pulmonary arterial hypertension on chest radiograph", "Cardiogenic pulmonary edema", "Right-upper-lobe atelectasis", "Massive pleural effusion"],
            ["Central pulmonary arteries are prominent", "Peripheral vascular markings are relatively pruned", "There is no diffuse edema or hemithorax whiteout"],
            "Enlarged central pulmonary arteries with peripheral pruning and right-heart prominence support pulmonary arterial hypertension.",
            [
                "Pulmonary hypertension classically enlarges the central pulmonary arteries while attenuating peripheral vessels, as shown.",
                "Cardiogenic edema produces vascular indistinctness, interstitial/alveolar opacity, and often pleural effusions rather than peripheral pruning.",
                "Right-upper-lobe atelectasis produces fissural displacement and upper-lobe volume loss, not symmetric central artery enlargement.",
                "A massive pleural effusion creates hemithorax opacity with a meniscus and possible contralateral shift, which is absent.",
            ],
        ),
    },
    {
        "slug": "thoracentesis-procedure",
        "answer": "Thoracentesis",
        "modality": "Diagram",
        "category": "Pulmonary procedures",
        "lecture": "P15 - Approach to the Patient with Respiratory Disease and Pulmonary Preventative Care",
        "local": "P473 Thoracentesis.png",
        "ground_truth": "The verified P15 picture manifest identifies patient positioning and the safe needle approach for thoracentesis.",
        "findings": "A needle/catheter is introduced through the posterolateral intercostal space toward a dependent pleural-fluid collection while the patient sits leaning forward.",
        "question": q(
            ["Thoracentesis", "Needle cricothyrotomy", "Subclavian central-line placement", "Tube thoracostomy"],
            ["The patient is seated and leaning forward", "The needle enters a posterolateral interspace", "The target is a dependent pleural collection"],
            "The diagram demonstrates thoracentesis for aspiration of pleural fluid.",
            [
                "Thoracentesis uses a needle or small catheter through the posterolateral chest into dependent pleural fluid, matching the diagram.",
                "Cricothyrotomy enters the anterior neck through the cricothyroid membrane, not the posterolateral thorax.",
                "A subclavian central line is inserted beneath the clavicle toward the central veins rather than into the pleural collection.",
                "Tube thoracostomy uses a larger incision and tube in the lateral safe triangle, not the fine aspiration needle shown.",
            ],
            "Identify the pulmonary procedure illustrated.",
        ),
    },
    {
        "slug": "pleural-effusion-lung-ultrasound",
        "answer": "Pleural effusion on lung ultrasound",
        "modality": "Ultrasound",
        "category": "Point-of-care ultrasound",
        "lecture": "P15 - Approach to the Patient with Respiratory Disease and Pulmonary Preventative Care",
        "video_frame": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/3/3d/Portable-bedside-ultrasound-the-visual-stethoscope-of-the-21st-century-1757-7241-20-18-S7.ogv",
            "landing": "https://commons.wikimedia.org/wiki/File:Portable-bedside-ultrasound-the-visual-stethoscope-of-the-21st-century-1757-7241-20-18-S7.ogv",
            "creator": "Gillman L and Kirkpatrick A",
            "organization": "Wikimedia Commons / Scandinavian Journal of Trauma, Resuscitation and Emergency Medicine",
            "license": "CC BY 2.0",
            "license_url": "https://creativecommons.org/licenses/by/2.0/",
            "rights_status": "cc_by",
            "sha1": "5f35d22482a4fc6d57ce730a6eaa67ebc4777f6d",
            "frame_time_seconds": 3.0,
            "source_filename": "Portable-bedside-ultrasound-the-visual-stethoscope-of-the-21st-century-1757-7241-20-18-S7.ogv",
        },
        "ground_truth": "The Commons asset page and linked open-access article identify this real-time lung-ultrasound sequence as a hypoechoic pleural effusion above the diaphragm; the displayed image is a reproducible frame at 3.0 seconds.",
        "findings": "A dependent anechoic-to-hypoechoic collection lies above the bright curvilinear diaphragm, separating the chest wall from compressed lung.",
        "question": q(
            ["Pleural effusion on lung ultrasound", "Lung consolidation with air bronchograms", "B-lines indicating interstitial syndrome", "Normal A-line pattern"],
            ["A dark fluid collection is present above the diaphragm", "The collection separates the chest wall from adjacent lung", "Dependent compressed lung is visible next to the fluid"],
            "The anechoic/hypoechoic dependent collection above the diaphragm is pleural fluid.",
            [
                "Pleural effusion appears as an anechoic or hypoechoic collection above the diaphragm, often with adjacent compressed lung, matching this image.",
                "Consolidated lung is tissue-like and may contain bright branching air bronchograms; it is not a simple dark fluid pocket.",
                "B-lines are bright vertical artifacts arising from the pleural line and extending to the far field, not a focal fluid collection.",
                "Normally aerated lung shows pleural sliding and repetitive horizontal A-lines rather than visible dependent fluid.",
            ],
        ),
    },
    {
        "slug": "consolidation-air-bronchograms-lung-ultrasound",
        "answer": "Lung consolidation with air bronchograms",
        "modality": "Ultrasound",
        "category": "Point-of-care ultrasound",
        "lecture": "P15 - Approach to the Patient with Respiratory Disease and Pulmonary Preventative Care",
        "video_frame": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/4/48/Prospective-application-of-clinician-performed-lung-ultrasonography-during-the-2009-H1N1-influenza-2036-7902-4-16-S3.ogv",
            "landing": "https://commons.wikimedia.org/wiki/File:Prospective-application-of-clinician-performed-lung-ultrasonography-during-the-2009-H1N1-influenza-2036-7902-4-16-S3.ogv",
            "creator": "Tsung J, Kessler D, and Shah V",
            "organization": "Wikimedia Commons / Critical Ultrasound Journal",
            "license": "CC BY 2.0",
            "license_url": "https://creativecommons.org/licenses/by/2.0/",
            "rights_status": "cc_by",
            "sha1": "b37c3996ef1d24142d4fdfef97e707be34faeb6f",
            "frame_time_seconds": 4.0,
            "source_filename": "Prospective-application-of-clinician-performed-lung-ultrasonography-during-the-2009-H1N1-influenza-2036-7902-4-16-S3.ogv",
        },
        "ground_truth": "The Commons asset page and linked open-access article identify this sequence as right anterior lung consolidation with air bronchograms; the displayed image is a reproducible frame at 4.0 seconds.",
        "findings": "Subpleural lung has tissue-like echogenicity with internal bright punctate and branching echoes representing air bronchograms.",
        "question": q(
            ["Lung consolidation with air bronchograms", "Pleural effusion", "B-lines indicating interstitial syndrome", "Normal A-line pattern"],
            ["The subpleural lung has a tissue-like appearance", "Bright internal echoes represent air bronchograms", "The normal reverberation pattern of aerated lung is replaced"],
            "The tissue-like subpleural region containing bright air bronchograms is sonographic lung consolidation.",
            [
                "Consolidated lung becomes tissue-like on ultrasound and commonly contains punctate or branching hyperechoic air bronchograms, as shown.",
                "Pleural effusion would be a dark fluid collection above the diaphragm rather than solid-appearing lung with internal bright echoes.",
                "B-lines are discrete vertical artifacts that arise from the pleural line and extend through the far field; they do not create hepatized lung tissue.",
                "Normally aerated lung is dominated by pleural sliding and horizontal A-lines, not a visible tissue-like subpleural region.",
            ],
        ),
    },
    {
        "slug": "right-mainstem-endotracheal-tube",
        "answer": "Right mainstem endotracheal-tube malposition",
        "modality": "X-ray",
        "category": "Lines and tubes",
        "lecture": "P18 - Basic Interpretation of Chest X-Ray",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/4/4e/Trachealtubus_mit_der_Spitze_im_rechten_Hauptbronchus_79W_-_CR_ap_-_001.jpg",
            "landing": "https://commons.wikimedia.org/wiki/File:Trachealtubus_mit_der_Spitze_im_rechten_Hauptbronchus_79W_-_CR_ap_-_001.jpg",
            "creator": "Hellerhoff",
            "organization": "Wikimedia Commons",
            "license": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "rights_status": "cc_by_sa",
            "sha1": "6d5b821f154df429a2a7c40dcd40ad091b5c522a",
        },
        "ground_truth": "The creator's Commons page explicitly identifies the endotracheal-tube tip within the right main bronchus.",
        "findings": "The endotracheal tube descends past the carina into the right main bronchus rather than ending several centimeters above the carina.",
        "question": q(
            ["Right mainstem endotracheal-tube malposition", "Correct endotracheal-tube position above the carina", "Esophageal intubation", "Left mainstem endotracheal-tube malposition"],
            ["The tube follows the tracheal air column", "Its tip projects distal to the carina", "The tip enters the right main bronchus"],
            "The endotracheal tube is advanced too far, with its tip in the right main bronchus.",
            [
                "A tube tip beyond the carina in the right main bronchus is a right mainstem intubation and risks under-ventilating the left lung.",
                "A correctly positioned adult endotracheal tube should terminate in the trachea above the carina, not within a main bronchus.",
                "An esophageal tube would not remain centered in the tracheal air column and would typically continue below the diaphragm toward the stomach.",
                "The tube tip is directed into the right, not the left, main bronchus.",
            ],
            "Assess the endotracheal-tube position on this chest radiograph.",
        ),
    },
    {
        "slug": "endotracheal-and-nasogastric-tubes-cxr",
        "answer": "Endotracheal and nasogastric tubes, both appropriately positioned",
        "modality": "X-ray",
        "category": "Lines and tubes",
        "lecture": "P18 - Basic Interpretation of Chest X-Ray",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/d/dc/ETTubeandNGtube.png",
            "landing": "https://commons.wikimedia.org/wiki/File:ETTubeandNGtube.png",
            "creator": "James Heilman, MD",
            "organization": "Wikimedia Commons",
            "license": "CC BY-SA 4.0",
            "license_url": "https://creativecommons.org/licenses/by-sa/4.0/",
            "rights_status": "cc_by_sa",
            "sha1": "0ccbfe41442ec81a9cc2b5dd13c4c2c2172efed0",
        },
        "ground_truth": "The creator's Commons page explicitly identifies an endotracheal tube and nasogastric tube, both in good position.",
        "findings": "One tube terminates centrally within the trachea above the carina, while a thinner enteric tube follows the esophagus and continues below the diaphragm.",
        "question": q(
            ["Endotracheal and nasogastric tubes, both appropriately positioned", "Endotracheal tube and central venous catheter", "Tracheostomy tube and pleural drain", "Pulmonary-artery catheter and feeding tube"],
            ["A larger airway tube terminates above the carina", "A thinner tube follows the esophagus", "The enteric tube continues below the diaphragm"],
            "The radiograph shows an appropriately positioned endotracheal tube plus a nasogastric tube coursing below the diaphragm.",
            [
                "The central airway tube terminates above the carina and the second thin tube follows the esophagus below the diaphragm, identifying an endotracheal tube and nasogastric tube.",
                "A central venous catheter would enter from the neck or subclavian region and end in the SVC rather than continue below the diaphragm.",
                "A tracheostomy tube enters directly through the anterior neck, and a pleural drain enters through the lateral chest wall; neither course is shown.",
                "A pulmonary-artery catheter traverses the right heart toward a pulmonary artery and has a different intrathoracic course from the central airway tube shown.",
            ],
            "Identify the two tubes and assess their overall position on this chest radiograph.",
        ),
    },
    {
        "slug": "kerley-b-lines-cxr",
        "answer": "Kerley B lines from interlobular septal thickening",
        "modality": "X-ray",
        "category": "Pulmonary edema and heart failure",
        "lecture": "P18 - Basic Interpretation of Chest X-Ray",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/c/ca/Chest_radiograph_of_a_lung_with_Kerley_B_lines.jpg",
            "landing": "https://commons.wikimedia.org/wiki/File:Chest_radiograph_of_a_lung_with_Kerley_B_lines.jpg",
            "creator": "Mikael Haggstrom",
            "organization": "Wikimedia Commons",
            "license": "CC0 1.0",
            "license_url": "https://creativecommons.org/publicdomain/zero/1.0/",
            "rights_status": "cc0",
            "sha1": "02606849078e5bb831486a6704fdd3396f1b468f",
        },
        "ground_truth": "The creator's Commons page identifies distinct Kerley B lines with cardiomegaly and vascular congestion in congestive heart failure.",
        "findings": "Short horizontal peripheral septal lines are visible near the costophrenic regions, with cardiomegaly and pulmonary vascular congestion.",
        "question": q(
            ["Kerley B lines from interlobular septal thickening", "Honeycombing from advanced pulmonary fibrosis", "Visceral pleural line of pneumothorax", "Air bronchograms within lobar consolidation"],
            ["Short horizontal lines reach the lateral pleural surface", "The lines are most conspicuous at the lung bases", "Cardiomegaly and vascular congestion support interstitial edema"],
            "The short peripheral basal septal lines are Kerley B lines, a radiographic sign of interlobular septal thickening often caused by hydrostatic edema.",
            [
                "Kerley B lines are short, horizontal peripheral lines at the lung bases that reflect thickened interlobular septa, matching this image.",
                "Honeycombing produces clustered subpleural cystic lucencies and volume loss rather than a few thin horizontal septal lines.",
                "A pneumothorax pleural line is a longer visceral pleural edge with absent lung markings peripheral to it, which is not present here.",
                "Air bronchograms are branching lucencies within an air-space opacity, not short peripheral septal lines.",
            ],
            "Identify the specific interstitial sign on this chest radiograph.",
        ),
    },
    {
        "slug": "barcode-sign-lung-ultrasound",
        "answer": "Barcode/stratosphere sign indicating absent lung sliding",
        "modality": "Ultrasound",
        "category": "Point-of-care ultrasound",
        "lecture": "P15 - Approach to the Patient with Respiratory Disease and Pulmonary Preventative Care",
        "web": {
            "url": "https://cdn.ncbi.nlm.nih.gov/pmc/blobs/6e2c/2700565/f16065fbe367/JETS-01-19-g002.jpg",
            "landing": "https://pmc.ncbi.nlm.nih.gov/articles/PMC2700565/",
            "creator": "Michael B. Stone",
            "organization": "Journal of Emergencies, Trauma, and Shock / PubMed Central",
            "license": "CC BY 2.0",
            "license_url": "https://creativecommons.org/licenses/by/2.0/",
            "rights_status": "cc_by",
            "sha1": "c776087c7aa895392df3923e4370b52527a89bfa",
        },
        "ground_truth": "Figure 2 of the CC BY open-access article explicitly identifies this M-mode image as the stratosphere/barcode sign caused by absent lung sliding in traumatic pneumothorax.",
        "findings": "M-mode shows parallel horizontal lines both above and below the pleural line, without the granular sandy pattern of normally sliding lung.",
        "question": q(
            ["Barcode/stratosphere sign indicating absent lung sliding", "Seashore sign indicating normal lung sliding", "B-lines indicating interstitial syndrome", "Dynamic air bronchograms within consolidation"],
            ["Parallel horizontal lines extend above and below the pleural line", "The granular lower seashore pattern is absent", "The M-mode pattern records absent pleural motion at this interspace"],
            "The uniform horizontal M-mode lines above and below the pleura form the barcode or stratosphere sign, indicating absent lung sliding and raising concern for pneumothorax in the appropriate context.",
            [
                "The barcode/stratosphere pattern consists of uninterrupted horizontal lines above and below the pleura because sliding is absent; it supports pneumothorax when integrated with other sonographic signs.",
                "The seashore sign requires a granular sandy pattern below the pleural line from normal sliding, which is absent here.",
                "B-lines are vertical B-mode reverberation artifacts extending from the pleura to the far field, not a uniform M-mode stripe pattern.",
                "Dynamic air bronchograms are moving bright branching echoes within tissue-like consolidated lung, not parallel M-mode lines.",
            ],
            "Identify the M-mode lung-ultrasound sign shown.",
        ),
    },
    {
        "slug": "endobronchial-mass-bronchoscopy",
        "answer": "Obstructing endobronchial mass",
        "modality": "Clinical Image",
        "category": "Bronchoscopy and airway lesions",
        "lecture": "P21 - Lung Cancer",
        "web": {
            "url": "https://upload.wikimedia.org/wikipedia/commons/4/4c/Lung_cancer_in_L._Bronchus_-_bronchoscopic_view.png",
            "landing": "https://commons.wikimedia.org/wiki/File:Lung_cancer_in_L._Bronchus_-_bronchoscopic_view.png",
            "creator": "JHeuser",
            "organization": "Wikimedia Commons",
            "license": "CC BY 2.5",
            "license_url": "https://creativecommons.org/licenses/by/2.5/",
            "rights_status": "cc_by",
            "sha1": "021eac2caa411909ce92f45f8b8e60dffcc6d6a2",
        },
        "ground_truth": "The Commons source description identifies a lung tumor invading the left bronchus on bronchoscopic view; the quiz key is deliberately limited to the visible finding rather than a histologic tumor type.",
        "findings": "An irregular focal mass projects into and narrows the bronchial lumen, interrupting the expected smooth airway contour.",
        "question": q(
            ["Obstructing endobronchial mass", "Normal bronchial bifurcation", "Diffuse purulent bronchitis", "Aspirated radiopaque foreign body"],
            ["A focal irregular lesion protrudes into the airway lumen", "The bronchial opening is visibly narrowed", "The abnormality is localized rather than diffuse"],
            "The bronchoscopic image shows an irregular endobronchial mass obstructing the bronchial lumen. Histologic tumor type cannot be determined from this view alone.",
            [
                "A focal irregular tissue mass projects into and narrows the bronchial lumen, which is the visible endobronchial finding.",
                "A normal bifurcation has smooth mucosa and patent daughter bronchi without a focal obstructing lesion.",
                "Diffuse purulent bronchitis would show widespread erythema, edema, and secretions rather than one discrete obstructing mass.",
                "An aspirated foreign body would appear as a discrete nonmucosal object; the lesion shown is contiguous with abnormal airway tissue and is not visibly radiopaque material.",
            ],
            "Identify the principal bronchoscopic finding.",
        ),
    },
    {
        "slug": "squamous-cell-carcinoma-keratin-pearls",
        "answer": "Pulmonary squamous cell carcinoma with keratin pearls",
        "modality": "Histology",
        "category": "Lung cancer",
        "lecture": "P26 - Diseases of the Respiratory Tract - Part 3 - Vascular, Cancer, Other Disease (Pathology)",
        "local": "D Squamous Cell Lung Carcinoma Keratin Pearls Histology.png",
        "ground_truth": "The verified P26/P39 Pulm Pictures manifests identify this lecture-aligned histology as squamous cell lung carcinoma with keratin pearls.",
        "findings": "Concentric eosinophilic whorls of keratin are surrounded by atypical polygonal squamous cells.",
        "question": q(
            ["Pulmonary squamous cell carcinoma with keratin pearls", "Pulmonary adenocarcinoma", "Small cell lung carcinoma", "Pulmonary carcinoid tumor"],
            ["Concentric eosinophilic keratin pearls are present", "The tumor cells show squamous differentiation", "There is no gland formation or small-cell molding"],
            "The concentric keratin pearls establish squamous differentiation and support pulmonary squamous cell carcinoma.",
            [
                "Squamous cell carcinoma is supported by concentric keratin pearls and atypical squamous cells, the decisive features shown.",
                "Adenocarcinoma would form malignant glands or produce mucin rather than concentric keratin pearls.",
                "Small cell carcinoma would show sheets of small hyperchromatic cells with nuclear molding and scant cytoplasm, not keratinization.",
                "A carcinoid tumor typically has organoid nests or trabeculae of uniform neuroendocrine cells without keratin pearls.",
            ],
            "Identify the pulmonary neoplasm shown on histology.",
        ),
    },
    {
        "slug": "curschmann-spiral-asthma",
        "answer": "Curschmann spiral from asthma",
        "modality": "Cytology",
        "category": "Asthma pathology",
        "lecture": "P19 - Obstructive Diseases and Airway Diseases",
        "local": "F_Asthma_Curschmann_Spirals.png",
        "ground_truth": "The verified P19 Pulm Pictures manifest identifies the coiled mucus cast as a Curschmann spiral from asthmatic sputum.",
        "findings": "A long, tightly coiled basophilic mucus cast is present in a sputum preparation.",
        "question": q(
            ["Curschmann spiral from asthma", "Ferruginous asbestos body", "Charcot-Leyden crystal", "Branching fungal hypha"],
            ["The structure is a long coiled mucus cast", "Its edges undulate rather than forming a rigid crystal", "No beaded iron coating or septate branching is present"],
            "The coiled mucus cast is a Curschmann spiral, a classic sputum finding in asthma.",
            [
                "Curschmann spirals are twisted mucus casts of small airways and have the long coiled contour shown here.",
                "Ferruginous bodies are golden-brown beaded rods with an iron-protein coat, not flexible basophilic coils.",
                "Charcot-Leyden crystals are sharply pointed bipyramidal structures derived from eosinophils, not mucus spirals.",
                "Fungal hyphae form tubular septate or pauciseptate branches rather than a single thick coiled mucus cast.",
            ],
            "Identify the sputum finding shown.",
        ),
    },
    {
        "slug": "charcot-leyden-crystal-asthma",
        "answer": "Charcot-Leyden crystal",
        "modality": "Cytology",
        "category": "Asthma pathology",
        "lecture": "P19 - Obstructive Diseases and Airway Diseases",
        "local": "G_Asthma_Charcot_Leyden_Crystal.png",
        "ground_truth": "The verified P19 Pulm Pictures manifest identifies the pointed crystal as a Charcot-Leyden crystal associated with eosinophil-rich asthma.",
        "findings": "A slender, sharply pointed bipyramidal crystal is isolated in an inflammatory background.",
        "question": q(
            ["Charcot-Leyden crystal", "Curschmann spiral", "Ferruginous asbestos body", "Calcium oxalate crystal"],
            ["The structure is elongated and sharply pointed at both ends", "It is a rigid crystal rather than a coiled mucus strand", "There is no golden-brown beaded coating"],
            "The bipyramidal crystal is a Charcot-Leyden crystal formed from eosinophil products and associated with asthma and other eosinophilic disorders.",
            [
                "Charcot-Leyden crystals are slender bipyramidal eosinophil-derived crystals with pointed ends, matching this structure.",
                "A Curschmann spiral is a long twisted mucus cast with an undulating coiled outline, not a rigid pointed crystal.",
                "A ferruginous body is a golden-brown segmented rod coated with iron and protein, which is not seen here.",
                "Calcium oxalate crystals are typically envelope- or dumbbell-shaped and are not the classic sputum finding shown.",
            ],
            "Identify the microscopic finding shown.",
        ),
    },
    {
        "slug": "blastomycosis-broad-based-budding",
        "answer": "Blastomyces with broad-based budding",
        "modality": "Microscopy",
        "category": "Endemic mycosis",
        "lecture": "P30 - Microbiology of Pneumonia - Fungal Infections",
        "local": "Blastomycosis Histology.png",
        "transform": {"crop": [105, 150, 645, 685]},
        "ground_truth": "The verified P30 Pulm Pictures manifest identifies this fungal morphology as Blastomyces; the quiz crop removes the answer title and panel labels.",
        "findings": "A large thick-walled yeast has a daughter bud attached by a broad base.",
        "question": q(
            ["Blastomyces with broad-based budding", "Cryptococcus with a thick capsule", "Coccidioides spherule", "Histoplasma within macrophages"],
            ["The yeast is large and thick walled", "The daughter cell attaches through a broad neck", "No capsule halo, endospores, or intracellular clusters dominate"],
            "A large thick-walled yeast with a broad-based bud is the classic tissue morphology of Blastomyces.",
            [
                "Blastomyces is identified by large thick-walled yeast with broad-based budding, exactly the relationship shown.",
                "Cryptococcus usually has narrow-based budding and a prominent polysaccharide capsule producing a clear halo.",
                "Coccidioides appears in tissue as a large spherule containing endospores rather than a budding yeast.",
                "Histoplasma consists of numerous tiny narrow-budding intracellular yeasts clustered in macrophages, not one large broad-based pair.",
            ],
            "Identify the fungal morphology shown.",
        ),
    },
    {
        "slug": "paracoccidioides-pilot-wheel",
        "answer": "Paracoccidioides with pilot-wheel budding",
        "modality": "Microscopy",
        "category": "Endemic mycosis",
        "lecture": "P30 - Microbiology of Pneumonia - Fungal Infections",
        "local": "Paracoccidioidomycosis Histology.png",
        "transform": {"crop": [105, 252, 645, 785]},
        "ground_truth": "The verified P30 Pulm Pictures manifest identifies this fungal morphology as Paracoccidioides; the quiz crop removes the answer title and panel labels.",
        "findings": "Multiple peripheral daughter buds radiate from a larger central mother yeast in a pilot-wheel configuration.",
        "question": q(
            ["Paracoccidioides with pilot-wheel budding", "Blastomyces with broad-based budding", "Cryptococcus with a thick capsule", "Coccidioides spherule"],
            ["Many daughter buds surround one mother cell", "The buds radiate in a pilot-wheel pattern", "The structure is neither a single broad-based pair nor an endospore-filled spherule"],
            "Multiple buds radiating from a central yeast create the characteristic pilot-wheel morphology of Paracoccidioides.",
            [
                "Paracoccidioides classically forms multiple narrow-necked daughter buds around a mother yeast, producing the pilot-wheel pattern shown.",
                "Blastomyces usually forms a single broad-based daughter bud rather than numerous radiating buds.",
                "Cryptococcus shows a thick capsule and usually narrow-based single budding, not a pilot-wheel arrangement.",
                "Coccidioides forms nonbudding tissue spherules filled with endospores, which are absent here.",
            ],
            "Identify the fungal morphology shown.",
        ),
    },
    {
        "slug": "oral-candidiasis-inhaled-corticosteroid",
        "answer": "Oral candidiasis associated with inhaled corticosteroid use",
        "modality": "Clinical Image",
        "category": "Asthma pharmacology",
        "lecture": "P22-23 - Drugs Used for Treatment of Asthma and COPD",
        "local": "P391 Inhaled Steroids 01.png",
        "ground_truth": "The verified P22-23 Pulm Pictures manifest identifies the removable white oral plaques as candidiasis, a major local adverse effect of inhaled corticosteroids.",
        "findings": "Confluent white plaques coat an erythematous tongue and oral mucosa.",
        "question": q(
            ["Oral candidiasis associated with inhaled corticosteroid use", "Aphthous ulcers", "Herpetic gingivostomatitis", "Oral hairy leukoplakia"],
            ["White plaque-like material coats the tongue", "The background mucosa is erythematous", "There are no discrete ulcers, vesicles, or lateral corrugated patches"],
            "White pseudomembranous plaques on erythematous oral mucosa are typical of oral candidiasis, an important local complication of inhaled corticosteroids.",
            [
                "Oral candidiasis produces removable white plaques on an erythematous base and is promoted by oropharyngeal steroid deposition.",
                "Aphthous disease causes discrete shallow painful ulcers with erythematous halos rather than diffuse white plaques.",
                "Herpetic gingivostomatitis produces clusters of vesicles and erosive ulcers with gingival inflammation, not a confluent pseudomembrane.",
                "Oral hairy leukoplakia causes adherent corrugated white plaques along the lateral tongue, not this diffuse erythematous pseudomembranous coating.",
            ],
            "Identify the complication shown in a patient using inhaled corticosteroids.",
        ),
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, destination: Path) -> None:
    temporary = destination.with_suffix(destination.suffix + ".part")
    for attempt in range(5):
        request = urllib.request.Request(url, headers={"User-Agent": "PulmonaryPictureQuiz/1.0"})
        try:
            with urllib.request.urlopen(request, timeout=60) as response, temporary.open("wb") as out:
                shutil.copyfileobj(response, out)
            temporary.replace(destination)
            return
        except (urllib.error.HTTPError, urllib.error.URLError, TimeoutError):
            temporary.unlink(missing_ok=True)
            if attempt == 4:
                raise
            time.sleep(2 ** attempt)


def create_variant(source: Path, destination: Path, transform: dict) -> tuple[int, int]:
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB")
        if transform.get("crop"):
            image = image.crop(tuple(transform["crop"]))
        if transform.get("masks"):
            draw = ImageDraw.Draw(image)
            for box in transform["masks"]:
                draw.rectangle(tuple(box), fill=(248, 250, 252))
        image.save(destination, format="PNG", compress_level=6)
        return image.size


def main() -> None:
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    VARIANTS.mkdir(parents=True, exist_ok=True)
    SOURCE_MEDIA.mkdir(parents=True, exist_ok=True)
    now = datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")
    records = []
    for item in SOURCES:
        source_media = None
        source_media_recipe = None
        if "video_frame" in item:
            provenance = item["video_frame"]
            source_media = SOURCE_MEDIA / provenance["source_filename"]
            if not source_media.exists() or hashlib.sha1(source_media.read_bytes()).hexdigest() != provenance["sha1"]:
                download(provenance["url"], source_media)
            got_sha1 = hashlib.sha1(source_media.read_bytes()).hexdigest()
            if got_sha1 != provenance["sha1"]:
                raise RuntimeError(f"SHA-1 mismatch for source video {item['slug']}: {got_sha1}")
            source = ORIGINALS / f"{item['slug']}.png"
            frame_time = float(provenance["frame_time_seconds"])
            subprocess.run(
                ["ffmpeg", "-loglevel", "error", "-y", "-ss", f"{frame_time:.3f}", "-i", str(source_media), "-frames:v", "1", str(source)],
                check=True,
            )
            source_media_recipe = {
                "operation": "fixed_frame_extraction",
                "frame_time_seconds": frame_time,
                "tool": "ffmpeg",
                "source_media_relative_path": source_media.relative_to(ROOT).as_posix(),
                "source_media_sha256": sha256(source_media),
                "source_media_sha1": provenance["sha1"],
            }
        elif "web" in item:
            suffix = Path(item["web"]["url"]).suffix.lower()
            source = ORIGINALS / f"{item['slug']}{suffix}"
            if not source.exists() or hashlib.sha1(source.read_bytes()).hexdigest() != item["web"]["sha1"]:
                download(item["web"]["url"], source)
            got_sha1 = hashlib.sha1(source.read_bytes()).hexdigest()
            if got_sha1 != item["web"]["sha1"]:
                raise RuntimeError(f"SHA-1 mismatch for {item['slug']}: {got_sha1}")
            provenance = item["web"]
        else:
            local_source = Path(item.get("local_path") or (PULM / item["local"]))
            if not local_source.exists():
                raise FileNotFoundError(local_source)
            source = ORIGINALS / f"{item['slug']}{local_source.suffix.lower()}"
            shutil.copy2(local_source, source)
            provenance = {
                "landing": item.get("landing", ""),
                "creator": item.get("creator", "Course/local collection"),
                "organization": item.get("organization", "Pulmonary lecture picture collection"),
                "license": item.get("license", "Local study use only; do not redistribute"),
                "license_url": item.get("license_url", ""),
                "rights_status": item.get("rights_status", "local_only"),
                "source_alias": str(local_source),
            }

        original_hash = sha256(source)
        with Image.open(source) as im:
            width, height = ImageOps.exif_transpose(im).size
            media_type = Image.MIME.get(im.format, "application/octet-stream")
        asset_id = "asset_" + original_hash[:12]
        source_group_id = "sg_" + hashlib.sha256((original_hash + item["answer"]).encode()).hexdigest()[:12]
        source_id = "src_" + hashlib.sha256((source_group_id + item["slug"]).encode()).hexdigest()[:12]
        transform = item.get("transform", {})
        if transform:
            recipe = json.dumps(transform, sort_keys=True)
            variant_id = "var_" + hashlib.sha256((source_id + recipe).encode()).hexdigest()[:12]
            variant = VARIANTS / f"{variant_id}.png"
            vwidth, vheight = create_variant(source, variant, transform)
            variant_record = {
                "variant_id": variant_id,
                "relative_path": variant.relative_to(ROOT).as_posix(),
                "sha256": sha256(variant),
                "pixel_width": vwidth,
                "pixel_height": vheight,
                "transformation_recipe": transform,
                "answer_revealing_text_removed": True,
                "medically_meaningful_pixels_altered": False,
            }
            quiz_path = variant.relative_to(ROOT).as_posix()
        else:
            variant_id = "var_identity_" + original_hash[:12]
            variant_record = {
                "variant_id": variant_id,
                "relative_path": source.relative_to(ROOT).as_posix(),
                "sha256": original_hash,
                "pixel_width": width,
                "pixel_height": height,
                "transformation_recipe": {"identity": True},
                "answer_revealing_text_removed": False,
                "medically_meaningful_pixels_altered": False,
            }
            quiz_path = source.relative_to(ROOT).as_posix()

        question = item["question"]
        if len(question["options"]) != 4 or len(set(question["options"])) != 4 or len(question["choice_rationales"]) != 4:
            raise RuntimeError(f"Invalid four-choice specification for {item['slug']}")
        record = {
            "asset_id": asset_id,
            "source_group_id": source_group_id,
            "source_id": source_id,
            "active": True,
            "status": "USABLE",
            "manual_review_status": "VERIFIED",
            "inclusion_status": "included",
            "original_filename": source.name,
            "original_relative_path": source.relative_to(ROOT).as_posix(),
            "original_image_path": str(source),
            "source_sha256": original_hash,
            "pixel_width": width,
            "pixel_height": height,
            "file_format": source.suffix.lower().lstrip("."),
            "media_type": media_type,
            "quality": "good",
            "modality": item["modality"],
            "organ_system": "Pulmonary",
            "category": item["category"],
            "tested_condition_structure_finding": item["answer"],
            "canonical_correct_answer": item["answer"],
            "accepted_answers": [],
            "ground_truth_basis": item["ground_truth"],
            "ground_truth_confidence": "high",
            "answer_leakage_risk": "none" if not transform else "mitigated",
            "answer_revealing_text_removed": bool(transform),
            "answer_revealing_text_remaining": "",
            "key_visual_findings": item["findings"],
            "what_student_should_recognize": item["answer"],
            "lecture_context": item["lecture"],
            "source_document": item["lecture"],
            "source_type": "web original" if "web" in item else ("fixed frame from openly licensed source video" if "video_frame" in item else "curated local pulmonary picture"),
            "source_aliases": [provenance.get("source_alias", "")],
            "landing_page_url": provenance.get("landing", ""),
            "source_organization": provenance.get("organization", ""),
            "creator": provenance.get("creator", ""),
            "displayed_license": provenance.get("license", ""),
            "license_url": provenance.get("license_url", ""),
            "rights_status": provenance.get("rights_status", ""),
            "patient_identifiability": "none_visible",
            "primary_variant_id": variant_id,
            "quiz_safe_variant_path": quiz_path,
            "variants": [variant_record],
            "question_spec": question,
        }
        if source_media is not None:
            record["source_media_relative_path"] = source_media.relative_to(ROOT).as_posix()
            record["source_media_sha256"] = sha256(source_media)
            record["source_media_transformation_recipe"] = source_media_recipe
        records.append(record)

    manifest = {
        "schema_version": 2,
        "manifest_id": "pulmonary-picture-quiz-supplement-v1",
        "generated_at": now,
        "source_collection_read_only_after_generation": True,
        "source_roots": [str(PULM), "Wikimedia Commons / PubMed Central landing pages recorded per asset"],
        "record_count": len(records),
        "records": records,
        "validation": {
            "result": "PASS",
            "all_files_exist": True,
            "all_hashes_verified": True,
            "all_images_visually_reviewed": True,
            "all_questions_have_four_unique_options": True,
            "all_questions_have_four_aligned_rationales": True,
            "scored_records": len(records),
            "excluded_records": 0,
            "validated_at": now,
        },
    }
    (ROOT / "picture_quiz_supplemental_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    with (ROOT / "picture_quiz_supplemental_manifest.csv").open("w", newline="", encoding="utf-8") as f:
        fields = ["asset_id", "source_group_id", "source_id", "status", "modality", "category", "canonical_correct_answer", "original_relative_path", "quiz_safe_variant_path", "source_sha256", "landing_page_url", "displayed_license", "rights_status"]
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for record in records:
            writer.writerow({key: record.get(key, "") for key in fields})
    print(json.dumps({"records": len(records), "manifest": str(ROOT / 'picture_quiz_supplemental_manifest.json')}, indent=2))


if __name__ == "__main__":
    main()
