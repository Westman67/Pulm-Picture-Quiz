import {
  QUALITY_FLAGS_STORAGE_KEY,
  STORAGE_KEY,
  applyAnswerToProgress,
  createSession,
  emptyQualityFlags,
  emptyProgress,
  lockAnswer,
  normalizeQualityFlags,
  normalizeProgress,
  reconcileQualityFlags,
  rationaleVisible,
  scoreAnswers,
  setQualityFlagStatus,
  toggleMarked,
  upsertQualityFlag,
} from "./quiz-core.mjs?v=rename-add-20260916d";

const app = document.querySelector("#app");
const state = {
  bank: null,
  reviewQueue: null,
  progress: loadProgress(),
  qualityFlags: loadQualityFlags(),
  view: "home",
  session: null,
  position: 0,
  drafts: {},
  answers: {},
  examComplete: false,
  flaggingQuestionId: null,
  showingOriginal: false,
  zoom: { scale: 1, x: 0, y: 0 },
  drag: null,
};

const QUALITY_FLAG_REASONS = {
  "cropped-incomplete": "Cropped or incomplete",
  "blurry-low-quality": "Blurry or low quality",
  "distorted-orientation": "Distorted or wrong orientation",
  "answer-visible": "Answer visible in image",
  "wrong-image-answer": "Wrong image or answer",
  "irrelevant-content": "Irrelevant content included",
  "context-stem": "Context or stem problem",
  other: "Other photo issue",
};

const COLLECTION_LABELS = {
  rename: "Rename collection",
  third_party: "3rd Party",
};

const CATEGORY_FILTERS = ["CXR", "CT", "All Imaging", "Histology", "Gross"];
const IMAGING_MODALITIES = new Set([
  "X-ray",
  "CT",
  "X-ray and CT",
  "X-ray and pathology",
  "X-ray, CT, and pathology",
  "MRI",
  "Angiography",
  "Nuclear Imaging",
  "Ultrasound",
  "Echocardiography",
]);
const HISTOLOGY_MODALITIES = new Set([
  "Histology",
  "Histopathology",
  "Microscopy",
  "Micrograph",
  "Immunohistochemistry",
  "Electron Microscopy",
  "Cytology",
  "Gross pathology and histology",
  "X-ray and pathology",
  "X-ray, CT, and pathology",
  "Microscopy",
]);
const GROSS_MODALITIES = new Set([
  "Gross Pathology",
  "Gross pathology",
  "Gross Anatomy",
  "Gross pathology and histology",
]);

function categoryFiltersFor(modality) {
  const filters = [];
  if (modality.includes("X-ray")) filters.push("CXR");
  if (modality.includes("CT")) filters.push("CT");
  if (IMAGING_MODALITIES.has(modality)) filters.push("All Imaging");
  if (HISTOLOGY_MODALITIES.has(modality)) filters.push("Histology");
  if (GROSS_MODALITIES.has(modality)) filters.push("Gross");
  return filters;
}

function imageCategoryFor(modality) {
  if (modality === "X-ray") return "CXR";
  if (modality === "CT") return "CT";
  if (IMAGING_MODALITIES.has(modality)) return "All Imaging";
  if (HISTOLOGY_MODALITIES.has(modality)) return "Histology";
  if (GROSS_MODALITIES.has(modality)) return "Gross";
  return "Other";
}

function applyImageCategories(bank) {
  bank.questions.forEach((question) => {
    question.topic = question.category;
    question.category = imageCategoryFor(question.modality);
    question.category_filters = categoryFiltersFor(question.modality);
  });
  return bank;
}


function loadProgress() {
  try {
    return normalizeProgress(JSON.parse(localStorage.getItem(STORAGE_KEY) || "null"));
  } catch {
    return emptyProgress();
  }
}

function saveProgress() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(state.progress));
}

function loadQualityFlags() {
  try {
    return normalizeQualityFlags(JSON.parse(localStorage.getItem(QUALITY_FLAGS_STORAGE_KEY) || "null"));
  } catch {
    return emptyQualityFlags();
  }
}

