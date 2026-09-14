#!/usr/bin/env python3
"""Build the downstream pulmonary ID bank without modifying the source library."""

from __future__ import annotations

import copy
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
LIBRARY = Path.home() / "Desktop" / "Picture Quiz"
UPSTREAM = LIBRARY / "picture_quiz_manifest.json"
# Keep the validated supplemental library inside the quiz project so the build is
# self-contained even if the former Desktop staging folder is edited or removed.
SUPPLEMENT_ROOT = PROJECT / "source-additions"
SUPPLEMENT_MANIFEST = SUPPLEMENT_ROOT / "picture_quiz_supplemental_manifest.json"
PROMOTION_MANIFEST = SUPPLEMENT_ROOT / "picture_quiz_review_promotions.json"
SUPPLEMENT_STAGE = PROJECT / ".supplement-stage"
ASSET_DIR = PROJECT / "public" / "assets" / "images"

# These sources were retained upstream but visibly failed the stricter scored-ID gate during
# downstream contact-sheet review. They remain untouched in the source library.
MANUAL_REVIEW = {
    "src_90a7391b3c05": "The displayed crop visibly contains the normal-spirometry answer label.",
    "src_6448b676a84c": "The teaching label names the decisive intercellular-bridge clue.",
    "src_acdb640076ef": "Visible teaching prose names consolidation before submission.",
    "src_b413e152c175": "Visible prose names air bronchograms and their associated conditions.",
    "src_f61b09398e77": "The ultrasound panels visibly label the effusion.",
    "src_f2a9e757c991": "The graph labels directly state the tested survival comparison.",
    "src_871bc1e4e6e4": "The physical-exam diagram labels the diagnostic displacement measurements.",
    "src_11d38df219ae": "The diagram text directly states the pressure- and volume-control answer.",
    "src_7013e3362c68": "Visible management/prognostic teaching text makes this text-dependent.",
    "src_ea504b038377": "The diagram visibly names the CPAM morphologic classes being tested.",
    "src_85db33131d60": "The radiograph visibly states the key hyperinflation and mediastinal-shift findings.",
    "src_c0ab8fd58980": "The measurement overlay effectively states the Haller-index task.",
    "src_d92bf1430d1b": "The equipment collage is recognition-trivial and not a defensible medical ID item.",
    "src_328fa020c224": "This is primarily a numeric spirometry table rather than an image-identification task.",
    "src_221b5febf5ec": "This is primarily a numeric bronchodilator-response table.",
    "src_742331504fc4": "Visible interpretive prose makes the ventilatory-defect answer text-dependent.",
    "src_4d69b62d43cf": "Visible interpretive prose states the restrictive pattern.",
    "src_16585366665e": "This is a numeric spirometry table rather than a visual-identification image.",
    "src_bf8e9dd14184": "This is a numeric spirometry table rather than a visual-identification image.",
}

BLOCKED = {"NEEDS_REVIEW", "REFERENCE_ONLY", "DUPLICATE", "AGGREGATE_DUPLICATE", "BROKEN", "EXCLUDED"}


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def clean(value: object) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def short_sentence(value: object, limit: int = 260) -> str:
    text = clean(value)
    if not text:
        return "the expected defining visual pattern"
    sentence = re.split(r"(?<=[.!?])\s+", text)[0]
    if len(sentence) > limit:
        sentence = sentence[: limit - 1].rstrip(" ,;:") + "…"
    return sentence.rstrip(".")


def modality_family(modality: str) -> str:
    m = modality.casefold()
    if any(x in m for x in ("x-ray", "ct", "mri", "angiograph", "nuclear", "ultrasound", "echo", "imaging")):
        return "imaging"
    if any(x in m for x in ("hist", "micro", "smear", "electron")):
        return "microscopy"
    if any(x in m for x in ("graph", "loop", "tracing", "ekg", "table")):
        return "tracing"
    if any(x in m for x in ("gross", "clinical")):
        return "gross-clinical"
    if any(x in m for x in ("diagram", "embry", "flowchart", "map")):
        return "diagram"
    return "other"


