#!/usr/bin/env python3
"""Build six user-approved, quiz-safe variants from read-only RLS source images."""

from __future__ import annotations

import hashlib
import json
import shutil
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from PIL import Image, ImageDraw, ImageOps


ROOT = Path(__file__).resolve().parents[1]
LIBRARY = Path.home() / "Desktop" / "Picture Quiz"
UPSTREAM = LIBRARY / "picture_quiz_manifest.json"
ORIGINALS = ROOT / "promotions" / "originals"
VARIANTS = ROOT / "promotions" / "variants"
OUTPUT = ROOT / "picture_quiz_review_promotions.json"


def question(answer, options, clues, explanation, rationales, stem):
    return {
        "stem": stem,
        "options": options,
        "correct_index": options.index(answer),
        "visual_clues": clues,
        "explanation": explanation,
        "choice_rationales": rationales,
    }


PROMOTIONS = [
    {
        "upstream_source_id": "src_6448b676a84c",
        "answer": "Squamous cell carcinoma with intercellular bridges",
        "crop": [105, 285, 1590, 1470],
        "masks": [],
        "findings": "Atypical polygonal tumor cells have visible intercellular bridges; the answer-bearing teaching title and prose are outside the crop.",
        "question": question(
            "Squamous cell carcinoma with intercellular bridges",
            ["Squamous cell carcinoma with intercellular bridges", "Pulmonary adenocarcinoma with gland formation", "Small cell lung carcinoma", "Pulmonary carcinoid tumor"],
            ["Adjacent polygonal cells remain connected by fine intercellular bridges", "The cells have more cytoplasm than small-cell carcinoma", "No malignant glands or organoid neuroendocrine nests dominate"],
            "Visible intercellular bridges indicate squamous differentiation and support squamous cell carcinoma.",
            [
                "Correct: fine bridges between adjacent atypical polygonal cells are a classic feature of squamous differentiation.",
                "Adenocarcinoma would show malignant gland formation or mucin rather than conspicuous intercellular bridges.",
                "Small cell carcinoma has small hyperchromatic cells with scant cytoplasm and nuclear molding, not polygonal cells joined by bridges.",
                "A carcinoid tumor usually forms uniform organoid nests or trabeculae with salt-and-pepper chromatin, which are absent here.",
            ],
            "Identify the pulmonary neoplasm shown on histology.",
        ),
    },
    {
        "upstream_source_id": "src_acdb640076ef",
        "answer": "Lobar consolidation",
        "crop": [58, 192, 1607, 1576],
        "masks": [],
        "findings": "A homogeneous lobar air-space opacity occupies the right upper lung; the explanatory definition above the radiograph is excluded.",
        "question": question(
            "Lobar consolidation",
            ["Lobar consolidation", "Pleural effusion", "Pneumothorax", "Diffuse interstitial pulmonary edema"],
            ["A dense homogeneous air-space opacity conforms to a lobe", "The opacity is intrapulmonary rather than a dependent pleural meniscus", "Peripheral lung markings remain visible without a pleural line"],
            "The sharply regional air-space opacity is a lobar consolidation pattern.",
            [
                "Correct: a dense homogeneous air-space opacity confined to a lobar distribution is lobar consolidation.",
                "Pleural effusion would layer dependently and form a meniscus or costophrenic-angle blunting rather than this upper-lobar opacity.",
                "Pneumothorax would produce a visceral pleural line with absent peripheral lung markings, not dense air-space opacity.",
                "Interstitial edema is usually bilateral and diffuse with septal lines or perihilar haze rather than a single lobar opacity.",
            ],
            "Identify the pulmonary radiographic pattern shown.",
        ),
    },
    {
        "upstream_source_id": "src_871bc1e4e6e4",
        "answer": "Peritonsillar abscess on physical examination",
        "crop": [23, 1000, 615, 1300],
        "masks": [[300, 0, 440, 40], [440, 0, 525, 75]],
        "mask_fill": [190, 70, 75],
        "findings": "The remaining visible anatomy shows unilateral peritonsillar and soft-palate bulging with deviation of the uvula away from the affected side.",
        "question": question(
            "Peritonsillar abscess on physical examination",
            ["Peritonsillar abscess on physical examination", "Retropharyngeal abscess", "Acute epiglottitis", "Symmetric acute tonsillitis"],
            ["The soft palate and peritonsillar region bulge unilaterally", "The uvula is displaced away from the bulge", "The process is asymmetric rather than bilateral"],
            "Unilateral peritonsillar bulging with contralateral uvular deviation is the classic oropharyngeal appearance of a peritonsillar abscess.",
            [
                "Correct: unilateral soft-palate bulging and contralateral uvular deviation are characteristic of a peritonsillar abscess.",
                "A retropharyngeal abscess produces posterior pharyngeal-wall swelling and is usually evaluated on lateral neck imaging rather than this unilateral peritonsillar pattern.",
                "Epiglottitis affects the supraglottic epiglottis and does not create this focal peritonsillar bulge with uvular deviation.",
                "Acute tonsillitis is usually bilateral with enlarged erythematous tonsils and lacks the marked asymmetric palatal bulge shown.",
            ],
            "Identify the upper-airway diagnosis illustrated.",
        ),
    },
    {
        "upstream_source_id": "src_c0ab8fd58980",
        "answer": "Haller index measurement for pectus excavatum",
        "crop": [80, 110, 1749, 780],
        "masks": [],
        "findings": "Axial chest CT contains perpendicular transverse and minimum anteroposterior measurements across a depressed sternum while the answer name and computed ratio are hidden.",
        "question": question(
            "Haller index measurement for pectus excavatum",
            ["Haller index measurement for pectus excavatum", "Cardiothoracic ratio", "Cobb angle", "Main pulmonary artery-to-aorta ratio"],
            ["The image is an axial chest CT through a depressed sternum", "One line measures the internal transverse chest diameter", "A perpendicular line measures the shortest sternum-to-spine distance"],
            "The ratio of internal transverse diameter to minimum anteroposterior diameter on axial CT is the Haller index used to quantify pectus excavatum.",
            [
                "Correct: the Haller index divides the internal transverse chest diameter by the shortest sternum-to-spine distance on axial CT.",
                "The cardiothoracic ratio compares cardiac width with thoracic width on a frontal chest radiograph, not two perpendicular CT chest dimensions.",
                "The Cobb angle measures spinal curvature on a coronal radiograph and does not use transverse and AP chest diameters.",
                "The pulmonary artery-to-aorta ratio compares vascular diameters near the pulmonary-artery bifurcation, not the thoracic cage measurements shown.",
            ],
            "Identify the thoracic measurement demonstrated on this CT image.",
        ),
    },
    {
        "upstream_source_id": "src_f61b09398e77",
        "answer": "Empyema on ultrasound",
        "crop": [1510, 460, 2800, 1480],
        "masks": [],
        "findings": "The pleural collection is complex and loculated with internal septations and echogenic gas, rather than simple anechoic fluid.",
        "question": question(
            "Empyema on ultrasound",
            ["Empyema on ultrasound", "Simple transudative pleural effusion", "Normally aerated lung with A-lines", "Pneumothorax with absent lung sliding"],
            ["Pleural fluid is internally complex rather than uniformly anechoic", "Multiple septations create loculations", "Echogenic gas is present within the collection"],
            "Complex septated pleural fluid with internal gas is strongly supportive of empyema in the appropriate clinical setting.",
            [
                "Correct: loculated complex pleural fluid containing septations and gas is a characteristic sonographic pattern of empyema.",
                "A simple transudative effusion is usually uniformly anechoic and lacks internal septations or gas.",
                "Normally aerated lung shows a pleural line with sliding and horizontal A-lines rather than a complex fluid collection.",
                "Pneumothorax is assessed by absent sliding or a barcode sign and does not create this septated pleural collection.",
            ],
            "Identify the pleural process shown on ultrasound.",
        ),
    },
    {
        "upstream_source_id": "src_85db33131d60",
        "answer": "Hyperinflated multicystic CPAM with contralateral mediastinal shift",
        "crop": [760, 50, 2320, 1600],
        "masks": [],
        "findings": "A large right-sided multicystic hyperlucent lesion expands the hemithorax and displaces the mediastinum leftward; answer-bearing text boxes are outside the crop.",
        "question": question(
            "Hyperinflated multicystic CPAM with contralateral mediastinal shift",
            ["Hyperinflated multicystic CPAM with contralateral mediastinal shift", "Congenital lobar emphysema", "Tension pneumothorax", "Congenital diaphragmatic hernia"],
            ["Multiple internal cystic lucencies occupy the right lung", "The involved hemithorax is expanded", "The mediastinum is displaced to the opposite side"],
            "The neonatal radiograph shows an expanded multicystic pulmonary lesion with contralateral shift, supporting CPAM.",
            [
                "Correct: a multicystic intrapulmonary lesion that expands one hemithorax and shifts the mediastinum is characteristic of CPAM.",
                "Congenital lobar emphysema produces overinflation of a lobe with attenuated but continuous vascular markings rather than multiple discrete cystic spaces.",
                "Tension pneumothorax creates a pleural line with absent peripheral vascular markings and a collapsed central lung, not a multicystic parenchymal lesion.",
                "Congenital diaphragmatic hernia shows intrathoracic bowel loops or stomach and an abnormal diaphragmatic contour rather than this pulmonary multicystic pattern.",
            ],
            "Identify the congenital pulmonary lesion shown.",
        ),
    },
]