function saveQualityFlags() {
  localStorage.setItem(QUALITY_FLAGS_STORAGE_KEY, JSON.stringify(state.qualityFlags));
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

function currentQuestion() {
  return state.session?.questions[state.position] || null;
}

function currentAnswer() {
  const question = currentQuestion();
  return question ? state.answers[question.question_id] : null;
}

function currentSelection() {
  const question = currentQuestion();
  if (!question) return null;
  const answer = currentAnswer();
  return answer?.locked ? answer.selected_index : (state.drafts[question.question_id] ?? null);
}

function currentQualityFlag() {
  const question = currentQuestion();
  return question ? state.qualityFlags.flags[question.question_id] || null : null;
}

function scrollPageTop() {
  window.scrollTo(0, 0);
  requestAnimationFrame(() => requestAnimationFrame(() => window.scrollTo(0, 0)));
  for (const delay of [0, 80, 250, 650]) setTimeout(() => window.scrollTo(0, 0), delay);
}

function setView(view) {
  document.activeElement?.blur();
  state.view = view;
  state.flaggingQuestionId = null;
  state.showingOriginal = false;
  resetZoom();
  render();
  scrollPageTop();
}

function header() {
  const openFlagCount = Object.values(state.qualityFlags.flags).filter((flag) => flag.status !== "resolved").length;
  const reviewCount = (state.reviewQueue?.count || 0) + openFlagCount;
  return `
    <header class="app-header">
      <button class="brand" data-action="home" aria-label="Return to dashboard">
        <span class="brand-mark">P</span>
        <span><strong>Pulmonary ID Lab</strong><small>Image-first visual practical</small></span>
      </button>
      <nav aria-label="Primary navigation">
        <button class="nav-button ${state.view === "home" ? "active" : ""}" data-action="home">Dashboard</button>
        <button class="nav-button ${state.view === "review" ? "active" : ""}" data-action="review">Review & flags <span>${reviewCount}</span></button>
      </nav>
    </header>`;
}

function homeView() {
  const categoryCounts = Object.fromEntries(CATEGORY_FILTERS.map((category) => [
    category,
    state.bank.questions.filter((question) => question.category_filters.includes(category)).length,
  ]));
  const collectionCounts = state.bank.questions.reduce((counts, question) => {
    counts[question.source_collection_key] = (counts[question.source_collection_key] || 0) + 1;
    return counts;
  }, {});
  const answered = Object.values(state.progress.questions).filter((p) => p.times_answered).length;
  const totalCorrect = Object.values(state.progress.questions).reduce((sum, p) => sum + (p.correct_count || 0), 0);
  const totalAnswered = Object.values(state.progress.questions).reduce((sum, p) => sum + (p.times_answered || 0), 0);
  const openFlagCount = Object.values(state.qualityFlags.flags).filter((flag) => flag.status !== "resolved").length;
  return `
    <main class="dashboard shell">
      <section class="hero">
        <div>
          <p class="eyebrow">Pulmonary visual recognition</p>
          <h1>See it. Name it. Know why.</h1>
          <p class="hero-copy">A local, image-identification practical built from ${state.bank.question_count} verified pulmonary sources.</p>
        </div>
        <div class="hero-stat"><strong>${answered}</strong><span>concepts seen</span><small>${totalAnswered ? Math.round(totalCorrect / totalAnswered * 100) : 0}% cumulative accuracy</small></div>
      </section>

      <section class="setup-grid">
        <form id="session-form" class="panel session-panel">
          <div class="section-heading"><div><p class="eyebrow">New session</p><h2>Configure your practical</h2></div><span class="verified-pill">Verified bank</span></div>

          <fieldset><legend>Feedback mode</legend><div class="segmented">
            <label><input type="radio" name="mode" value="learn" checked><span><strong>Learn</strong><small>Immediate clues and rationales</small></span></label>
            <label><input type="radio" name="mode" value="exam"><span><strong>Exam</strong><small>Results only after completion</small></span></label>
          </div></fieldset>

          <div class="form-row">
            <label>Category<select name="category"><option value="all">Mixed — all categories</option>${CATEGORY_FILTERS.map((category) => `<option value="${escapeHtml(category)}">${escapeHtml(category)} (${categoryCounts[category]})</option>`).join("")}</select></label>
            <label>Collection<select name="sourceCollection"><option value="all">All pictures (${state.bank.question_count})</option>${Object.entries(COLLECTION_LABELS).map(([key, label]) => `<option value="${escapeHtml(key)}">${escapeHtml(label)} (${collectionCounts[key] || 0})</option>`).join("")}</select></label>
            <label>Question state<select name="stateFilter"><option value="all">All available</option><option value="unseen">Unseen only</option><option value="incorrect">Previously incorrect</option><option value="marked">Marked for review</option></select></label>
          </div>

          <fieldset><legend>Length</legend><div class="length-options">
            ${[10, 20, 40].map((n) => `<label><input type="radio" name="length" value="${n}" ${n === 20 ? "checked" : ""}><span>${n}</span></label>`).join("")}
            <label><input type="radio" name="length" value="all"><span>All</span></label>
            <label><input type="radio" name="length" value="endless"><span>Endless</span></label>
          </div></fieldset>
          <button class="primary large" type="submit">Start ID quiz <span>→</span></button>
        </form>

        <aside class="dashboard-side">
          <section class="panel mini-stats"><div><span>Bank</span><strong>${state.bank.question_count}</strong><small>scored visual IDs</small></div><div><span>Source review</span><strong>${state.reviewQueue.count}</strong><small>withheld candidates</small></div><div><span>Photo flags</span><strong>${openFlagCount}</strong><small>open fixes</small></div><div><span>Storage</span><strong>Local</strong><small>no uploads</small></div></section>
          <section class="panel data-panel"><p class="eyebrow">Learner data</p><h3>Portable progress</h3><p>Export a versioned backup or import it on another browser.</p><div class="button-row"><button data-action="export" class="secondary">Export</button><label class="secondary file-label">Import<input id="import-file" type="file" accept="application/json"></label><button data-action="reset-progress" class="danger-ghost">Reset</button></div></section>
          <section class="safety-note"><strong>Image safety</strong><p>Quiz assets use opaque filenames and preserve diagnostic pixels. Client-side answers are not cryptographically secret.</p></section>
        </aside>
      </section>
    </main>`;
}

function quizView() {
  const question = currentQuestion();
  if (!question) return emptyState("No questions match those filters.", "Try a broader category or question state.");
  const answer = currentAnswer();
  const submitted = Boolean(answer?.locked);
  const reveal = rationaleVisible(state.session.mode, submitted, state.examComplete);
  const marked = state.progress.marked.includes(question.question_id);
  const imageSrc = state.showingOriginal && reveal ? question.original_asset : question.quiz_asset;
  const progressLabel = state.session.endless ? `Endless · ${state.position + 1}` : `${state.position + 1} / ${state.session.questions.length}`;
  const answeredCount = Object.values(state.answers).filter((item) => item?.locked).length;
  const isLast = state.position === state.session.questions.length - 1 && !state.session.endless;
  const selectedIndex = currentSelection();
  const qualityFlag = currentQualityFlag();
  return `
    <main class="quiz-shell shell">
      <section class="quiz-topbar">
        <div><span class="mode-badge ${state.session.mode}">${state.session.mode === "learn" ? "Learn mode" : "Exam mode"}</span><span class="category-label">${escapeHtml(question.category)} · ${escapeHtml(question.topic)} · ${escapeHtml(question.source_collection || COLLECTION_LABELS[question.source_collection_key] || question.source_collection_key)}</span></div>
        <strong>${progressLabel}</strong>
        <div class="quiz-topbar-actions">
          <button class="mark-button ${marked ? "marked" : ""}" data-action="mark">${marked ? "★ Marked" : "☆ Mark for study"}</button>
          <button class="flag-button ${qualityFlag?.status === "open" ? "flagged" : ""}" data-action="toggle-flag" aria-pressed="${state.flaggingQuestionId === question.question_id}">${qualityFlag?.status === "open" ? "⚑ Photo flagged" : "⚐ Flag bad photo"}</button>
        </div>
      </section>
      <div class="progress-track" aria-label="${answeredCount} of ${state.session.questions.length} answers locked"><span style="width:${state.session.endless ? 100 : (answeredCount / state.session.questions.length * 100)}%"></span></div>

      <section class="quiz-grid">
        <div class="image-panel panel">
          <div class="image-toolbar"><span>${state.showingOriginal && reveal ? "Teaching original" : "Quiz image"}</span><div><button data-action="zoom-out" aria-label="Zoom out">−</button><button data-action="reset-zoom">Reset</button><button data-action="zoom-in" aria-label="Zoom in">+</button><button data-action="toggle-zoom" aria-label="Toggle zoom">Z</button></div></div>
          <div id="image-stage" class="image-stage ${state.zoom.scale > 1 ? "zoomed" : ""}">
            <img id="quiz-image" src="${escapeHtml(imageSrc)}" alt="quiz source image" draggable="false" style="transform:translate(${state.zoom.x}px, ${state.zoom.y}px) scale(${state.zoom.scale})">
          </div>
          <p class="image-hint">Scroll or use controls to zoom · drag to pan · double-click to reset</p>
        </div>

        <div class="question-panel">
          <div class="question-heading">
            <p class="eyebrow">Identification</p>
            ${question.case_context ? `<p class="case-context">${escapeHtml(question.case_context)}</p>` : ""}
            <h1>${escapeHtml(question.stem)}</h1>
            <p class="visual-target"><strong>Visual target:</strong> ${escapeHtml(question.visual_target || "the complete displayed image")}${question.joint_images ? " · panels tested jointly" : ""}</p>
          </div>
          ${qualityFlagTemplate(question, qualityFlag)}
          <div class="choices" role="radiogroup" aria-label="Answer choices">
            ${question.options.map((option, index) => choiceTemplate(question, option, index, answer, reveal)).join("")}
          </div>
          <div id="answer-error" class="inline-error" role="alert"></div>
          ${feedbackTemplate(question, answer, reveal)}
          <div class="quiz-actions">
            <button class="secondary nav-control" data-action="previous" ${state.position === 0 ? "disabled" : ""}>← Back</button>
            ${!submitted ? `<button class="secondary lock-control" data-action="submit" ${selectedIndex === null ? "disabled" : ""}>Lock answer <kbd>Enter</kbd></button>` : `<span class="locked-status">Answer locked</span>`}
            <button class="primary nav-control" data-action="next">${isLast ? (state.session.mode === "exam" ? "Finish exam" : "View summary") : "Next →"}</button>
            ${reveal && question.original_asset !== question.quiz_asset ? `<button class="secondary" data-action="toggle-original">${state.showingOriginal ? "Show quiz crop" : "Show teaching original"}</button>` : ""}
          </div>
        </div>
      </section>
    </main>`;
}

function qualityFlagTemplate(question, existing) {
  if (state.flaggingQuestionId !== question.question_id) return "";
  const selectedReason = existing?.issue_type || "";
  return `<form id="quality-flag-form" class="quality-flag-form panel">
    <div><p class="eyebrow">Photo quality flag</p><h2>${existing ? "Update this flag" : "Send this photo for fixing"}</h2><p>Stored locally with the question, source, variant, and image IDs. It will not change your quiz score.</p></div>
    <label>Issue type
      <select name="issueType" required>
        <option value="">Choose an issue…</option>
        ${Object.entries(QUALITY_FLAG_REASONS).map(([value, label]) => `<option value="${value}" ${selectedReason === value ? "selected" : ""}>${escapeHtml(label)}</option>`).join("")}
      </select>
    </label>
    <label>Optional note
      <textarea name="note" maxlength="500" placeholder="What should be fixed?">${escapeHtml(existing?.note || "")}</textarea>
    </label>
    <p class="flag-error inline-error" role="alert"></p>
    <div class="button-row"><button class="flag-save" type="submit">Save photo flag</button><button class="secondary" type="button" data-action="cancel-flag">Cancel</button></div>
  </form>`;
}

function choiceTemplate(question, option, index, answer, reveal) {
  const selected = currentSelection() === index;
  const correct = reveal && index === question.correct_index;
  const incorrect = reveal && answer?.selected_index === index && !answer.correct;
  const classes = ["choice", selected ? "selected" : "", correct ? "correct" : "", incorrect ? "incorrect" : ""].filter(Boolean).join(" ");
  return `<button class="${classes}" data-action="choose" data-index="${index}" role="radio" aria-checked="${selected}" ${answer?.locked ? "disabled" : ""}><span class="choice-number">${index + 1}</span><span>${escapeHtml(option)}</span>${correct ? '<span class="choice-status">Correct</span>' : incorrect ? '<span class="choice-status">Your answer</span>' : ""}</button>`;
}

function sourceDetailsTemplate(question) {
  const source = question.post_answer_source || {};
  const landing = /^https:\/\//.test(source.landing_page_url || "")
    ? `<dt>Landing page</dt><dd><a href="${escapeHtml(source.landing_page_url)}" target="_blank" rel="noopener noreferrer">Open verified source</a></dd>`
    : "";
  const creator = source.creator ? `<dt>Creator</dt><dd>${escapeHtml(source.creator)}</dd>` : "";
  const license = source.displayed_license ? `<dt>License</dt><dd>${escapeHtml(source.displayed_license)}</dd>` : "";
  const page = source.source_page_or_slide ? `<dt>Page/slide</dt><dd>${escapeHtml(source.source_page_or_slide)}</dd>` : "";
  return `<details class="source-details"><summary>Source provenance and attribution</summary><dl><dt>Source</dt><dd>${escapeHtml(source.source_document)}</dd>${page}<dt>Original file</dt><dd>${escapeHtml(source.original_filename)}</dd>${creator}${license}${landing}<dt>Source ID</dt><dd>${escapeHtml(question.source_id)}</dd></dl></details>`;
}

function feedbackTemplate(question, answer, reveal) {
  if (!reveal) {
    if (state.session.mode === "exam" && answer?.locked) return `<div class="exam-lock-note">Answer locked. Feedback will be available when the exam is complete.</div>`;
    return "";
  }
  return `<section class="feedback ${answer.correct ? "is-correct" : "is-incorrect"}">
    <div class="feedback-title"><span>${answer.correct ? "✓" : "×"}</span><div><p>${answer.correct ? "Correct" : "Not quite"}</p><strong>${escapeHtml(question.options[question.correct_index])}</strong></div></div>
    <p>${escapeHtml(question.explanation)}</p>
    <div class="clue-box"><strong>What to notice</strong><ul>${question.visual_clues.map((clue) => `<li>${escapeHtml(clue)}</li>`).join("")}</ul></div>
    <div class="rationale-list"><h3>Choice rationales</h3>${question.options.map((option, index) => `<article class="rationale ${index === question.correct_index ? "keyed" : ""} ${index === answer.selected_index ? "selected-rationale" : ""}"><div><span>${index + 1}</span><strong>${escapeHtml(option)}</strong>${index === question.correct_index ? "<em>Keyed</em>" : ""}${index === answer.selected_index ? "<em>Your choice</em>" : ""}</div><p>${escapeHtml(question.choice_rationales[index])}</p></article>`).join("")}</div>
    ${sourceDetailsTemplate(question)}
  </section>`;
}

function resultsView() {
  const score = scoreAnswers(state.session.questions, state.answers);
  const marked = new Set(state.progress.marked);
  const review = score.graded.filter(({ question, answer }) => !answer?.correct || marked.has(question.question_id));
  return `<main class="results shell">
    <section class="results-hero"><div class="score-ring" style="--score:${score.percentage * 3.6}deg"><div><strong>${score.percentage}%</strong><span>${score.correct} / ${score.total}</span></div></div><div><p class="eyebrow">Session complete</p><h1>${score.percentage >= 80 ? "Sharp recognition." : "Review the misses, then run it again."}</h1><p>${score.correct} correct · ${score.incorrect} incorrect · ${score.unanswered} unanswered · ${marked.size} marked overall</p><div class="button-row"><button class="primary" data-action="retry-missed" ${score.incorrect + score.unanswered ? "" : "disabled"}>Retry missed</button><button class="secondary" data-action="home">New session</button></div></div></section>
    <section class="results-grid">
      <div class="panel"><h2>Performance by image type</h2><div class="category-results">${Object.entries(score.byCategory).sort().map(([name, value]) => `<div><span>${escapeHtml(name)}</span><div class="mini-track"><i style="width:${Math.round(value.correct / value.total * 100)}%"></i></div><strong>${value.correct}/${value.total}</strong></div>`).join("")}</div></div>
      <div class="panel"><h2>Review (${review.length})</h2>${review.length ? review.map(resultReviewCard).join("") : '<p class="empty-copy">No missed or marked questions in this session.</p>'}</div>
    </section>
  </main>`;
}

function resultReviewCard({ question, answer }) {
  const status = answer?.correct ? "Correct" : answer?.locked ? "Incorrect" : "Unanswered";
  return `<details class="result-card"><summary><img src="${escapeHtml(question.quiz_asset)}" alt="quiz source image"><span><small>${escapeHtml(question.category)} · ${escapeHtml(question.topic)}</small><strong>${escapeHtml(question.tested_concept)}</strong><em class="${answer?.correct ? "good" : "bad"}">${status}</em></span></summary><div><p>${escapeHtml(question.explanation)}</p><div class="rationale-list">${question.options.map((option, i) => `<article class="rationale ${i === question.correct_index ? "keyed" : ""} ${i === answer?.selected_index ? "selected-rationale" : ""}"><div><span>${i + 1}</span><strong>${escapeHtml(option)}</strong>${i === question.correct_index ? "<em>Keyed</em>" : ""}${i === answer?.selected_index ? "<em>Your choice</em>" : ""}</div><p>${escapeHtml(question.choice_rationales[i])}</p></article>`).join("")}</div>${sourceDetailsTemplate(question)}</div></details>`;
}

function reviewView() {
  const flags = Object.values(state.qualityFlags.flags).sort((a, b) => {
    const statusOrder = Number(a.status === "resolved") - Number(b.status === "resolved");
    return statusOrder || String(b.updated_at || "").localeCompare(String(a.updated_at || ""));
  });
  const openFlags = flags.filter((flag) => flag.status !== "resolved").length;
  const qualityFlags = flags.length
    ? `<div class="quality-flag-grid">${flags.map((flag) => {
        const question = state.bank.questions.find((item) => item.question_id === flag.question_id);
        const image = question?.quiz_asset || flag.quiz_asset;
        const status = flag.status === "resolved" ? "resolved" : "open";
        return `<article class="quality-flag-card panel ${status}">
          <img src="${escapeHtml(image)}" alt="flagged quiz source image">
          <div><span class="quality-status ${status}">${status}</span><h3>${escapeHtml(question?.tested_concept || flag.tested_concept || "Flagged photo")}</h3>
          <p class="quality-reason">${escapeHtml(QUALITY_FLAG_REASONS[flag.issue_type] || flag.issue_type)}</p>
          ${flag.note ? `<p>${escapeHtml(flag.note)}</p>` : '<p class="empty-copy">No note supplied.</p>'}
          <dl><dt>Question</dt><dd>${escapeHtml(flag.question_id)}</dd><dt>Source</dt><dd>${escapeHtml(flag.source_id)}</dd><dt>Variant</dt><dd>${escapeHtml(flag.variant_id)}</dd><dt>Updated</dt><dd>${escapeHtml(flag.updated_at)}</dd></dl>
          <button class="secondary" data-action="set-flag-status" data-question-id="${escapeHtml(flag.question_id)}" data-status="${status === "open" ? "resolved" : "open"}">${status === "open" ? "Mark fixed" : "Reopen flag"}</button>
          </div>
        </article>`;
      }).join("")}</div>`
    : '<section class="panel quality-empty"><span>⚐</span><h2>No photo-quality flags yet</h2><p>Use “Flag bad photo” while taking a quiz to send an image here for fixing.</p></section>';
  const queue = state.reviewQueue.items.length
    ? `<div class="review-grid">${state.reviewQueue.items.map((item) => `<article class="review-card panel"><img src="${escapeHtml(item.preview_asset)}" alt="review-only source preview"><div><span class="review-status">Needs review</span><h2>${escapeHtml(item.proposed_answer)}</h2><p>${escapeHtml(item.uncertainty_reason)}</p><dl><dt>Modality</dt><dd>${escapeHtml(item.modality)}</dd><dt>Evidence</dt><dd>${escapeHtml(item.evidence)}</dd><dt>Leak risk</dt><dd>${escapeHtml(item.answer_leakage_risk)}</dd><dt>Source ID</dt><dd>${escapeHtml(item.source_id)}</dd></dl></div></article>`).join("")}</div>`
    : '<section class="panel review-empty"><span>✓</span><h2>Review queue is empty</h2><p>There are no review-only photos in this quiz project.</p></section>';
  return `<main class="review shell">
    <section class="page-heading"><div><p class="eyebrow">Reviewer mode</p><h1>Review & photo flags</h1><p>${openFlags} open learner photo flag${openFlags === 1 ? "" : "s"}. Flags remain local until exported.</p></div><div class="button-row"><button class="secondary" data-action="export-flags" ${flags.length ? "" : "disabled"}>Export photo flags</button><button class="secondary" data-action="export-review">Export source queue</button></div></section>
    <section class="review-section"><div class="section-heading"><div><p class="eyebrow">Learner-reported fixes</p><h2>Photo quality flags (${flags.length})</h2></div></div>${qualityFlags}</section>
    <section class="review-section"><div class="section-heading"><div><p class="eyebrow">Bank curation</p><h2>Source review queue (${state.reviewQueue.items.length})</h2></div></div>${queue}</section>
  </main>`;
}

function emptyState(title, copy) {
  return `<main class="shell empty-state"><div><span>∅</span><h1>${escapeHtml(title)}</h1><p>${escapeHtml(copy)}</p><button class="primary" data-action="home">Adjust session</button></div></main>`;
}

function render() {
  let body = "";
  if (state.view === "home") body = homeView();
  if (state.view === "quiz") body = quizView();
  if (state.view === "results") body = resultsView();
  if (state.view === "review") body = reviewView();
  app.innerHTML = header() + body;
  bindStage();
}

function startSession(config, explicitQuestions = null) {
  const questions = explicitQuestions || state.bank.questions;
  state.session = createSession(questions, config, state.progress, Date.now());
  state.position = 0;
  state.drafts = {};
  state.answers = {};
  state.examComplete = false;
  state.flaggingQuestionId = null;
  state.showingOriginal = false;
  resetZoom();
  state.progress.last_session = { id: state.session.id, started_at: new Date().toISOString(), config };
  saveProgress();
  setView("quiz");
}

function submitAnswer() {
  const question = currentQuestion();
  if (!question || currentAnswer()?.locked) return;
  try {
    const answer = lockAnswer(question, currentAnswer(), currentSelection());
    state.answers[question.question_id] = answer;
    state.progress = applyAnswerToProgress(state.progress, question, answer);
    saveProgress();
    render();
  } catch (error) {
    const message = document.querySelector("#answer-error");
    if (message) message.textContent = error.message;
  }
}

function nextQuestion() {
  if (state.position < state.session.questions.length - 1) {
    document.activeElement?.blur();
    state.position += 1;
    state.flaggingQuestionId = null;
    state.showingOriginal = false;
    resetZoom();
    render();
    scrollPageTop();
    return;
  }
  if (state.session.endless) {
    document.activeElement?.blur();
    const next = createSession(state.bank.questions, { mode: state.session.mode, category: state.session.category, stateFilter: "all", length: "endless" }, state.progress, state.session.seed + 1);
    state.session.questions.push(...next.questions);
    state.position += 1;
    state.flaggingQuestionId = null;
    resetZoom();
    render();
    scrollPageTop();
    return;
  }
  state.examComplete = true;
  const score = scoreAnswers(state.session.questions, state.answers);
  if (state.session.mode === "exam") {
    state.progress.exam_attempts.push({ session_id: state.session.id, completed_at: new Date().toISOString(), correct: score.correct, total: score.total, percentage: score.percentage });
    saveProgress();
  }
  setView("results");
}

function previousQuestion() {
  if (state.position <= 0) return;
  document.activeElement?.blur();
  state.position -= 1;
  state.flaggingQuestionId = null;
  state.showingOriginal = false;
  resetZoom();
  render();
  scrollPageTop();
}

function resetZoom() {
  state.zoom = { scale: 1, x: 0, y: 0 };
}

function adjustZoom(delta) {
  state.zoom.scale = Math.max(1, Math.min(5, Number((state.zoom.scale + delta).toFixed(2))));
  if (state.zoom.scale === 1) state.zoom = { scale: 1, x: 0, y: 0 };
  render();
}

function bindStage() {
  const stage = document.querySelector("#image-stage");
  const image = document.querySelector("#quiz-image");
  if (!stage || !image) return;
  stage.addEventListener("wheel", (event) => {
    event.preventDefault();
    adjustZoom(event.deltaY < 0 ? 0.25 : -0.25);
  }, { passive: false });
  stage.addEventListener("dblclick", () => { resetZoom(); render(); });
  stage.addEventListener("pointerdown", (event) => {
    if (state.zoom.scale <= 1) return;
    stage.setPointerCapture(event.pointerId);
    state.drag = { startX: event.clientX, startY: event.clientY, x: state.zoom.x, y: state.zoom.y };
  });
  stage.addEventListener("pointermove", (event) => {
    if (!state.drag) return;
    state.zoom.x = state.drag.x + event.clientX - state.drag.startX;
    state.zoom.y = state.drag.y + event.clientY - state.drag.startY;
    image.style.transform = `translate(${state.zoom.x}px, ${state.zoom.y}px) scale(${state.zoom.scale})`;
  });
  stage.addEventListener("pointerup", () => { state.drag = null; });
}

function downloadJson(filename, value) {
  const blob = new Blob([JSON.stringify(value, null, 2)], { type: "application/json" });
  const link = document.createElement("a");
  link.href = URL.createObjectURL(blob);
  link.download = filename;
  link.click();
  URL.revokeObjectURL(link.href);
}

app.addEventListener("submit", (event) => {
  if (event.target.id === "quality-flag-form") {
    event.preventDefault();
    const question = currentQuestion();
    if (!question) return;
    const form = new FormData(event.target);
    const existing = currentQualityFlag();
    try {
      state.qualityFlags = upsertQualityFlag(state.qualityFlags, {
        question_id: question.question_id,
        source_group_id: question.source_group_id,
        source_id: question.source_id,
        variant_id: question.variant_id,
        quiz_asset: question.quiz_asset,
        tested_concept: question.tested_concept,
        category: question.category,
        modality: question.modality,
        stem: question.stem,
        visual_target: question.visual_target,
        issue_type: String(form.get("issueType") || ""),
        note: String(form.get("note") || "").trim(),
        status: "open",
        created_at: existing?.created_at,
        session_mode: state.session.mode,
        session_position: state.position + 1,
      });
      saveQualityFlags();
      state.flaggingQuestionId = null;
      render();
    } catch (error) {
      const message = event.target.querySelector(".flag-error");
      if (message) message.textContent = error.message;
    }
    return;
  }
  if (event.target.id !== "session-form") return;
  event.preventDefault();
  const form = new FormData(event.target);
  startSession({ mode: form.get("mode"), category: form.get("category"), sourceCollection: form.get("sourceCollection"), stateFilter: form.get("stateFilter"), length: form.get("length") });
});

app.addEventListener("change", async (event) => {
  if (event.target.id !== "import-file" || !event.target.files?.[0]) return;
  try {
    const imported = normalizeProgress(JSON.parse(await event.target.files[0].text()));
    state.progress = imported;
    saveProgress();
    render();
  } catch {
    alert("That file is not a valid version-2 Pulmonary ID Lab progress export.");
  }
});

app.addEventListener("click", (event) => {
  const target = event.target.closest("[data-action]");
  if (!target) return;
  const action = target.dataset.action;
  if (action === "home") setView("home");
  if (action === "review") setView("review");
  if (action === "choose" && !currentAnswer()?.locked) { state.drafts[currentQuestion().question_id] = Number(target.dataset.index); render(); }
  if (action === "submit") submitAnswer();
  if (action === "next") nextQuestion();
  if (action === "previous") previousQuestion();
  if (action === "toggle-flag") {
    const questionId = currentQuestion()?.question_id;
    state.flaggingQuestionId = state.flaggingQuestionId === questionId ? null : questionId;
    render();
  }
  if (action === "cancel-flag") { state.flaggingQuestionId = null; render(); }
  if (action === "set-flag-status") {
    state.qualityFlags = setQualityFlagStatus(state.qualityFlags, target.dataset.questionId, target.dataset.status);
    saveQualityFlags();
    render();
  }
  if (action === "mark") { state.progress = toggleMarked(state.progress, currentQuestion().question_id); saveProgress(); render(); }
  if (action === "zoom-in") adjustZoom(0.25);
  if (action === "zoom-out") adjustZoom(-0.25);
  if (action === "reset-zoom") { resetZoom(); render(); }
  if (action === "toggle-zoom") { state.zoom = state.zoom.scale > 1 ? { scale: 1, x: 0, y: 0 } : { scale: 2, x: 0, y: 0 }; render(); }
  if (action === "toggle-original") { state.showingOriginal = !state.showingOriginal; resetZoom(); render(); }
  if (action === "export") downloadJson(`pulmonary-id-progress-${new Date().toISOString().slice(0, 10)}.json`, state.progress);
  if (action === "export-review") downloadJson("pulmonary-picture-review-queue.json", state.reviewQueue);
  if (action === "export-flags") downloadJson(`pulmonary-picture-quality-flags-${new Date().toISOString().slice(0, 10)}.json`, state.qualityFlags);
  if (action === "reset-progress" && confirm("Reset all local quiz progress? The source bank will not be changed.")) { state.progress = emptyProgress(); saveProgress(); render(); }
  if (action === "retry-missed") {
    const missed = state.session.questions.filter((question) => !state.answers[question.question_id]?.correct);
    startSession({ mode: "learn", category: "all", stateFilter: "all", length: "all" }, missed);
  }
});

window.addEventListener("keydown", (event) => {
  if (state.view !== "quiz" || event.metaKey || event.ctrlKey || event.altKey) return;
  if (event.target.closest("input, select, textarea, button")) return;
  if (["1", "2", "3", "4"].includes(event.key) && !currentAnswer()?.locked) {
    state.drafts[currentQuestion().question_id] = Number(event.key) - 1;
    render();
  }
  if (event.key === "Enter") {
    event.preventDefault();
    currentAnswer()?.locked ? nextQuestion() : submitAnswer();
  }
  if (event.key === "ArrowLeft") {
    event.preventDefault();
    previousQuestion();
  }
  if (event.key === "ArrowRight") {
    event.preventDefault();
    nextQuestion();
  }
  if (event.key.toLowerCase() === "z") {
    state.zoom = state.zoom.scale > 1 ? { scale: 1, x: 0, y: 0 } : { scale: 2, x: 0, y: 0 };
    render();
  }
});

async function init() {
  try {
    const [bank, reviewQueue] = await Promise.all([
      fetch("data/question-bank.json?v=rename-add-20260916d").then((response) => response.json()),
      fetch("data/review-queue.json?v=rename-add-20260916d").then((response) => response.json()),
    ]);
    state.bank = applyImageCategories(bank);
    state.reviewQueue = reviewQueue;
    const reconciledFlags = reconcileQualityFlags(state.qualityFlags, bank.quality_review);
    if (JSON.stringify(reconciledFlags) !== JSON.stringify(state.qualityFlags)) {
      state.qualityFlags = reconciledFlags;
      saveQualityFlags();
    }
    render();
  } catch (error) {
    app.innerHTML = `<main class="load-error"><h1>Unable to load the local bank</h1><p>${escapeHtml(error.message)}</p><p>Start the app through the documented local server; do not open index.html with file://.</p></main>`;
  }
}

init();