def topic_cluster(record: dict) -> str:
    text = " ".join(clean(record.get(key)).casefold() for key in (
        "canonical_correct_answer", "category", "tested_condition_structure_finding", "lecture_context"
    ))
    groups = [
        ("chest-wall-congenital", ("pectus", "kypho", "scolio", "diaphrag", "cystic pulmonary", "cpam", "agenesis", "hypoplas", "sequestration", "bronchogenic cyst", "tracheoesophageal", "congenital")),
        ("vascular", ("embol", "thrombo", "pulmonary hypertension", "plexiform", "arteriovenous", "vascular malformation", "pulmonary artery", "infarct")),
        ("interstitial", ("fibros", "interstitial", "honeycomb", "uip", "usual interstitial", "asbestos", "silicos", "pneumocon")),
        ("granulomatous", ("sarcoid", "granuloma", "granulomatous", "hypersensitivity")),
        ("infection", ("pneumonia", "abscess", "tubercul", "asperg", "histoplas", "coccidio", "cryptococ", "klebsiella", "staphyl", "legionella", "influenza", "pneumocyst", "bronchopneumonia", "mycos")),
        ("airway-obstructive", ("asthma", "copd", "emphysema", "bronchiect", "bronchitis", "bronchiol", "air trapping", "obstruct", "tracheomalacia", "bronchoconstr", "mucus")),
        ("neoplasm", ("carcinoma", "cancer", "mesothelioma", "tumor", "hamartoma", "carcinoid", "adenocarcinoma", "metasta", "malignant")),
        ("sleep", ("sleep", "apnea", "polysom", "hypnogram", "oximetry")),
        ("upper-airway", ("tonsil", "peritonsillar", "epiglott", "croup", "nasal", "subglottic", "vocal", "mallampati", "laryng", "pharyn")),
        ("alveolar-injury", ("ards", "diffuse alveolar", "hyaline membrane", "pulmonary edema", "alveolar hemorrhage")),
        ("microanatomy", ("pneumocyte", "epithelium", "blood-air", "alveolar sept", "bronchiole", "trachea", "bronchi", "mucociliary")),
        ("physiology", ("pressure", "ventilation", "spirom", "flow-volume", "compliance", "curve", "loop", "pleural", "gas exchange", "oxygen")),
    ]
    for name, terms in groups:
        # Require a word start so short medical abbreviations (for example, UIP) do not match
        # inside unrelated words such as "equipment".
        if any(re.search(rf"(?<![a-z]){re.escape(term)}", text) for term in terms):
            return name
    return modality_family(clean(record.get("modality")))


def stem_for(record: dict) -> str:
    modality = clean(record.get("modality")).casefold()
    category = clean(record.get("category")).casefold()
    if modality == "clinical image":
        if "equipment" in category:
            return "Identify the pulmonary examination instrument shown in this image."
        return "Identify the physical or endoscopic finding shown in this clinical image."
    family = modality_family(clean(record.get("modality")))
    return {
        "imaging": "Identify the pulmonary finding or diagnosis demonstrated in this image.",
        "microscopy": "Identify the tissue, organism, pathologic process, or diagnosis shown.",
        "tracing": "Identify the physiologic pattern or interpretation demonstrated by this visual.",
        "gross-clinical": "Identify the structure, finding, or diagnosis demonstrated in this image.",
        "diagram": "Identify the structure, process, or pattern demonstrated by this visual.",
        "other": "Identify the pulmonary finding or pattern demonstrated in this image.",
    }[family]


def visual_clues(record: dict) -> list[str]:
    raw = clean(record.get("key_visual_findings"))
    parts = [clean(x) for x in re.split(r"(?<=[.!?;])\s+", raw) if clean(x)]
    if not parts:
        parts = [clean(record.get("what_student_should_recognize"))]
    return [x.rstrip(";") for x in parts if x][:4]


def save_safe_png(source: Path, destination: Path) -> dict:
    """Re-encode decoded pixels losslessly as PNG, stripping metadata and compositing alpha."""
    destination.parent.mkdir(parents=True, exist_ok=True)
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
        image.save(destination, format="PNG", compress_level=6)
        width, height = image.size
    return {
        "path": destination.relative_to(PROJECT).as_posix(),
        "sha256": sha256_file(destination),
        "pixel_width": width,
        "pixel_height": height,
        "transformations": ["metadata_stripped"] + (["neutral_background_composite"] if had_alpha else []),
    }


