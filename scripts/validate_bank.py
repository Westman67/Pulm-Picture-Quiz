#!/usr/bin/env python3
"""Fail-closed validation for the rebuilt multi-collection pulmonary quiz."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import re
from pathlib import Path

from PIL import Image


PROJECT = Path(__file__).resolve().parents[1]
SOURCES = {
    "rename": Path.home() / "Desktop" / "Rename",
    "third_party": Path.home() / "Desktop" / "Add",
}
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg"}
OPAQUE_ASSET = {
    "quiz_asset": re.compile(r"^public/assets/images/quiz_[a-f0-9]{16}\.webp$"),
    "original_asset": re.compile(r"^public/assets/images/original_[a-f0-9]{16}\.png$"),
}
EXPECTED_FORMAT = {"quiz_asset": "WEBP", "original_asset": "PNG"}
BLOCKED = {"NEEDS_REVIEW", "REFERENCE_ONLY", "DUPLICATE", "AGGREGATE_DUPLICATE", "BROKEN", "EXCLUDED"}


def sha256_file(path: Path) -> str:
    hasher = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            hasher.update(chunk)
    return hasher.hexdigest()


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def check_explanation_quality(questions: list[dict], errors: list[str]) -> None:
    """Guard against duplicate/uncoordinated auto-generated answer explanations.

    This exists because two different failure modes were found and fixed by
    hand in a lecture-grounding pass: (1) two options in the *same* question
    resolving to byte-identical "why this is/isn't the answer" clue text
    (usually from a too-broad regex, or from two genuinely different
    diagnoses never having been distinguished), and (2) two concepts that
    share identical clue text and are NOT blocked from ever being offered as
    distractors together by CONCEPT_SYNONYM_GROUPS -- a "latent" version of
    the same bug that hasn't shown up yet only because of how the current
    question pool happens to be bucketed, and would surface the moment a new
    image or a distractor-selection change lets those two concepts land in
    the same question. Both are re-checked here on every validation run so a
    future edit to FEATURE_RULES or CONCEPT_SYNONYM_GROUPS in
    scripts/generate_rename_bank.py can't silently reintroduce either bug.
    """
    spec = importlib.util.spec_from_file_location(
        "generate_rename_bank", PROJECT / "scripts" / "generate_rename_bank.py"
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]

    def norm(concept: str) -> str:
        return re.sub(r"[^a-z0-9]+", " ", concept.casefold()).strip()

    def synonym_keys(concept: str) -> set[str]:
        n = norm(concept)
        keys = {n}
        for group in module.CONCEPT_SYNONYM_GROUPS:
            if n in group:
                keys.add(next(iter(sorted(group))))
        return keys

    concept_modality: dict[str, str] = {}

    for question in questions:
        qid = question.get("question_id", "<missing>")
        modality = question.get("modality") or question.get("family") or ""
        options = question.get("options") or []
        if len(options) != 4:
            continue
        clue_to_options: dict[str, list[str]] = {}
        for option in options:
            option = str(option)
            concept_modality.setdefault(option, modality)
            clue = module.feature_for(option, modality)
            clue_to_options.setdefault(clue, []).append(option)
        for clue, names in clue_to_options.items():
            require(
                len(names) == 1,
                f"{qid}: options {names} resolve to identical explanation clue text "
                f"({clue[:60]}...) -- add a distinguishing FEATURE_RULES entry or "
                f"check rule ordering (a broad rule listed earlier can shadow a more "
                f"specific one listed later)",
                errors,
            )

    clue_to_concepts: dict[str, set[str]] = {}
    for concept, modality in concept_modality.items():
        clue = module.feature_for(concept, modality)
        clue_to_concepts.setdefault(clue, set()).add(concept)

    for clue, concepts in clue_to_concepts.items():
        if len(concepts) < 2:
            continue
        ordered = sorted(concepts)
        keys = [synonym_keys(c) for c in ordered]
        for i in range(len(ordered)):
            for j in range(i + 1, len(ordered)):
                require(
                    bool(keys[i] & keys[j]),
                    f"latent duplicate clue: {ordered[i]!r} and {ordered[j]!r} share "
                    f"identical explanation text ({clue[:60]}...) but are not linked "
                    f"in CONCEPT_SYNONYM_GROUPS -- if they are the same finding, merge "
                    f"them there; if not, give one of them distinguishing text",
                    errors,
                )


def main() -> None:
    data = PROJECT / "data"
    bank = json.loads((data / "question-bank.json").read_text(encoding="utf-8"))
    manifest = json.loads((data / "source-manifest.json").read_text(encoding="utf-8"))
    asset_map = json.loads((data / "asset-map.json").read_text(encoding="utf-8"))
    review = json.loads((data / "review-queue.json").read_text(encoding="utf-8"))
    records = manifest.get("records", [])
    questions = bank.get("questions", [])
    sources = {record.get("source_id"): record for record in records}
    scored_ids = {question.get("source_id") for question in questions}
    errors: list[str] = []

    require(bank.get("schema_version") == 2, "question bank must use schema version 2", errors)
    require(manifest.get("schema_version") == 2, "source manifest must use schema version 2", errors)
    require(bank.get("question_count") == len(questions), "question_count does not match questions", errors)
    require(manifest.get("record_count") == len(records), "record_count does not match records", errors)
    require(review.get("count") == len(review.get("items", [])), "review queue count mismatch", errors)
    physical_sources = sum(
        1
        for root in SOURCES.values()
        for path in root.iterdir()
        if path.suffix.casefold() in IMAGE_EXTENSIONS
    )
    require(len(records) == physical_sources, "not every source image is represented in the manifest", errors)
    require(len({record.get("asset_id") for record in records}) == len(records), "duplicate asset IDs", errors)
    require(len({record.get("source_id") for record in records}) == len(records), "duplicate source IDs", errors)
    require(len({question.get("question_id") for question in questions}) == len(questions), "duplicate question IDs", errors)

    for filename in ("question-bank.json", "source-manifest.json", "asset-map.json", "review-queue.json"):
        require((PROJECT / filename).read_bytes() == (data / filename).read_bytes(), f"root/data divergence: {filename}", errors)

    for record in records:
        sid = record.get("source_id", "<missing>")
        collection_key = record.get("source_collection_key")
        source_root = SOURCES.get(collection_key)
        source = source_root / str(record.get("original_relative_path", "")) if source_root else Path("/__invalid_collection__")
        require(source_root is not None, f"{sid}: unknown collection key {collection_key}", errors)
        require(source.is_file(), f"{sid}: source file missing", errors)
        if source.is_file():
            require(sha256_file(source) == record.get("source_sha256"), f"{sid}: immutable source checksum changed", errors)
        require(record.get("source_origin") == "third_party", f"{sid}: invalid provenance category", errors)
        require(record.get("status") in {"USABLE", "NEEDS_REVIEW", "DUPLICATE"}, f"{sid}: invalid status", errors)
        require(bool(record.get("question_type_matrix")), f"{sid}: missing question type matrix", errors)
        variants = record.get("variants") or []
        require(len(variants) == 1, f"{sid}: expected one reproducible variant", errors)
        if record.get("status") in BLOCKED:
            require(sid not in scored_ids, f"{sid}: blocked source appears in scored bank", errors)

    decoded: set[str] = set()
    for question in questions:
        qid = question.get("question_id", "<missing>")
        source = sources.get(question.get("source_id"), {})
        options = question.get("options") or []
        rationales = question.get("choice_rationales") or []
        correct = question.get("correct_index")
        require(source.get("status") == "USABLE", f"{qid}: missing usable source lineage", errors)
        require(question.get("source_origin") == "third_party", f"{qid}: invalid source origin", errors)
        require(question.get("source_collection_key") in SOURCES, f"{qid}: invalid source collection", errors)
        require(source.get("source_collection_key") == question.get("source_collection_key"), f"{qid}: collection lineage mismatch", errors)
        require(len(options) == 4, f"{qid}: expected four options", errors)
        require(len({str(option).strip().casefold() for option in options}) == 4, f"{qid}: duplicate options", errors)
        require(len(rationales) == 4 and all(str(item).strip() for item in rationales), f"{qid}: invalid choice rationales", errors)
        require(isinstance(correct, int) and 0 <= correct < 4, f"{qid}: invalid correct index", errors)
        if isinstance(correct, int) and 0 <= correct < len(rationales):
            require(rationales[correct].startswith("Correct:"), f"{qid}: keyed rationale is not aligned", errors)
        require(bool(str(question.get("stem", "")).strip()), f"{qid}: missing stem", errors)
        require(bool(str(question.get("visual_target", "")).strip()), f"{qid}: missing visual target", errors)
        require(isinstance(question.get("joint_images"), bool), f"{qid}: joint_images must be boolean", errors)
        if question.get("joint_images"):
            require(bool(re.search(r"all displayed panels together|considering", f"{question.get('stem')} {question.get('visual_target')}", re.I)), f"{qid}: composite target is not explicit", errors)
        require(question.get("explanation") and question.get("visual_clues"), f"{qid}: missing image-grounded teaching text", errors)

        for field in ("quiz_asset", "original_asset"):
            relative = str(question.get(field, ""))
            require(bool(OPAQUE_ASSET[field].fullmatch(relative)), f"{qid}: nonopaque {field}: {relative}", errors)
            path = (PROJECT / relative).resolve()
            require(path.is_relative_to(PROJECT.resolve()), f"{qid}: {field} escapes project", errors)
            require(path.is_file(), f"{qid}: missing {field}", errors)
            if path.is_file() and relative not in decoded:
                try:
                    with Image.open(path) as image:
                        image.verify()
                    with Image.open(path) as image:
                        require(image.format == EXPECTED_FORMAT[field], f"{qid}: {field} is not {EXPECTED_FORMAT[field]}", errors)
                        require(image.width > 0 and image.height > 0, f"{qid}: invalid {field} dimensions", errors)
                    decoded.add(relative)
                except Exception as exc:
                    errors.append(f"{qid}: cannot decode {field}: {exc}")

        variant_id = question.get("variant_id")
        mapping = asset_map.get(variant_id, {})
        require(mapping.get("source_id") == question.get("source_id"), f"{qid}: broken asset lineage", errors)
        require(mapping.get("quiz", {}).get("path") == question.get("quiz_asset"), f"{qid}: quiz asset-map mismatch", errors)
        require(mapping.get("original", {}).get("path") == question.get("original_asset"), f"{qid}: original asset-map mismatch", errors)

    for item in review.get("items", []):
        require(item.get("project_status") == "NEEDS_REVIEW", "review item missing NEEDS_REVIEW status", errors)
        require(item.get("source_id") not in scored_ids, f"{item.get('source_id')}: review item is scored", errors)
        require((PROJECT / item.get("preview_asset", "")).is_file(), f"{item.get('source_id')}: missing review preview", errors)

    app_source = (PROJECT / "src" / "app.js").read_text(encoding="utf-8")
    require('alt="quiz source image"' in app_source, "learner image alt text is not neutral", errors)
    require('data-action="previous"' in app_source and 'data-action="next"' in app_source, "persistent Back/Next controls missing", errors)

    check_explanation_quality(questions, errors)

    if errors:
        preview = "\n".join(f"- {error}" for error in errors[:100])
        suffix = f"\n- …and {len(errors) - 100} more" if len(errors) > 100 else ""
        raise SystemExit(f"Quiz-bank validation failed ({len(errors)} errors):\n{preview}{suffix}")

    print(json.dumps({
        "result": "PASS",
        "source_records": len(records),
        "scored_questions": len(questions),
        "review_only": review.get("count"),
        "decoded_assets": len(decoded),
    }, indent=2))


if __name__ == "__main__":
    main()