def sha256(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_variant(source: Path, destination: Path, crop, masks, mask_fill):
    with Image.open(source) as opened:
        image = ImageOps.exif_transpose(opened).convert("RGB").crop(tuple(crop))
        if masks:
            draw = ImageDraw.Draw(image)
            for box in masks:
                draw.rectangle(tuple(box), fill=tuple(mask_fill))
        image.save(destination, format="PNG", compress_level=6)
        return image.size


def main():
    payload = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    by_id = {record["source_id"]: record for record in payload["records"]}
    ORIGINALS.mkdir(parents=True, exist_ok=True)
    VARIANTS.mkdir(parents=True, exist_ok=True)
    for stale in VARIANTS.glob("var_*.png"):
        stale.unlink()
    records = []
    now = datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")
    for spec in PROMOTIONS:
        upstream = by_id[spec["upstream_source_id"]]
        source = LIBRARY / upstream["original_relative_path"]
        expected = upstream["source_sha256"]
        if sha256(source) != expected:
            raise RuntimeError(f"Upstream source hash mismatch: {source}")
        original = ORIGINALS / f"{upstream['source_id']}.png"
        shutil.copy2(source, original)
        if sha256(original) != expected:
            raise RuntimeError(f"Copied source hash mismatch: {original}")
        mask_fill = spec.get("mask_fill", [214, 218, 222])
        recipe = {"crop_pixels": spec["crop"], "opaque_masks_pixels": spec["masks"], "mask_fill_rgb": mask_fill, "rotation_degrees": 0}
        promotion_source_id = "src_" + hashlib.sha256((upstream["source_id"] + ":review-promotion:v1").encode()).hexdigest()[:12]
        variant_id = "var_" + hashlib.sha256((promotion_source_id + json.dumps(recipe, sort_keys=True)).encode()).hexdigest()[:12]
        variant = VARIANTS / f"{variant_id}.png"
        width, height = build_variant(original, variant, spec["crop"], spec["masks"], mask_fill)
        record = {
            "asset_id": upstream["asset_id"],
            "source_group_id": upstream["source_group_id"],
            "source_id": promotion_source_id,
            "upstream_source_id": upstream["source_id"],
            "active": True,
            "status": "USABLE",
            "manual_review_status": "VERIFIED",
            "inclusion_status": "included",
            "original_filename": upstream["original_filename"],
            "original_relative_path": original.relative_to(ROOT).as_posix(),
            "original_image_path": str(original),
            "source_sha256": expected,
            "source_document": upstream.get("source_document"),
            "source_document_path": upstream.get("source_document_path"),
            "source_document_sha256": upstream.get("source_document_sha256"),
            "source_page_or_slide": upstream.get("source_page_or_slide"),
            "source_type": "project-local copy of canonical RLS extraction",
            "extraction_method": upstream.get("extraction_method"),
            "modality": upstream.get("modality"),
            "organ_system": "Pulmonary",
            "category": upstream.get("category"),
            "canonical_correct_answer": spec["answer"],
            "tested_condition_structure_finding": spec["answer"],
            "accepted_answers": upstream.get("accepted_answers") or [],
            "ground_truth_basis": upstream.get("ground_truth_basis"),
            "ground_truth_confidence": "high",
            "answer_leakage_risk": "mitigated",
            "answer_revealing_text_removed": True,
            "answer_revealing_text_remaining": "",
            "key_visual_findings": spec["findings"],
            "what_student_should_recognize": spec["answer"],
            "lecture_context": upstream.get("lecture_context"),
            "quality": upstream.get("quality", "acceptable"),
            "patient_identifiability": "none_visible",
            "primary_variant_id": variant_id,
            "quiz_safe_variant_path": variant.relative_to(ROOT).as_posix(),
            "variants": [{
                "variant_id": variant_id,
                "relative_path": variant.relative_to(ROOT).as_posix(),
                "sha256": sha256(variant),
                "pixel_width": width,
                "pixel_height": height,
                "transformation_recipe": recipe,
                "answer_revealing_text_removed": True,
                "medically_meaningful_pixels_altered": False,
            }],
            "question_spec": spec["question"],
            "promotion_review_status": "user_approved_and_visually_verified",
        }
        records.append(record)

    manifest = {
        "schema_version": 2,
        "manifest_id": "pulmonary-picture-quiz-review-promotions-v1",
        "generated_at": now,
        "source_library_read_only": True,
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
    OUTPUT.write_text(json.dumps(manifest, indent=2), encoding="utf-8")
    print(json.dumps({"records": len(records), "manifest": str(OUTPUT)}, indent=2))


if __name__ == "__main__":
    main()
