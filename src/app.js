import {
  STORAGE_KEY,
  applyAnswerToProgress,
  createSession,
  emptyProgress,
  lockAnswer,
  normalizeProgress,
  rationaleVisible,
  scoreAnswers,
  toggleMarked,
} from "./quiz-core.mjs";

const app = document.querySelector("#app");
const state = {
  bank: null,
  reviewQueue: null,
  progress: loadProgress(),
  view: "home",
  session: null,
  position: 0,
  selectedIndex: null,
  answers: {},
  examComplete: false,
  showingOriginal: false,
  zoom: { scale: 1, x: 0, y: 0 },
  drag: null,
};

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

function setView(view) {
  state.view = view;
  state.showingOriginal = false;
  resetZoom();
  render();
}

function header() {
  return `
    <header class="app-header">
      <button class="brand" data-action="home" aria-label="Return to dashboard">
        <span class="brand-mark">P</span>
        <span><strong>Pulmonary ID Lab</strong><small>Image-first visual practical</small></span>
      </button>
      <nav aria-label="Primary navigation">
        <button class="nav-button ${state.view === "home" ? "active" : ""}" data-action="home">Dashboard</button>
        <button class="nav-button ${state.view === "review" ? "active" : ""}" data-action="review">Review queue <span>${state.reviewQueue?.count || 0}</span></button>
      </nav>
    </header>`;
}

