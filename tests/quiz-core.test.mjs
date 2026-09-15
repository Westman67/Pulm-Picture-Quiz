import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import {
  PROGRESS_SCHEMA_VERSION,
  QUALITY_FLAGS_SCHEMA_VERSION,
  applyAnswerToProgress,
  createSession,
  emptyQualityFlags,
  emptyProgress,
  lockAnswer,
  normalizeQualityFlags,
  normalizeProgress,
  prepareQuestion,
  reconcileQualityFlags,
  rationaleVisible,
  scoreAnswers,
  setQualityFlagStatus,
  toggleMarked,
  upsertQualityFlag,
} from "../src/quiz-core.mjs";

const project = new URL("../", import.meta.url);
const bank = JSON.parse(await readFile(new URL("data/question-bank.json", project), "utf8"));
const manifest = JSON.parse(await readFile(new URL("data/source-manifest.json", project), "utf8"));
const review = JSON.parse(await readFile(new URL("data/review-queue.json", project), "utf8"));
const questions = bank.questions;

test("new bank uses schema version 2 and valid source lineage", () => {
  assert.equal(bank.schema_version, 2);
  assert.equal(bank.question_count, questions.length);
  assert.ok(questions.length >= 100);
  const sources = new Map(manifest.records.map((record) => [record.source_id, record]));
  for (const question of questions) {
    assert.equal(sources.get(question.source_id)?.status, "USABLE");
    assert.equal(sources.get(question.source_id)?.source_origin, question.source_origin);
    assert.ok(["lecture", "third_party"].includes(question.source_origin));
    assert.ok(question.source_group_id);
    assert.ok(question.variant_id);
  }
});

test("every question has four unique options and four nonempty aligned rationales", () => {
  for (const question of questions) {
    assert.ok(question.stem?.trim(), question.question_id);
    assert.ok(question.visual_target?.trim(), question.question_id);
    assert.equal(typeof question.joint_images, "boolean", question.question_id);
    assert.equal(question.options.length, 4, question.question_id);
    assert.equal(new Set(question.options.map((x) => x.trim().toLowerCase())).size, 4, question.question_id);
    assert.equal(question.choice_rationales.length, 4, question.question_id);
    assert.ok(question.choice_rationales.every((x) => typeof x === "string" && x.trim()), question.question_id);
    assert.match(question.choice_rationales[question.correct_index], /^Correct:/, question.question_id);
  }
});

test("stems identify a modality-specific visual task and jointly tested panels are explicit", () => {
  const retiredGenericStems = new Set([
    "Identify the pulmonary finding or diagnosis demonstrated in this image.",
    "Identify the tissue, organism, pathologic process, or diagnosis shown.",
    "Identify the structure, finding, or diagnosis demonstrated in this image.",
    "Identify the physiologic pattern or interpretation demonstrated by this visual.",
    "Identify the pulmonary finding, pattern, or procedure shown.",
  ]);
  for (const question of questions) {
    assert.equal(retiredGenericStems.has(question.stem), false, question.question_id);
    if (question.joint_images) assert.match(`${question.stem} ${question.visual_target}`, /together|both|joint/i, question.question_id);
  }
});

test("no distractor duplicates or contains the keyed answer concept", () => {
  const normalize = (value) => value.toLowerCase().replace(/[^a-z0-9]+/g, " ").trim();
  for (const question of questions) {
    const keyed = normalize(question.options[question.correct_index]);
    question.options.forEach((option, index) => {
      if (index === question.correct_index) return;
      const distractor = normalize(option);
      assert.equal(keyed.includes(distractor) || distractor.includes(keyed), false, `${question.question_id}: ${keyed} <> ${distractor}`);
    });
  }
});

test("option randomization keeps rationales and key aligned", () => {
  const original = questions[0];
  for (const seed of [1, 2, 3, 99]) {
    const shuffled = prepareQuestion(original, seed);
    assert.equal(shuffled.options.length, 4);
    assert.match(shuffled.choice_rationales[shuffled.correct_index], /^Correct:/);
    assert.equal(shuffled.options[shuffled.correct_index], original.options[original.correct_index]);
    for (let i = 0; i < shuffled.options.length; i += 1) {
      const oldIndex = original.options.indexOf(shuffled.options[i]);
      assert.equal(shuffled.choice_rationales[i], original.choice_rationales[oldIndex]);
    }
  }
});