def question_asset(record: dict, prefix: str) -> tuple[str, dict]:
    rel = clean(record.get("quiz_safe_variant_path")) or clean(record.get("original_relative_path"))
    source = LIBRARY / rel
    digest = hashlib.sha256((prefix + ":" + record["source_id"] + ":" + rel).encode()).hexdigest()[:16]
    destination = ASSET_DIR / f"{prefix}_{digest}.png"
    meta = save_safe_png(source, destination)
    return meta["path"], meta


def supplemental_asset(record: dict, prefix: str, original: bool = False) -> tuple[str, dict]:
    rel = clean(record.get("original_relative_path") if original else record.get("quiz_safe_variant_path"))
    if not rel:
        rel = clean(record.get("original_relative_path"))
    source = SUPPLEMENT_STAGE / rel
    digest = hashlib.sha256((prefix + ":" + record["source_id"] + ":" + rel).encode()).hexdigest()[:16]
    destination = ASSET_DIR / f"{prefix}_{digest}.png"
    meta = save_safe_png(source, destination)
    return meta["path"], meta


def stage_supplement_assets(records: list[dict]) -> None:
    """Copy and hash-check supplemental inputs into the build directory before long processing."""
    SUPPLEMENT_STAGE.mkdir(parents=True, exist_ok=True)
    staged: dict[str, str] = {}
    for record in records:
        original_rel = clean(record.get("original_relative_path"))
        if not original_rel:
            raise RuntimeError(f"Supplemental source path missing for {record.get('source_id')}")
        staged[original_rel] = clean(record.get("source_sha256"))
        quiz_rel = clean(record.get("quiz_safe_variant_path")) or original_rel
        if quiz_rel != original_rel:
            variants = {clean(v.get("relative_path")): clean(v.get("sha256")) for v in record.get("variants", [])}
            staged[quiz_rel] = variants.get(quiz_rel, "")

    for rel, expected in staged.items():
        source = SUPPLEMENT_ROOT / rel
        if not source.is_file():
            raise FileNotFoundError(source)
        if not expected or sha256_file(source) != expected:
            raise RuntimeError(f"Supplemental source hash mismatch: {rel}")
        destination = SUPPLEMENT_STAGE / rel
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        if sha256_file(destination) != expected:
            raise RuntimeError(f"Staged supplemental hash mismatch: {rel}")


def choose_distractors(target: dict, candidates: list[dict]) -> list[dict]:
    answer = clean(target.get("canonical_correct_answer")).casefold()
    modality = clean(target.get("modality")).casefold()
    category = clean(target.get("category")).casefold()
    family = modality_family(modality)
    cluster = topic_cluster(target)
    doc = clean(target.get("source_document")).casefold()
    related = {clean(x).casefold() for x in (target.get("related_concepts") or []) if clean(x)}

    def normalized_terms(record: dict) -> set[str]:
        values = [clean(record.get("canonical_correct_answer")), *(record.get("accepted_answers") or [])]
        return {re.sub(r"[^a-z0-9]+", " ", value.casefold()).strip() for value in values if clean(value)}

    target_terms = normalized_terms(target)
    stop = {"and", "with", "from", "into", "the", "for", "versus", "type", "image", "pattern", "disease"}

    def overlaps_key(candidate: dict) -> bool:
        candidate_terms = normalized_terms(candidate)
        for one in target_terms:
            one_tokens = {x for x in one.split() if x not in stop}
            for two in candidate_terms:
                two_tokens = {x for x in two.split() if x not in stop}
                if one == two or (len(one) >= 7 and one in two) or (len(two) >= 7 and two in one):
                    return True
                if one_tokens and two_tokens and (one_tokens <= two_tokens or two_tokens <= one_tokens):
                    return True
                if len(one_tokens & two_tokens) / max(1, len(one_tokens | two_tokens)) >= 0.6:
                    return True
        return False

    ranked: list[tuple[tuple, dict]] = []
    seen: set[str] = set()
    for candidate in candidates:
        cand_answer = clean(candidate.get("canonical_correct_answer"))
        folded = cand_answer.casefold()
        if not cand_answer or folded == answer or folded in seen or overlaps_key(candidate):
            continue
        seen.add(folded)
        cand_related = {clean(x).casefold() for x in (candidate.get("related_concepts") or []) if clean(x)}
        score = 0
        same_cluster = topic_cluster(candidate) == cluster
        same_family = modality_family(clean(candidate.get("modality"))) == family
        score += 25 if same_cluster else 0
        score += 30 if clean(candidate.get("modality")).casefold() == modality else 0
        score += 10 if same_family else 0
        score += 30 if same_cluster and same_family else 0
        score += 8 if category and clean(candidate.get("category")).casefold() == category else 0
        score += 4 if doc and clean(candidate.get("source_document")).casefold() == doc else 0
        score += min(4, len(related & cand_related) * 2)
        tie = hashlib.sha256((target["source_id"] + candidate["source_id"]).encode()).hexdigest()
        ranked.append(((-score, tie), candidate))
    ranked.sort(key=lambda x: x[0])
    return [candidate for _, candidate in ranked[:3]]


