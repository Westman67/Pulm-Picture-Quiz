import assert from "node:assert/strict";
import { readFile } from "node:fs/promises";
import test from "node:test";
import {
  PROGRESS_SCHEMA_VERSION,
  applyAnswerToProgress,
  createSession,
  emptyProgress,
  lockAnswer,
  normalizeProgress,
  prepareQuestion,
  rationaleVisible,
  scoreAnswers,
  toggleMarked,
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
    assert.ok(question.source_group_id);
    assert.ok(question.variant_id);
  }
});

test("every question has four unique options and four nonempty aligned rationales", () => {
  for (const question of questions) {
    assert.equal(question.options.length, 4, question.question_id);
    assert.equal(new Set(question.options.map((x) => x.trim().toLowerCase())).size, 4, question.question_id);
    assert.equal(question.choice_rationales.length, 4, question.question_id);
    assert.ok(question.choice_rationales.every((x) => typeof x === "string" && x.trim()), question.question_id);
    assert.match(question.choice_rationales[question.correct_index], /^Correct:/, question.question_id);
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

test("progress schema, marking, import normalization, and reset are versioned", () => {
  const empty = emptyProgress();
  assert.equal(empty.schema_version, PROGRESS_SCHEMA_VERSION);
  const marked = toggleMarked(empty, questions[0].question_id);
  assert.deepEqual(marked.marked, [questions[0].question_id]);
  assert.deepEqual(toggleMarked(marked, questions[0].question_id).marked, []);
  assert.deepEqual(normalizeProgress({ schema_version: 999 }), emptyProgress());
});

test("rationales reveal only after Learn submission or Exam completion", () => {
  assert.equal(rationaleVisible("learn", false, false), false);
  assert.equal(rationaleVisible("learn", true, false), true);
  assert.equal(rationaleVisible("exam", true, false), false);
  assert.equal(rationaleVisible("exam", true, true), true);
});

test("review queue is excluded from the scored bank", () => {
  const scoredIds = new Set(questions.map((question) => question.source_id));
  assert.ok(review.items.length > 0);
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
});
