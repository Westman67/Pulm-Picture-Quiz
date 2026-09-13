export const PROGRESS_SCHEMA_VERSION = 2;
export const STORAGE_KEY = "pulmonary-picture-id-progress-v2";

export function hashSeed(text) {
  let h = 2166136261;
  for (let i = 0; i < String(text).length; i += 1) {
    h ^= String(text).charCodeAt(i);
    h = Math.imul(h, 16777619);
  }
  return h >>> 0;
}

function mulberry32(seed) {
  return function random() {
    let t = (seed += 0x6d2b79f5);
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

export function seededShuffle(items, seed) {
  const result = [...items];
  const random = mulberry32(typeof seed === "number" ? seed : hashSeed(seed));
  for (let i = result.length - 1; i > 0; i -= 1) {
    const j = Math.floor(random() * (i + 1));
    [result[i], result[j]] = [result[j], result[i]];
  }
  return result;
}

export function prepareQuestion(question, sessionSeed) {
  const pairs = question.options.map((option, index) => ({
    option,
    rationale: question.choice_rationales[index],
    correct: index === question.correct_index,
  }));
  const shuffled = seededShuffle(pairs, `${sessionSeed}:${question.question_id}`);
  return {
    ...question,
    options: shuffled.map((pair) => pair.option),
    choice_rationales: shuffled.map((pair) => pair.rationale),
    correct_index: shuffled.findIndex((pair) => pair.correct),
  };
}

export function emptyProgress() {
  return {
    schema_version: PROGRESS_SCHEMA_VERSION,
    updated_at: null,
    questions: {},
    source_groups: {},
    concepts: {},
    marked: [],
    exam_attempts: [],
    last_session: null,
  };
}

export function normalizeProgress(value) {
  const base = emptyProgress();
  if (!value || Number(value.schema_version) !== PROGRESS_SCHEMA_VERSION) return base;
  return {
    ...base,
    ...value,
    questions: value.questions || {},
    source_groups: value.source_groups || {},
    concepts: value.concepts || {},
    marked: Array.isArray(value.marked) ? value.marked : [],
    exam_attempts: Array.isArray(value.exam_attempts) ? value.exam_attempts : [],
  };
}

function progressMatches(question, progress, stateFilter) {
  const item = progress.questions?.[question.question_id] || {};
  if (stateFilter === "unseen") return !item.times_answered;
  if (stateFilter === "incorrect") return (item.incorrect_count || 0) > 0;
  if (stateFilter === "marked") return progress.marked?.includes(question.question_id);
  return true;
}

function spreadSourceGroups(questions) {
  const remaining = [...questions];
  const result = [];
  while (remaining.length) {
    const previous = result.at(-1)?.source_group_id;
    let index = remaining.findIndex((question) => question.source_group_id !== previous);
    if (index < 0) index = 0;
    result.push(remaining.splice(index, 1)[0]);
  }
  return result;
}

export function createSession(questions, config, progress, seed = Date.now()) {
  const category = config.category || "all";
  const stateFilter = config.stateFilter || "all";
  let candidates = questions.filter((question) =>
    (category === "all" || question.category === category || question.modality === category) &&
    progressMatches(question, progress, stateFilter),
  );
  candidates = spreadSourceGroups(seededShuffle(candidates, seed));
  const requested = config.length === "all" || config.length === "endless"
    ? candidates.length
    : Number(config.length || 10);
  const selected = candidates.slice(0, Math.min(requested, candidates.length));
  return {
    id: `session_${hashSeed(`${seed}:${config.mode}:${category}:${stateFilter}`)}`,
    seed,
    mode: config.mode || "learn",
    category,
    stateFilter,
    endless: config.length === "endless",
    requested_length: config.length,
    available_count: candidates.length,
    questions: selected.map((question) => prepareQuestion(question, seed)),
  };
}

export function lockAnswer(question, existingAnswer, selectedIndex) {
  if (existingAnswer?.locked) return existingAnswer;
  if (!Number.isInteger(selectedIndex) || selectedIndex < 0 || selectedIndex > 3) {
    throw new Error("Select an answer before submitting.");
  }
  return {
    selected_index: selectedIndex,
    correct_index: question.correct_index,
    correct: selectedIndex === question.correct_index,
    locked: true,
    answered_at: new Date().toISOString(),
  };
}

export function rationaleVisible(mode, submitted, examComplete) {
  return mode === "learn" ? Boolean(submitted) : Boolean(examComplete);
}

function bump(record, correct, now) {
  return {
    times_seen: (record?.times_seen || 0) + 1,
    times_answered: (record?.times_answered || 0) + 1,
    correct_count: (record?.correct_count || 0) + (correct ? 1 : 0),
    incorrect_count: (record?.incorrect_count || 0) + (correct ? 0 : 1),
    last_result: correct ? "correct" : "incorrect",
    last_answered_at: now,
  };
}

export function applyAnswerToProgress(progressValue, question, answer) {
  const progress = normalizeProgress(progressValue);
  const now = answer.answered_at || new Date().toISOString();
  const next = structuredClone(progress);
  next.questions[question.question_id] = bump(next.questions[question.question_id], answer.correct, now);
  next.source_groups[question.source_group_id] = bump(next.source_groups[question.source_group_id], answer.correct, now);
  next.concepts[question.tested_concept] = bump(next.concepts[question.tested_concept], answer.correct, now);
  next.updated_at = now;
  return next;
}

export function toggleMarked(progressValue, questionId) {
  const progress = structuredClone(normalizeProgress(progressValue));
  const set = new Set(progress.marked);
  if (set.has(questionId)) set.delete(questionId);
  else set.add(questionId);
  progress.marked = [...set];
  progress.updated_at = new Date().toISOString();
  return progress;
}

export function scoreAnswers(questions, answers) {
  const graded = questions.map((question) => ({ question, answer: answers[question.question_id] }))
    .filter((item) => item.answer?.locked);
  const correct = graded.filter((item) => item.answer.correct).length;
  const byCategory = {};
  for (const item of graded) {
    const key = item.question.category || item.question.modality;
    byCategory[key] ||= { correct: 0, total: 0 };
    byCategory[key].total += 1;
    if (item.answer.correct) byCategory[key].correct += 1;
  }
  return {
    correct,
    incorrect: graded.length - correct,
    total: graded.length,
    percentage: graded.length ? Math.round((correct / graded.length) * 100) : 0,
    byCategory,
    graded,
  };
}
