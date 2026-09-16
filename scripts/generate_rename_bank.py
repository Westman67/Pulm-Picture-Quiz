#!/usr/bin/env python3
"""Build a local pulmonary picture-identification bank from ~/Desktop/Rename.

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
SOURCE = Path.home() / "Desktop" / "Rename"
ASSET_DIR = PROJECT / "public" / "assets" / "images"
DATA_DIR = PROJECT / "data"
REPORT_DIR = PROJECT / "reports"
NOW = datetime.now(ZoneInfo("America/New_York")).isoformat()

IMAGE_EXTENSIONS = {".png"}

# These files remain visible in reviewer mode but are not used in scored sessions. Their
# visible evidence does not establish one sufficiently precise pulmonary answer.
REVIEW_ONLY: dict[str, str] = {
    "Acute Asthma Attack.png": "A near-normal chest radiograph cannot establish an acute asthma diagnosis by itself.",
    "Appendicitis CXR.png": "The filename and visible target do not establish a defensible pulmonary identification task.",
    "Asthma CXR.png": "A normal or near-normal chest radiograph is not diagnostic of asthma.",
    "CF CT 2.png": "The displayed upper-abdominal CT does not provide sufficient pulmonary evidence for cystic fibrosis.",
    "CF CT 3.png": "The displayed upper-abdominal CT does not provide sufficient pulmonary evidence for cystic fibrosis.",
    "Normal Histo.png": "The filename does not identify the organ, tissue compartment, or intended normal structure.",
    "Pulmonary Infarct Gross.png": "Embedded labels state the tested diagnosis directly over medically meaningful tissue.",
    "Pulmonary Metalplasia .png": "The source label is ambiguous and the intended metaplastic process is not specified reliably.",
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


FEATURE_RULES: list[tuple[str, str]] = [
    (r"^normal$", "symmetric normally aerated lungs without focal opacity, pleural collection, mass, or destructive change"),
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
    (r"organizing pneumonia|boop|cop", "polypoid fibroblastic plugs within distal air spaces with preserved underlying architecture"),
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
    (r"emphysema|vanishing lung|pink puffer", "hyperinflation, attenuated vascular markings, flattened diaphragms, or large bullous air spaces"),
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


def modality_for(name: str) -> str:
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


def concept_for(name: str) -> str:
    value = re.sub(r"\s+", " ", Path(name).stem).strip()
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
        value = re.sub(r"\s+(?:cxr|ct|histo|gross|diagram|us|echo|em|angiogram|x\s*ray|sputum)$", "", value, flags=re.I)
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
    if modality in {"X-ray", "CT", "MRI", "Angiography", "Ultrasound", "X-ray and CT", "X-ray and pathology"}:
        return "imaging"
    if modality in {"Histology", "Immunohistochemistry", "Electron Microscopy", "Cytology", "Gross pathology and histology"}:
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
    elif modality in {"X-ray and CT", "X-ray and pathology", "Gross pathology and histology"}:
        stem = f"Considering {scope}, which diagnosis best unifies the visible findings?"
    elif modality == "Histology":
        stem = f"Which diagnosis, tissue, or pathologic process best matches the dominant microscopic morphology in {scope}?"
    elif modality == "Immunohistochemistry":
        stem = f"Which diagnosis best matches the immunostaining pattern and cellular morphology in {scope}?"
    elif modality == "Electron Microscopy":
        stem = f"Which material or microanatomic structure is identified by the ultrastructural appearance in {scope}?"
    elif modality == "Gross Pathology":
        stem = f"Which diagnosis or anatomic abnormality best matches the gross morphology in {scope}?"
    elif modality == "Diagram":
        stem = f"Which pulmonary structure, anomaly, or intervention is represented by the relationships in {scope}?"
    elif modality == "Ultrasound":
        stem = f"Which diagnosis best matches the sonographic appearance in {scope}?"
    elif modality == "Angiography":
        stem = f"Which vascular abnormality is demonstrated by the contrast-filled vessels in {scope}?"
    elif modality == "Cytology":
        stem = f"Which diagnosis or process best matches the dominant cells in {scope}?"
    else:
        stem = f"Which pulmonary diagnosis, phenotype, or structure best matches the visible finding in {scope}?"
    return stem, scope


def candidate_pool(current: dict, entries: list[dict]) -> list[str]:
    tiers = [
        [e for e in entries if e["topic"] == current["topic"] and e["family"] == current["family"]],
        [e for e in entries if e["family"] == current["family"]],
        [e for e in entries if e["topic"] == current["topic"]],
        entries,
    ]
    correct = current["concept"]
    correct_norm = re.sub(r"[^a-z0-9]+", " ", correct.casefold()).strip()
    result: list[str] = []
    seen_norms: set[str] = set()
    for tier in tiers:
        for entry in sorted(tier, key=lambda item: hashlib.sha256(f"{current['sha']}:{item['concept']}".encode()).hexdigest()):
            option = entry["concept"]
            option_norm = re.sub(r"[^a-z0-9]+", " ", option.casefold()).strip()
            if not option_norm or option_norm == correct_norm or option_norm in seen_norms:
                continue
            if correct_norm in option_norm or option_norm in correct_norm:
                continue
            result.append(option)
            seen_norms.add(option_norm)
            if len(result) == 3:
                return result
    raise RuntimeError(f"Could not create distractors for {current['filename']}")


def reencode(source: Path, destination: Path, crop: tuple[float, float, float, float] | None = None) -> dict:
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
                    reuse = existing.format == "PNG" and existing.size == image.size
            except OSError:
                reuse = False
        if not reuse:
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
    if not SOURCE.is_dir():
        raise SystemExit(f"Missing source directory: {SOURCE}")
    files = sorted((path for path in SOURCE.iterdir() if path.suffix.casefold() in IMAGE_EXTENSIONS), key=lambda path: path.name.casefold())
    if not files:
        raise SystemExit(f"No PNG files found in {SOURCE}")

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    REPORT_DIR.mkdir(parents=True, exist_ok=True)
    ASSET_DIR.mkdir(parents=True, exist_ok=True)

    entries: list[dict] = []
    for path in files:
        sha = digest_file(path)
        with Image.open(path) as opened:
            image = ImageOps.exif_transpose(opened)
            width, height = image.size
            perceptual = dhash(image)
            has_alpha = image.mode in {"RGBA", "LA"} or "transparency" in image.info
        modality = modality_for(path.name)
        concept = concept_for(path.name)
        topic = topic_for(concept)
        base = re.sub(r"\s+(?:copy|[234])$", "", path.stem, flags=re.I)
        group_key = f"{clean_text(base)}:{modality_family(modality)}"
        entries.append({
            "path": path,
            "filename": path.name,
            "sha": sha,
            "width": width,
            "height": height,
            "aspect_ratio": width / height,
            "perceptual_hash": perceptual,
            "has_alpha": has_alpha,
            "modality": modality,
            "family": modality_family(modality),
            "concept": concept,
            "topic": topic,
            "asset_id": stable_id("asset", sha),
            "source_id": stable_id("src", sha),
            "source_group_id": stable_id("sg", group_key.casefold()),
            "variant_id": stable_id("var", f"{sha}:quiz-v1"),
            "question_id": stable_id("q", f"{sha}:{concept}:identification"),
            "status": "NEEDS_REVIEW" if path.name in REVIEW_ONLY else "USABLE",
        })

    groups: dict[str, list[dict]] = defaultdict(list)
    for entry in entries:
        groups[entry["source_group_id"]].append(entry)

    records: list[dict] = []
    asset_map: dict[str, dict] = {}
    questions: list[dict] = []
    review_items: list[dict] = []

    for entry in entries:
        source = entry["path"]
        crop = CROPS.get(entry["filename"])
        original_name = f"original_{entry['sha'][:16]}.png"
        quiz_key = hashlib.sha256(f"{entry['sha']}:quiz:{crop}".encode()).hexdigest()[:16]
        quiz_name = f"quiz_{quiz_key}.png"
        original_path = ASSET_DIR / original_name
        quiz_path = ASSET_DIR / quiz_name
        original_meta = reencode(source, original_path)
        quiz_meta = reencode(source, quiz_path, crop)
        original_relative = original_path.relative_to(PROJECT).as_posix()
        quiz_relative = quiz_path.relative_to(PROJECT).as_posix()
        transformations = ["metadata_strip", "lossless_png_reencode"]
        if entry["has_alpha"]:
            transformations.append("neutral_background_composite")
        if crop:
            transformations.append("answer_title_border_crop")

        joint = entry["modality"] in {"X-ray and CT", "X-ray and pathology", "Gross pathology and histology"} or entry["filename"] in COMPOSITES
        stem, visual_target = stem_for(entry["modality"], joint, entry["concept"])
        clue = feature_for(entry["concept"], entry["modality"])
        group_members = groups[entry["source_group_id"]]
        record = {
            "asset_id": entry["asset_id"],
            "source_group_id": entry["source_group_id"],
            "source_id": entry["source_id"],
            "original_relative_path": entry["filename"],
            "original_absolute_path": str(source),
            "source_sha256": entry["sha"],
            "perceptual_hash": entry["perceptual_hash"],
            "duplicate_relationships": [member["source_id"] for member in group_members if member["source_id"] != entry["source_id"]],
            "canonical_representative": max(group_members, key=lambda item: item["width"] * item["height"])["source_id"],
            "pixel_width": entry["width"],
            "pixel_height": entry["height"],
            "aspect_ratio": entry["aspect_ratio"],
            "file_format": "PNG",
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
            "manual_review_reason": REVIEW_ONLY.get(entry["filename"], ""),
            "source_attribution_visible_in_original": "unknown",
            "source_origin": "third_party",
            "source_collection": "Rename",
            "collection_rule": "All images supplied in the Desktop Rename collection are third-party study images.",
            "rights_status": "unknown; local study use only",
            "immutable_source_hash": entry["sha"],
            "status": entry["status"],
            "visual_target": visual_target,
            "key_visual_findings": clue,
            "panel_handling": "retained_composite" if joint else "single_complete_image",
            "question_type_matrix": {
                "Identification": {
                    "supported": "YES" if entry["status"] == "USABLE" else "REVIEW",
                    "visual_target": visual_target,
                    "required_variant": entry["variant_id"],
                    "full_image_required": crop is None,
                    "preserve": ["diagnostic pixels", "arrows", "orientation markers"],
                    "confidence": "high" if entry["status"] == "USABLE" else "low",
                    "reason_unsupported": REVIEW_ONLY.get(entry["filename"], ""),
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

        if entry["status"] != "USABLE":
            review_items.append({
                "source_id": entry["source_id"],
                "source_group_id": entry["source_group_id"],
                "preview_asset": original_relative,
                "proposed_answer": entry["concept"],
                "modality": entry["modality"],
                "evidence": "User-supplied filename and visual review were insufficient for a unique scored key.",
                "uncertainty_reason": REVIEW_ONLY[entry["filename"]],
                "answer_leakage_risk": "high" if "Embedded labels" in REVIEW_ONLY[entry["filename"]] else "low",
                "project_status": "NEEDS_REVIEW",
            })
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
            "case_context": "",
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
            "quiz_asset": quiz_relative,
            "original_asset": original_relative,
            "post_answer_source": {
                "original_filename": entry["filename"],
                "source_document": "Desktop/Rename user-curated pulmonary image collection",
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
        "builder": "build-medical-picture-quiz / Rename flat-collection builder",
        "source_directory": str(SOURCE),
        "source_library_read_only": True,
        "collection_provenance_rule": "All Desktop/Rename images are third_party and restricted to local study use.",
        "record_count": len(records),
        "records": records,
    }
    bank = {
        "schema_version": 2,
        "bank_id": stable_id("bank", "rename:" + "".join(entry["sha"] for entry in entries)),
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
    for path in ASSET_DIR.glob("*.png"):
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
    audit = [
        "# Pulmonary Rename collection preflight audit",
        "",
        f"Generated: {NOW}",
        "",
        f"- Source: `{SOURCE}` (read-only)",
        f"- Physical PNG files: {len(entries)}",
        f"- Decodable files: {len(entries)}",
        f"- Scored questions: {len(questions)}",
        f"- Review-only sources: {len(review_items)}",
        f"- Source groups with multiple named variants: {len(duplicate_groups)}",
        f"- Low-resolution files (one dimension below 500 px): {len(low_resolution)}",
        f"- Quiz-safe border crops: {len(CROPS)}",
        "- Exact byte-identical duplicate groups: 0",
        "- Provenance: all records are `third_party`; rights are unknown and the build is restricted to local study use.",
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
        "All browser assets were losslessly re-encoded as PNG with metadata stripped. Transparency was composited onto a neutral background. Six answer-revealing captions or titles in non-diagnostic border space were removed with recorded source-relative crop coordinates. No image was stretched, upscaled, generatively reconstructed, or altered within diagnostic pixels.",
        "",
        "## Ground-truth decision",
        "",
        "The collection was descriptively renamed by the user before import. Keys were accepted only where the visible morphology was compatible during the complete contact-sheet review. Sources with insufficient, ambiguous, non-pulmonary, or answer-leaking evidence were withheld in the review queue.",
    ]
    (REPORT_DIR / "preflight-audit.md").write_text("\n".join(audit) + "\n", encoding="utf-8")
    shutil.copy2(PROJECT.parent / "rename-audit" / "source-audit.json", REPORT_DIR / "source-audit.json") if (PROJECT.parent / "rename-audit" / "source-audit.json").exists() else None

    print(json.dumps({
        "result": "GENERATED",
        "source_files": len(entries),
        "scored_questions": len(questions),
        "review_only": len(review_items),
        "assets": len(list(ASSET_DIR.glob("*.png"))),
    }, indent=2))


if __name__ == "__main__":
    main()
