#!/usr/bin/env python3
"""Fail closed when a scored quiz item or learner-facing image is incomplete."""

from __future__ import annotations

import json
import re
from pathlib import Path

from PIL import Image


PROJECT = Path(__file__).resolve().parents[1]
BANK_PATH = PROJECT / "data" / "question-bank.json"
MANIFEST_PATH = PROJECT / "data" / "source-manifest.json"
ASSET_MAP_PATH = PROJECT / "data" / "asset-map.json"
ROOT_DATA_MIRRORS = ("question-bank.json", "source-manifest.json", "asset-map.json", "review-queue.json")
OPAQUE_ASSET = re.compile(r"^public/assets/images/(?:quiz|original)_[a-f0-9]{16}\.png$")
RETIRED_GENERIC_STEMS = {
    "Identify the pulmonary finding or diagnosis demonstrated in this image.",
    "Identify the tissue, organism, pathologic process, or diagnosis shown.",
    "Identify the structure, finding, or diagnosis demonstrated in this image.",
    "Identify the physiologic pattern or interpretation demonstrated by this visual.",
    "Identify the pulmonary finding, pattern, or procedure shown.",
}


def require(condition: bool, message: str, errors: list[str]) -> None:
    if not condition:
        errors.append(message)


def main() -> None:
    bank = json.loads(BANK_PATH.read_text(encoding="utf-8"))
    manifest = json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))
    asset_map = json.loads(ASSET_MAP_PATH.read_text(encoding="utf-8"))
    questions = bank.get("questions", [])
    sources = {record.get("source_id"): record for record in manifest.get("records", [])}
    errors: list[str] = []
    decoded: dict[str, tuple[int, int]] = {}

    require(bank.get("question_count") == len(questions), "question_count does not match the bank", errors)
    require(len({q.get("question_id") for q in questions}) == len(questions), "duplicate question_id detected", errors)
    for filename in ROOT_DATA_MIRRORS:
        root_copy = PROJECT / filename
        data_copy = PROJECT / "data" / filename
        require(root_copy.is_file(), f"missing root data mirror: {filename}", errors)
        require(data_copy.is_file(), f"missing canonical data file: data/{filename}", errors)
        if root_copy.is_file() and data_copy.is_file():
            require(root_copy.read_bytes() == data_copy.read_bytes(), f"root/data divergence: {filename}", errors)

    for question in questions:
        qid = question.get("question_id", "<missing-question-id>")
        options = question.get("options") or []
        rationales = question.get("choice_rationales") or []
        correct = question.get("correct_index")
        require(sources.get(question.get("source_id"), {}).get("status") == "USABLE", f"{qid}: unusable or missing source lineage", errors)
        require(len(options) == 4 and len({str(x).strip().casefold() for x in options}) == 4, f"{qid}: options are not four unique choices", errors)
        require(len(rationales) == 4 and all(str(x).strip() for x in rationales), f"{qid}: rationales are not four aligned explanations", errors)
        require(isinstance(correct, int) and 0 <= correct < 4, f"{qid}: invalid correct_index", errors)
        if isinstance(correct, int) and 0 <= correct < len(rationales):
            require(str(rationales[correct]).startswith("Correct:"), f"{qid}: keyed rationale is not marked Correct", errors)
        require(bool(str(question.get("stem", "")).strip()), f"{qid}: blank stem", errors)
        require(question.get("stem") not in RETIRED_GENERIC_STEMS, f"{qid}: retired generic stem", errors)
        require(bool(str(question.get("visual_target", "")).strip()), f"{qid}: missing visual target", errors)
        require(isinstance(question.get("joint_images"), bool), f"{qid}: joint_images must be boolean", errors)
        require(question.get("source_origin") in {"lecture", "third_party"}, f"{qid}: invalid source_origin", errors)
        require(sources.get(question.get("source_id"), {}).get("source_origin") == question.get("source_origin"), f"{qid}: source-origin lineage mismatch", errors)
        if question.get("joint_images"):
            scope_text = f"{question.get('stem', '')} {question.get('visual_target', '')}"
            require(bool(re.search(r"\b(together|both|joint|all displayed panels)\b", scope_text, re.I)), f"{qid}: jointly tested panels are not stated", errors)

        for field in ("quiz_asset", "original_asset"):
            relative = str(question.get(field, ""))
            require(bool(OPAQUE_ASSET.fullmatch(relative)), f"{qid}: {field} is not an opaque PNG path: {relative}", errors)
            path = (PROJECT / relative).resolve()
            require(path.is_relative_to(PROJECT.resolve()), f"{qid}: {field} escapes the project", errors)
            require(path.is_file(), f"{qid}: missing {field}: {relative}", errors)
            if path.is_file() and relative not in decoded:
                try:
                    with Image.open(path) as image:
                        image.verify()
                    with Image.open(path) as image:
                        decoded[relative] = image.size
                        require(image.format == "PNG", f"{qid}: {field} is not a decoded PNG", errors)
                        require(image.width > 0 and image.height > 0, f"{qid}: {field} has invalid dimensions", errors)
                except Exception as exc:  # pragma: no cover - only reached for corrupt build artifacts
                    errors.append(f"{qid}: unreadable {field} {relative}: {exc}")

        variant_id = question.get("variant_id")
        require(variant_id in asset_map, f"{qid}: variant_id missing from asset map", errors)
        if variant_id in asset_map:
            require(asset_map[variant_id].get("quiz", {}).get("path") == question.get("quiz_asset"), f"{qid}: quiz asset-map mismatch", errors)
            require(asset_map[variant_id].get("original", {}).get("path") == question.get("original_asset"), f"{qid}: original asset-map mismatch", errors)

    if errors:
        preview = "\n".join(f"- {error}" for error in errors[:80])
        suffix = f"\n- …and {len(errors) - 80} more" if len(errors) > 80 else ""
        raise SystemExit(f"Quiz-bank validation failed ({len(errors)} errors):\n{preview}{suffix}")

    print(json.dumps({
        "result": "PASS",
        "questions": len(questions),
        "unique_decoded_assets": len(decoded),
        "source_records": len(sources),
    }, indent=2))


if __name__ == "__main__":
    main()