function homeView() {
  const categories = [...new Set(state.bank.questions.map((q) => q.category))].sort();
  const answered = Object.values(state.progress.questions).filter((p) => p.times_answered).length;
  const totalCorrect = Object.values(state.progress.questions).reduce((sum, p) => sum + (p.correct_count || 0), 0);
  const totalAnswered = Object.values(state.progress.questions).reduce((sum, p) => sum + (p.times_answered || 0), 0);
  return `
    <main class="dashboard shell">
      <section class="hero">
        <div>
          <p class="eyebrow">Pulmonary visual recognition</p>
          <h1>See it. Name it. Know why.</h1>
          <p class="hero-copy">A local, image-identification practical built from ${state.bank.question_count} lecture-verified pulmonary sources.</p>
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
            <label>Category<select name="category"><option value="all">Mixed — all categories</option>${categories.map((c) => `<option value="${escapeHtml(c)}">${escapeHtml(c)}</option>`).join("")}</select></label>
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
          <section class="panel mini-stats"><div><span>Bank</span><strong>${state.bank.question_count}</strong><small>scored visual IDs</small></div><div><span>Review</span><strong>${state.reviewQueue.count}</strong><small>withheld candidates</small></div><div><span>Storage</span><strong>Local</strong><small>no uploads</small></div></section>
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
  return `
    <main class="quiz-shell shell">
      <section class="quiz-topbar">
        <div><span class="mode-badge ${state.session.mode}">${state.session.mode === "learn" ? "Learn mode" : "Exam mode"}</span><span class="category-label">${escapeHtml(question.category)} · ${escapeHtml(question.modality)}</span></div>
        <strong>${progressLabel}</strong>
        <button class="mark-button ${marked ? "marked" : ""}" data-action="mark">${marked ? "★ Marked" : "☆ Mark for review"}</button>
      </section>
      <div class="progress-track"><span style="width:${state.session.endless ? 100 : ((state.position + (submitted ? 1 : 0)) / state.session.questions.length * 100)}%"></span></div>

      <section class="quiz-grid">
        <div class="image-panel panel">
          <div class="image-toolbar"><span>${state.showingOriginal && reveal ? "Teaching original" : "Quiz image"}</span><div><button data-action="zoom-out" aria-label="Zoom out">−</button><button data-action="reset-zoom">Reset</button><button data-action="zoom-in" aria-label="Zoom in">+</button><button data-action="toggle-zoom" aria-label="Toggle zoom">Z</button></div></div>
          <div id="image-stage" class="image-stage ${state.zoom.scale > 1 ? "zoomed" : ""}">
            <img id="quiz-image" src="${escapeHtml(imageSrc)}" alt="quiz source image" draggable="false" style="transform:translate(${state.zoom.x}px, ${state.zoom.y}px) scale(${state.zoom.scale})">
          </div>
          <p class="image-hint">Scroll or use controls to zoom · drag to pan · double-click to reset</p>
        </div>

        <div class="question-panel">
          <div class="question-heading"><p class="eyebrow">Identification</p><h1>${escapeHtml(question.stem)}</h1></div>
          <div class="choices" role="radiogroup" aria-label="Answer choices">
            ${question.options.map((option, index) => choiceTemplate(question, option, index, answer, reveal)).join("")}
          </div>
          <div id="answer-error" class="inline-error" role="alert"></div>
          ${feedbackTemplate(question, answer, reveal)}
          <div class="quiz-actions">
            ${!submitted ? `<button class="primary" data-action="submit">Lock answer <kbd>Enter</kbd></button>` : `<button class="primary" data-action="next">${state.position === state.session.questions.length - 1 && !state.session.endless ? (state.session.mode === "exam" ? "Finish exam" : "View summary") : "Next image"} <kbd>Enter</kbd></button>`}
            ${reveal && question.original_asset !== question.quiz_asset ? `<button class="secondary" data-action="toggle-original">${state.showingOriginal ? "Show quiz crop" : "Show teaching original"}</button>` : ""}
          </div>
        </div>
      </section>
    </main>`;
}

function choiceTemplate(question, option, index, answer, reveal) {
  const selected = state.selectedIndex === index || answer?.selected_index === index;
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
  return `<details class="source-details"><summary>Lecture provenance and attribution</summary><dl><dt>Source</dt><dd>${escapeHtml(source.source_document)}</dd>${page}<dt>Original file</dt><dd>${escapeHtml(source.original_filename)}</dd>${creator}${license}${landing}<dt>Source ID</dt><dd>${escapeHtml(question.source_id)}</dd></dl></details>`;
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
  const review = score.graded.filter(({ question, answer }) => !answer.correct || marked.has(question.question_id));
  return `<main class="results shell">
    <section class="results-hero"><div class="score-ring" style="--score:${score.percentage * 3.6}deg"><div><strong>${score.percentage}%</strong><span>${score.correct} / ${score.total}</span></div></div><div><p class="eyebrow">Session complete</p><h1>${score.percentage >= 80 ? "Sharp recognition." : "Review the misses, then run it again."}</h1><p>${score.correct} correct · ${score.incorrect} incorrect · ${marked.size} marked overall</p><div class="button-row"><button class="primary" data-action="retry-missed" ${score.incorrect ? "" : "disabled"}>Retry missed</button><button class="secondary" data-action="home">New session</button></div></div></section>
    <section class="results-grid">
      <div class="panel"><h2>Performance by category</h2><div class="category-results">${Object.entries(score.byCategory).sort().map(([name, value]) => `<div><span>${escapeHtml(name)}</span><div class="mini-track"><i style="width:${Math.round(value.correct / value.total * 100)}%"></i></div><strong>${value.correct}/${value.total}</strong></div>`).join("")}</div></div>
      <div class="panel"><h2>Review (${review.length})</h2>${review.length ? review.map(resultReviewCard).join("") : '<p class="empty-copy">No missed or marked questions in this session.</p>'}</div>
    </section>
  </main>`;
}

function resultReviewCard({ question, answer }) {
  return `<details class="result-card"><summary><img src="${escapeHtml(question.quiz_asset)}" alt="quiz source image"><span><small>${escapeHtml(question.category)}</small><strong>${escapeHtml(question.tested_concept)}</strong><em class="${answer.correct ? "good" : "bad"}">${answer.correct ? "Correct" : "Incorrect"}</em></span></summary><div><p>${escapeHtml(question.explanation)}</p><div class="rationale-list">${question.options.map((option, i) => `<article class="rationale ${i === question.correct_index ? "keyed" : ""} ${i === answer.selected_index ? "selected-rationale" : ""}"><div><span>${i + 1}</span><strong>${escapeHtml(option)}</strong>${i === question.correct_index ? "<em>Keyed</em>" : ""}${i === answer.selected_index ? "<em>Your choice</em>" : ""}</div><p>${escapeHtml(question.choice_rationales[i])}</p></article>`).join("")}</div>${sourceDetailsTemplate(question)}</div></details>`;
}

function reviewView() {
  return `<main class="review shell"><section class="page-heading"><div><p class="eyebrow">Reviewer mode</p><h1>Manual review queue</h1><p>These sources remain local and are excluded from every scored session.</p></div><button class="secondary" data-action="export-review">Export queue</button></section><div class="review-grid">${state.reviewQueue.items.map((item) => `<article class="review-card panel"><img src="${escapeHtml(item.preview_asset)}" alt="review-only source preview"><div><span class="review-status">Needs review</span><h2>${escapeHtml(item.proposed_answer)}</h2><p>${escapeHtml(item.uncertainty_reason)}</p><dl><dt>Modality</dt><dd>${escapeHtml(item.modality)}</dd><dt>Evidence</dt><dd>${escapeHtml(item.evidence)}</dd><dt>Leak risk</dt><dd>${escapeHtml(item.answer_leakage_risk)}</dd><dt>Source ID</dt><dd>${escapeHtml(item.source_id)}</dd></dl></div></article>`).join("")}</div></main>`;
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
  state.selectedIndex = null;
  state.answers = {};
  state.examComplete = false;
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
    const answer = lockAnswer(question, currentAnswer(), state.selectedIndex);
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
  if (!currentAnswer()?.locked) return submitAnswer();
  if (state.position < state.session.questions.length - 1) {
    state.position += 1;
    state.selectedIndex = null;
    state.showingOriginal = false;
    resetZoom();
    render();
    return;
  }
  if (state.session.endless) {
    const next = createSession(state.bank.questions, { mode: state.session.mode, category: state.session.category, stateFilter: "all", length: "endless" }, state.progress, state.session.seed + 1);
    state.session.questions.push(...next.questions);
    state.position += 1;
    state.selectedIndex = null;
    resetZoom();
    render();
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
  if (event.target.id !== "session-form") return;
  event.preventDefault();
  const form = new FormData(event.target);
  startSession({ mode: form.get("mode"), category: form.get("category"), stateFilter: form.get("stateFilter"), length: form.get("length") });
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
  if (action === "choose" && !currentAnswer()?.locked) { state.selectedIndex = Number(target.dataset.index); render(); }
  if (action === "submit") submitAnswer();
  if (action === "next") nextQuestion();
  if (action === "mark") { state.progress = toggleMarked(state.progress, currentQuestion().question_id); saveProgress(); render(); }
  if (action === "zoom-in") adjustZoom(0.25);
  if (action === "zoom-out") adjustZoom(-0.25);
  if (action === "reset-zoom") { resetZoom(); render(); }
  if (action === "toggle-zoom") { state.zoom = state.zoom.scale > 1 ? { scale: 1, x: 0, y: 0 } : { scale: 2, x: 0, y: 0 }; render(); }
  if (action === "toggle-original") { state.showingOriginal = !state.showingOriginal; resetZoom(); render(); }
  if (action === "export") downloadJson(`pulmonary-id-progress-${new Date().toISOString().slice(0, 10)}.json`, state.progress);
  if (action === "export-review") downloadJson("pulmonary-picture-review-queue.json", state.reviewQueue);
  if (action === "reset-progress" && confirm("Reset all local quiz progress? The source bank will not be changed.")) { state.progress = emptyProgress(); saveProgress(); render(); }
  if (action === "retry-missed") {
    const missed = state.session.questions.filter((question) => state.answers[question.question_id] && !state.answers[question.question_id].correct);
    startSession({ mode: "learn", category: "all", stateFilter: "all", length: "all" }, missed);
  }
});

window.addEventListener("keydown", (event) => {
  if (state.view !== "quiz" || event.metaKey || event.ctrlKey || event.altKey) return;
  if (["1", "2", "3", "4"].includes(event.key) && !currentAnswer()?.locked) {
    state.selectedIndex = Number(event.key) - 1;
    render();
  }
  if (event.key === "Enter") {
    event.preventDefault();
    currentAnswer()?.locked ? nextQuestion() : submitAnswer();
  }
  if (event.key.toLowerCase() === "z") {
    state.zoom = state.zoom.scale > 1 ? { scale: 1, x: 0, y: 0 } : { scale: 2, x: 0, y: 0 };
    render();
  }
});

async function init() {
  try {
    const [bank, reviewQueue] = await Promise.all([
      fetch("data/question-bank.json").then((response) => response.json()),
      fetch("data/review-queue.json").then((response) => response.json()),
    ]);
    state.bank = bank;
    state.reviewQueue = reviewQueue;
    render();
  } catch (error) {
    app.innerHTML = `<main class="load-error"><h1>Unable to load the local bank</h1><p>${escapeHtml(error.message)}</p><p>Start the app through the documented local server; do not open index.html with file://.</p></main>`;
  }
}

init();