test("session selection is deterministic and respects filters and requested length", () => {
  let progress = emptyProgress();
  progress.questions[questions[0].question_id] = { times_answered: 1, incorrect_count: 1 };
  progress.marked = [questions[1].question_id];
  const config = { mode: "learn", category: "all", stateFilter: "all", length: 20 };
  const one = createSession(questions, config, progress, 12345);
  const two = createSession(questions, config, progress, 12345);
  assert.deepEqual(one.questions.map((q) => q.question_id), two.questions.map((q) => q.question_id));
  assert.equal(one.questions.length, 20);
  const incorrect = createSession(questions, { ...config, stateFilter: "incorrect", length: "all" }, progress, 1);
  assert.deepEqual(incorrect.questions.map((q) => q.question_id), [questions[0].question_id]);
  const marked = createSession(questions, { ...config, stateFilter: "marked", length: "all" }, progress, 1);
  assert.deepEqual(marked.questions.map((q) => q.question_id), [questions[1].question_id]);
  const lecture = createSession(questions, { ...config, sourceOrigin: "lecture", length: "all" }, progress, 1);
  const thirdParty = createSession(questions, { ...config, sourceOrigin: "third_party", length: "all" }, progress, 1);
  assert.ok(lecture.questions.length > 0);
  assert.ok(thirdParty.questions.length > 0);
  assert.ok(lecture.questions.every((q) => q.source_origin === "lecture"));
  assert.ok(thirdParty.questions.every((q) => q.source_origin === "third_party"));
  assert.equal(lecture.questions.length + thirdParty.questions.length, questions.length);
});

test("session selection avoids adjacent source groups when alternatives exist", () => {
  const session = createSession(questions, { mode: "learn", category: "all", stateFilter: "all", length: "all" }, emptyProgress(), 77);
  for (let index = 1; index < session.questions.length; index += 1) {
    assert.notEqual(session.questions[index - 1].source_group_id, session.questions[index].source_group_id);
  }
});

test("answers lock deterministically and cannot be replaced", () => {
  const question = prepareQuestion(questions[0], 42);
  const first = lockAnswer(question, null, question.correct_index);
  assert.equal(first.correct, true);
  const attemptedReplacement = lockAnswer(question, first, (question.correct_index + 1) % 4);
  assert.strictEqual(attemptedReplacement, first);
});

test("scoring and progress update question, source group, and concept", () => {
  const q1 = prepareQuestion(questions[0], 4);
  const q2 = prepareQuestion(questions[1], 4);
  const a1 = lockAnswer(q1, null, q1.correct_index);
  const a2 = lockAnswer(q2, null, (q2.correct_index + 1) % 4);
  const score = scoreAnswers([q1, q2], { [q1.question_id]: a1, [q2.question_id]: a2 });
  assert.equal(score.correct, 1);
  assert.equal(score.incorrect, 1);
  assert.equal(score.percentage, 50);
  const updated = applyAnswerToProgress(emptyProgress(), q1, a1);
  assert.equal(updated.questions[q1.question_id].correct_count, 1);
  assert.equal(updated.source_groups[q1.source_group_id].correct_count, 1);
  assert.equal(updated.concepts[q1.tested_concept].correct_count, 1);
});

test("unanswered questions remain navigable and count separately in the final score", () => {
  const q1 = prepareQuestion(questions[0], 8);
  const q2 = prepareQuestion(questions[1], 8);
  const answer = lockAnswer(q1, null, q1.correct_index);
  const score = scoreAnswers([q1, q2], { [q1.question_id]: answer });
  assert.equal(score.correct, 1);
  assert.equal(score.incorrect, 0);
  assert.equal(score.unanswered, 1);
  assert.equal(score.answered, 1);
  assert.equal(score.total, 2);
  assert.equal(score.percentage, 50);
  assert.equal(score.graded.length, 2);
});

test("progress schema, marking, import normalization, and reset are versioned", () => {
  const empty = emptyProgress();
  assert.equal(empty.schema_version, PROGRESS_SCHEMA_VERSION);
  const marked = toggleMarked(empty, questions[0].question_id);
  assert.deepEqual(marked.marked, [questions[0].question_id]);
  assert.deepEqual(toggleMarked(marked, questions[0].question_id).marked, []);
  assert.deepEqual(normalizeProgress({ schema_version: 999 }), emptyProgress());
});