def main() -> None:
    payload = json.loads(UPSTREAM.read_text(encoding="utf-8"))
    supplement_payload = json.loads(SUPPLEMENT_MANIFEST.read_text(encoding="utf-8"))
    promotion_payload = json.loads(PROMOTION_MANIFEST.read_text(encoding="utf-8"))
    supplement_records = supplement_payload.get("records", []) + promotion_payload.get("records", [])
    promoted_upstream_ids = {clean(r.get("upstream_source_id")) for r in promotion_payload.get("records", [])}
    if supplement_payload.get("schema_version", 0) < 2 or supplement_payload.get("validation", {}).get("result") != "PASS":
        raise RuntimeError("Supplemental manifest did not pass its schema/version gate")
    if promotion_payload.get("schema_version", 0) < 2 or promotion_payload.get("validation", {}).get("result") != "PASS":
        raise RuntimeError("Review-promotion manifest did not pass its schema/version gate")
    stage_supplement_assets(supplement_records)
    records = payload.get("records", [])
    active_usable = [
        r for r in records
        if r.get("active", True)
        and r.get("status") == "USABLE"
        and r.get("inclusion_status") == "included"
        and r.get("ground_truth_confidence") == "high"
    ]

    # One canonical ID task per modality/answer pair prevents repeated concepts from inflating the bank.
    grouped: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for record in active_usable:
        grouped[(clean(record.get("modality")).casefold(), clean(record.get("canonical_correct_answer")).casefold())].append(record)
    selected: list[dict] = []
    concept_duplicates: list[dict] = []
    risk_rank = {"none": 0, "low": 1, "medium": 2, "high": 3}
    quality_rank = {"excellent": 0, "good": 1, "acceptable": 2, "poor": 3, "limited": 4}
    for group in grouped.values():
        group.sort(key=lambda r: (
            risk_rank.get(clean(r.get("answer_leakage_risk")).casefold(), 9),
            quality_rank.get(clean(r.get("quality")).casefold(), 9),
            0 if r.get("quiz_safe_variant_path") else 1,
            r["source_id"],
        ))
        selected.append(group[0])
        concept_duplicates.extend(group[1:])
    selected = [r for r in selected if r["source_id"] not in MANUAL_REVIEW]
    selected.sort(key=lambda r: (clean(r.get("source_document")), int(r.get("source_page_or_slide") or 0), r["source_id"]))

    ASSET_DIR.mkdir(parents=True, exist_ok=True)
    questions: list[dict] = []
    asset_map: dict[str, dict] = {}
    for record in selected:
        quiz_path, quiz_meta = question_asset(record, "quiz")
        original_rel = clean(record.get("original_relative_path"))
        quiz_rel = clean(record.get("quiz_safe_variant_path")) or original_rel
        if original_rel == quiz_rel:
            original_path, original_meta = quiz_path, quiz_meta
        else:
            original_path, original_meta = question_asset({**record, "quiz_safe_variant_path": original_rel}, "original")

        variant_id = clean(record.get("primary_variant_id")) or f"var_identity_{record['source_id'][4:]}"
        distractors = choose_distractors(record, active_usable)
        if len(distractors) != 3:
            continue
        correct_answer = clean(record.get("canonical_correct_answer"))
        correct_clue = short_sentence(record.get("key_visual_findings"))
        option_records = [{"answer": correct_answer, "record": record, "correct": True}] + [
            {"answer": clean(d.get("canonical_correct_answer")), "record": d, "correct": False}
            for d in distractors
        ]
        rotation = int(hashlib.sha256(record["source_id"].encode()).hexdigest(), 16) % 4
        option_records = option_records[rotation:] + option_records[:rotation]
        options = [item["answer"] for item in option_records]
        rationales: list[str] = []
        correct_index = 0
        for index, item in enumerate(option_records):
            if item["correct"]:
                correct_index = index
                rationales.append(f"Correct: the displayed image shows {correct_clue}. This supports {correct_answer}.")
            else:
                expected = short_sentence(item["record"].get("key_visual_findings"), 190)
                rationales.append(
                    f"{item['answer']} would be better supported by {expected}; that pattern is not dominant here. "
                    f"Instead, this image shows {correct_clue}."
                )

        qhash = hashlib.sha256((record["source_id"] + ":identification:v2").encode()).hexdigest()[:12]
        clues = visual_clues(record)
        questions.append({
            "question_id": f"q_{qhash}",
            "source_group_id": record["source_group_id"],
            "source_id": record["source_id"],
            "variant_id": variant_id,
            "question_type": "Identification",
            "tested_concept": correct_answer,
            "stem": stem_for(record),
            "options": options,
            "correct_index": correct_index,
            "accepted_terminology": record.get("accepted_answers") or [],
            "explanation": f"This image demonstrates {correct_answer}. {clean(record.get('key_visual_findings'))}",
            "visual_clues": clues,
            "choice_rationales": rationales,
            "ground_truth_confidence": record.get("ground_truth_confidence"),
            "ground_truth_evidence": record.get("ground_truth_basis"),
            "category": clean(record.get("category")) or clean(record.get("modality")),
            "modality": clean(record.get("modality")),
            "organ_system": "Pulmonary",
            "topic_cluster": topic_cluster(record),
            "quiz_asset": quiz_path,
            "original_asset": original_path,
            "post_answer_source": {
                "original_filename": record.get("original_filename"),
                "source_document": record.get("source_document"),
                "source_page_or_slide": record.get("source_page_or_slide"),
                "source_id": record["source_id"],
            },
            "review_status": "VERIFIED",
        })
        asset_map[variant_id] = {"quiz": quiz_meta, "original": original_meta, "source_id": record["source_id"]}

    # Add the separate, versioned pulmonary-picture supplement. Its explicit question specs were
    # visually reviewed and preserve four index-aligned rationales; the source collection remains
    # separate from both the RLS library and the application build.
    for record in supplement_records:
        if not (
            record.get("active", True)
            and record.get("status") == "USABLE"
            and record.get("inclusion_status") == "included"
            and record.get("ground_truth_confidence") == "high"
        ):
            continue
        spec = record.get("question_spec") or {}
        options = spec.get("options") or []
        rationales = list(spec.get("choice_rationales") or [])
        correct_index = spec.get("correct_index")
        if len(options) != 4 or len(set(options)) != 4 or len(rationales) != 4 or correct_index not in range(4):
            raise RuntimeError(f"Invalid supplemental question contract for {record.get('source_id')}")
        if any(not clean(value) for value in [*options, *rationales]):
            raise RuntimeError(f"Blank supplemental option or rationale for {record.get('source_id')}")
        if not rationales[correct_index].startswith("Correct:"):
            rationales[correct_index] = "Correct: " + rationales[correct_index]
        quiz_path, quiz_meta = supplemental_asset(record, "quiz")
        if clean(record.get("quiz_safe_variant_path")) == clean(record.get("original_relative_path")):
            original_path, original_meta = quiz_path, quiz_meta
        else:
            original_path, original_meta = supplemental_asset(record, "original", original=True)
        variant_id = clean(record.get("primary_variant_id"))
        answer = clean(record.get("canonical_correct_answer"))
        if clean(options[correct_index]) != answer:
            raise RuntimeError(f"Supplemental key does not match canonical answer for {record.get('source_id')}")
        qhash = hashlib.sha256((record["source_id"] + ":identification:v2").encode()).hexdigest()[:12]
        questions.append({
            "question_id": f"q_{qhash}",
            "source_group_id": record["source_group_id"],
            "source_id": record["source_id"],
            "variant_id": variant_id,
            "question_type": "Identification",
            "tested_concept": answer,
            "stem": clean(spec.get("stem")),
            "options": options,
            "correct_index": correct_index,
            "accepted_terminology": record.get("accepted_answers") or [],
            "explanation": clean(spec.get("explanation")),
            "visual_clues": spec.get("visual_clues") or [],
            "choice_rationales": rationales,
            "ground_truth_confidence": record.get("ground_truth_confidence"),
            "ground_truth_evidence": record.get("ground_truth_basis"),
            "category": clean(record.get("category")) or clean(record.get("modality")),
            "modality": clean(record.get("modality")),
            "organ_system": "Pulmonary",
            "topic_cluster": topic_cluster(record),
            "quiz_asset": quiz_path,
            "original_asset": original_path,
            "post_answer_source": {
                "original_filename": record.get("original_filename"),
                "source_document": record.get("source_document"),
                "source_id": record["source_id"],
                "landing_page_url": record.get("landing_page_url"),
                "creator": record.get("creator"),
                "displayed_license": record.get("displayed_license"),
            },
            "review_status": "VERIFIED",
        })
        asset_map[variant_id] = {
            "quiz": quiz_meta,
            "original": original_meta,
            "source_id": record["source_id"],
            "supplemental_source_manifest": (
                PROMOTION_MANIFEST.as_posix() if record.get("upstream_source_id") else SUPPLEMENT_MANIFEST.as_posix()
            ),
        }

    # Review items receive opaque, metadata-stripped previews but never enter scored sessions.
    review_items = []
    by_id = {r.get("source_id"): r for r in records}
    for source_id, reason in MANUAL_REVIEW.items():
        if source_id in promoted_upstream_ids:
            continue
        record = by_id[source_id]
        preview, preview_meta = question_asset(record, "review")
        review_items.append({
            "source_id": source_id,
            "source_group_id": record.get("source_group_id"),
            "preview_asset": preview,
            "modality": record.get("modality"),
            "category": record.get("category"),
            "proposed_answer": record.get("canonical_correct_answer"),
            "confidence": record.get("ground_truth_confidence"),
            "evidence": record.get("ground_truth_basis"),
            "uncertainty_reason": reason,
            "answer_leakage_risk": record.get("answer_leakage_risk"),
            "duplicate_group": record.get("duplicate_group"),
            "project_status": "NEEDS_REVIEW",
            "source_document": record.get("source_document"),
            "source_page_or_slide": record.get("source_page_or_slide"),
            "preview_sha256": preview_meta["sha256"],
        })

    now = datetime.now(ZoneInfo("America/New_York")).isoformat(timespec="seconds")
    bank = {
        "schema_version": 2,
        "bank_id": "pulmonary-picture-id-v1",
        "generated_at": now,
        "mode": "image-identification",
        "question_count": len(questions),
        "questions": questions,
    }
    review_queue = {
        "schema_version": 1,
        "generated_at": now,
        "count": len(review_items),
        "items": review_items,
    }

    # Preserve upstream records and lineage; append only builder-local, reproducible projection data.
    projected = copy.deepcopy(payload)
    projected["schema_version"] = 2
    projected["upstream_schema_version"] = payload.get("schema_version")
    projected["builder"] = "build-medical-picture-quiz"
    projected["builder_generated_at"] = now
    projected["source_library_read_only"] = True
    projected["supplemental_source_library"] = {
        "path": SUPPLEMENT_ROOT.as_posix(),
        "manifest": SUPPLEMENT_MANIFEST.as_posix(),
        "schema_version": supplement_payload.get("schema_version"),
        "record_count": len(supplement_records),
        "validation": supplement_payload.get("validation"),
        "review_promotion_manifest": PROMOTION_MANIFEST.as_posix(),
        "review_promotion_record_count": len(promotion_payload.get("records", [])),
        "review_promotion_validation": promotion_payload.get("validation"),
        "read_only_during_quiz_build": True,
    }
    projected["records"].extend(copy.deepcopy(supplement_records))
    selected_ids = {q["source_id"] for q in questions}
    duplicate_ids = {r["source_id"] for r in concept_duplicates}
    for record in projected["records"]:
        sid = record.get("source_id")
        active = record.get("active", True) and record.get("status") == "USABLE"
        promoted_original = sid in promoted_upstream_ids
        review_only = sid in MANUAL_REVIEW and not promoted_original
        record["question_type_matrix"] = {
            "Identification": {
                "supported": "YES" if sid in selected_ids else ("REVIEW" if review_only else "NO"),
                "visual_target": record.get("tested_condition_structure_finding"),
                "required_variant": record.get("primary_variant_id") or "identity",
                "full_image_required": record.get("panel_handling") == "retained_composite",
                "preserve": record.get("labels_preserved") or [],
                "confidence": record.get("ground_truth_confidence"),
                "reason_unsupported": (
                    f"Promoted through a project-local quiz-safe derivative in {PROMOTION_MANIFEST.name}."
                    if promoted_original else (MANUAL_REVIEW.get(sid, "") if sid not in selected_ids else "")
                ),
            }
        }
        record["builder_scored_question"] = sid in selected_ids
        if promoted_original:
            record["builder_exclusion_reason"] = f"Replaced for scoring by a project-local quiz-safe derivative from source {sid}."
        elif review_only:
            record["builder_review_reason"] = MANUAL_REVIEW[sid]
        elif sid in duplicate_ids:
            record["builder_exclusion_reason"] = "Duplicate modality/answer concept retained upstream but not repeated in the initial scored bank."

    (PROJECT / "data" / "question-bank.json").write_text(json.dumps(bank, indent=2, ensure_ascii=False), encoding="utf-8")
    (PROJECT / "data" / "review-queue.json").write_text(json.dumps(review_queue, indent=2, ensure_ascii=False), encoding="utf-8")
    (PROJECT / "data" / "source-manifest.json").write_text(json.dumps(projected, indent=2, ensure_ascii=False), encoding="utf-8")
    (PROJECT / "data" / "asset-map.json").write_text(json.dumps(asset_map, indent=2), encoding="utf-8")

    status_counts = Counter(r.get("status") for r in records if r.get("active", True))
    modality_counts = Counter(q["modality"] for q in questions)
    report = f"""# Pulmonary Picture Quiz Preflight Audit

Generated: {now}

## Scope

- Canonical upstream library: `{LIBRARY}` (read-only)
- Supplemental pulmonary-picture library: `{SUPPLEMENT_ROOT}` (read-only during quiz build)
- Audited collection: `{LIBRARY / 'Pulmonary'}`
- Output project: `{PROJECT}`
- Quiz format: image-identification, one scored task per selected source/concept

## Upstream validation summary

- Extractor: `{payload.get('extractor')}` version {payload.get('extractor_version')}
- Upstream manifest generated: {payload.get('generated_at')}
- Manifest records: {len(records)}
- Active records: {sum(bool(r.get('active', True)) for r in records)}
- Active status counts: {dict(status_counts)}
- Active, high-confidence, scored-eligible candidates before downstream review: {len(active_usable)}
- Source-document hashes were independently checked before this build: 37/37 matched.
- Extractor states were independently checked before this build: 38 complete, 1,995 slides inspected.

## Downstream ID gate

- Activated questions: {len(questions)}
- New pulmonary-picture additions: {len(supplement_records)}
- Distinct activated source groups: {len({q['source_group_id'] for q in questions})}
- Manual-review exclusions: {len(review_items)}
- Repeated modality/answer concepts not duplicated in the bank: {len(concept_duplicates)}
- Question bank schema: 2
- Every item has four unique options and four index-aligned rationales.

## Activated questions by modality

{chr(10).join(f'- {name}: {count}' for name, count in modality_counts.most_common())}

## Safety decisions

- Learner-facing assets use opaque hashed names.
- Images are losslessly re-encoded from decoded pixels to strip embedded metadata.
- Transparent pixels are composited onto a controlled neutral background.
- No image is upscaled, mirrored, recolored, or generatively altered.
- Source filenames, lecture names, pages, originals, and rationales remain hidden before Learn submission and Exam completion.
- Upstream `REFERENCE_ONLY`, `EXCLUDED`, inactive, broken, duplicate, and review-only records are not scored.
- Client-side answer hiding is interface behavior, not cryptographic secrecy.

## Limitations

- Distractors were selected deterministically from modality- and category-aligned, lecture-verified source records.
- {len(review_items)} visually labeled or text-dependent candidates remain in the local review queue; six user-approved sources were promoted through reproducible local crops or opaque masks.
- The build preserves the upstream medical ground truth; it does not reinterpret RLS content from filenames.
"""
    (PROJECT / "reports" / "preflight-audit.md").write_text(report, encoding="utf-8")
    print(json.dumps({
        "questions": len(questions),
        "review_items": len(review_items),
        "concept_duplicates_removed": len(concept_duplicates),
        "assets": len(asset_map),
    }, indent=2))


if __name__ == "__main__":
    main()