test("photo-quality flags are versioned, updateable, and resolve without changing study progress", () => {
  const empty = emptyQualityFlags();
  assert.equal(empty.schema_version, QUALITY_FLAGS_SCHEMA_VERSION);
  assert.deepEqual(normalizeQualityFlags({ schema_version: 999 }), emptyQualityFlags());
  const question = questions[0];
  const flagged = upsertQualityFlag(empty, {
    question_id: question.question_id,
    source_id: question.source_id,
    variant_id: question.variant_id,
    issue_type: "cropped-incomplete",
    note: "Missing a border",
  });
  assert.equal(flagged.flags[question.question_id].status, "open");
  assert.equal(flagged.flags[question.question_id].note, "Missing a border");
  const updated = upsertQualityFlag(flagged, {
    question_id: question.question_id,
    issue_type: "blurry-low-quality",
    note: "Use the sharper teaching original",
  });
  assert.equal(updated.flags[question.question_id].flag_id, flagged.flags[question.question_id].flag_id);
  assert.equal(updated.flags[question.question_id].issue_type, "blurry-low-quality");
  const resolved = setQualityFlagStatus(updated, question.question_id, "resolved");
  assert.equal(resolved.flags[question.question_id].status, "resolved");
  assert.equal("questions" in resolved, false);
});

test("a completed quality-review batch resolves matching local flags once and preserves a later reopen", () => {
  const question = questions[0];
  const flagged = upsertQualityFlag(emptyQualityFlags(), {
    question_id: question.question_id,
    issue_type: "cropped-incomplete",
    note: "Needs a tighter crop",
  });
  const review = {
    batch_id: "batch-1",
    reviewed_at: "2026-09-14T12:00:00-04:00",
    resolved_flags: [{ question_id: question.question_id, action: "crop", reason: "Cropped and verified." }],
  };
  const resolved = reconcileQualityFlags(flagged, review);
  assert.equal(resolved.flags[question.question_id].status, "resolved");
  assert.equal(resolved.flags[question.question_id].resolution_action, "crop");
  assert.equal(resolved.flags[question.question_id].resolution_batch, "batch-1");
  const reopened = setQualityFlagStatus(resolved, question.question_id, "open");
  assert.equal(reconcileQualityFlags(reopened, review).flags[question.question_id].status, "open");
});

test("rationales reveal only after Learn submission or Exam completion", () => {
  assert.equal(rationaleVisible("learn", false, false), false);
  assert.equal(rationaleVisible("learn", true, false), true);
  assert.equal(rationaleVisible("exam", true, false), false);
  assert.equal(rationaleVisible("exam", true, true), true);
});

test("review queue is excluded from the scored bank", () => {
  const scoredIds = new Set(questions.map((question) => question.source_id));
  assert.equal(review.count, review.items.length);
  for (const item of review.items) {
    assert.equal(item.project_status, "NEEDS_REVIEW");
    assert.equal(scoredIds.has(item.source_id), false);
  }
});

test("learner-facing asset paths are opaque and alt text is neutral", async () => {
  for (const question of questions) {
    assert.match(question.quiz_asset, /^public\/assets\/images\/quiz_[a-f0-9]{16}\.png$/);
    const folded = question.quiz_asset.toLowerCase();
    const answerWords = question.options[question.correct_index].toLowerCase().split(/[^a-z0-9]+/).filter((x) => x.length >= 5);
    assert.equal(answerWords.some((word) => folded.includes(word)), false);
  }
  const appSource = await readFile(new URL("src/app.js", project), "utf8");
  assert.match(appSource, /alt="quiz source image"/);
  assert.match(appSource, /data-action="previous"/);
  assert.match(appSource, /data-action="next"/);
  assert.match(appSource, /state\.drafts\[currentQuestion\(\)\.question_id\]/);
  assert.match(appSource, /Flag bad photo/);
  assert.match(appSource, /pulmonary-picture-quality-flags/);
  assert.match(appSource, /Picture source/);
  assert.match(appSource, /sourceOrigin/);
});
