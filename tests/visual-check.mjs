import { mkdir, readFile, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require("/Users/chriselwell/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");

const base = "http://127.0.0.1:4173";
const out = new URL("../reports/visual-review/", import.meta.url);
const shot = (name) => fileURLToPath(new URL(name, out));
await mkdir(out, { recursive: true });
const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const findings = [];

async function newPage(viewport) {
  const page = await browser.newPage({ viewport });
  page.on("console", (message) => {
    if (message.type() === "error") findings.push(`console: ${message.text()}`);
  });
  page.on("pageerror", (error) => findings.push(`pageerror: ${error.message}`));
  await page.goto(base, { waitUntil: "networkidle" });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: "networkidle" });
  return page;
}

const desktop = await newPage({ width: 1440, height: 1000 });
await desktop.screenshot({ path: shot("desktop-home.png"), fullPage: true });
await desktop.locator('input[name="length"][value="10"]').check({ force: true });
await desktop.getByRole("button", { name: /Start ID quiz/ }).click();
await desktop.waitForSelector("#quiz-image");
if (await desktop.locator(".feedback").count()) findings.push("Learn feedback leaked before submission");
if (await desktop.locator(".source-details").count()) findings.push("Source provenance leaked before submission");
if (!(await desktop.locator('[data-action="previous"]').isDisabled())) findings.push("Back is not disabled on the first question");
await desktop.screenshot({ path: shot("desktop-learn-preanswer.png"), fullPage: true });
await desktop.locator('[data-action="toggle-flag"]').click();
if ((await desktop.locator("#quality-flag-form").count()) !== 1) findings.push("Photo-flag form did not open from the quiz");
await desktop.screenshot({ path: shot("desktop-photo-flag-form.png"), fullPage: true });
await desktop.locator('#quality-flag-form select[name="issueType"]').selectOption("cropped-incomplete");
const flagNote = desktop.locator('#quality-flag-form textarea[name="note"]');
await flagNote.fill("Automated check: panel ");
await flagNote.press("1");
await flagNote.pressSequentially(" should preserve the complete photo.");
if ((await desktop.locator('.choice[aria-checked="true"]').count()) !== 0) findings.push("Typing a number in the photo-flag note selected a quiz answer");
await desktop.locator('#quality-flag-form button[type="submit"]').click();
if (!/Photo flagged/.test(await desktop.locator('[data-action="toggle-flag"]').textContent())) findings.push("Saved photo flag is not reflected on the quiz button");
await desktop.locator('[data-action="choose"]').nth(1).click();
await desktop.locator('[data-action="next"]').click();
if (await desktop.locator(".feedback").count()) findings.push("Skipping with Next unexpectedly locked or revealed the first answer");
await desktop.locator('[data-action="previous"]').click();
if ((await desktop.locator('.choice[aria-checked="true"]').count()) !== 1) findings.push("Draft selection was not restored after Back navigation");
if (await desktop.locator(".feedback").count()) findings.push("Unsubmitted draft was converted into feedback after Back navigation");
if (!/Photo flagged/.test(await desktop.locator('[data-action="toggle-flag"]').textContent())) findings.push("Photo flag did not survive question navigation");
await desktop.locator('[data-action="zoom-in"]').click();
const transform = await desktop.locator("#quiz-image").getAttribute("style");
if (!transform?.includes("scale(1.25)")) findings.push("Zoom control did not update the image transform");
await desktop.locator('[data-action="choose"]').first().click();
await desktop.locator('[data-action="submit"]').click();
if (!(await desktop.locator(".feedback").count())) findings.push("Learn feedback missing after submission");
if ((await desktop.locator(".rationale").count()) !== 4) findings.push("Learn feedback does not show four rationales");
if (!(await desktop.locator(".source-details").count())) findings.push("Post-answer provenance is missing");
if (!(await desktop.locator(".choice:disabled").count())) findings.push("Choices were not locked after submission");
await desktop.screenshot({ path: shot("desktop-learn-feedback.png"), fullPage: true });

await desktop.locator('[data-action="review"]').click();
if ((await desktop.locator(".quality-flag-card.open").count()) !== 1) findings.push("Saved photo flag is missing from Review & flags");
if (!(await desktop.getByText("Automated check: panel 1 should preserve the complete photo.", { exact: true }).count())) findings.push("Photo-flag note was not preserved");
await desktop.screenshot({ path: shot("desktop-review-photo-flags.png"), fullPage: true });
const flagDownloadPromise = desktop.waitForEvent("download");
await desktop.locator('[data-action="export-flags"]').click();
const flagDownload = await flagDownloadPromise;
const flagExport = JSON.parse(await readFile(await flagDownload.path(), "utf8"));
if (flagExport.schema_version !== 1 || Object.keys(flagExport.flags || {}).length !== 1) findings.push("Photo-flag export did not contain the saved versioned record");
await desktop.locator('[data-action="set-flag-status"]').click();
if ((await desktop.locator(".quality-flag-card.resolved").count()) !== 1) findings.push("Photo flag could not be marked fixed");
await desktop.locator('[data-action="set-flag-status"]').click();
if ((await desktop.locator(".quality-flag-card.open").count()) !== 1) findings.push("Resolved photo flag could not be reopened");
await desktop.locator('[data-action="home"]').first().click();
await desktop.locator('input[name="mode"][value="exam"]').check({ force: true });
await desktop.locator('input[name="length"][value="10"]').check({ force: true });
await desktop.getByRole("button", { name: /Start ID quiz/ }).click();
for (let index = 0; index < 10; index += 1) {
  await desktop.locator('[data-action="choose"]').first().click();
  await desktop.locator('[data-action="submit"]').click();
  if (index === 0) {
    if (await desktop.locator(".feedback").count()) findings.push("Exam feedback leaked after answer submission");
    if (await desktop.locator(".rationale").count()) findings.push("Exam rationales leaked before completion");
    await desktop.screenshot({ path: shot("desktop-exam-locked.png"), fullPage: true });
  }
  await desktop.locator('[data-action="next"]').click();
}
await desktop.waitForSelector(".results-hero");
if (!(await desktop.locator(".result-card").count())) findings.push("Exam result review cards missing");
await desktop.screenshot({ path: shot("desktop-exam-results.png"), fullPage: true });
await desktop.close();

const mobile = await newPage({ width: 390, height: 844 });
await mobile.screenshot({ path: shot("mobile-home.png"), fullPage: true });
await mobile.locator('input[name="length"][value="10"]').check({ force: true });
await mobile.getByRole("button", { name: /Start ID quiz/ }).click();
await mobile.waitForSelector("#quiz-image");
await mobile.screenshot({ path: shot("mobile-quiz.png"), fullPage: true });
await mobile.close();

const sourceFilter = await newPage({ width: 1200, height: 900 });
await sourceFilter.locator('select[name="sourceOrigin"]').selectOption("third_party");
await sourceFilter.locator('input[name="length"][value="all"]').check({ force: true });
await sourceFilter.screenshot({ path: shot("desktop-third-party-filter.png"), fullPage: true });
await sourceFilter.getByRole("button", { name: /Start ID quiz/ }).click();
await sourceFilter.waitForSelector("#quiz-image");
if (!(await sourceFilter.getByText("1 / 51", { exact: true }).count())) findings.push("Third-party source filter did not produce the expected 51-question session");
if (!/Third party/.test(await sourceFilter.locator(".category-label").textContent())) findings.push("Third-party provenance is not shown on the quiz question");
await sourceFilter.locator('[data-action="home"]').first().click();
await sourceFilter.locator('select[name="sourceOrigin"]').selectOption("lecture");
await sourceFilter.locator('input[name="length"][value="all"]').check({ force: true });
await sourceFilter.screenshot({ path: shot("desktop-lecture-filter.png"), fullPage: true });
await sourceFilter.getByRole("button", { name: /Start ID quiz/ }).click();
await sourceFilter.waitForSelector("#quiz-image");
if (!(await sourceFilter.getByText("1 / 225", { exact: true }).count())) findings.push("Lecture source filter did not produce the expected 225-question session");
if (!/Lecture/.test(await sourceFilter.locator(".category-label").textContent())) findings.push("Lecture provenance is not shown on the quiz question");
await sourceFilter.close();

const supplement = await newPage({ width: 1440, height: 1000 });
await supplement.locator('select[name="category"]').selectOption({ label: "Point-of-care ultrasound" });
await supplement.locator('input[name="length"][value="all"]').check({ force: true });
await supplement.getByRole("button", { name: /Start ID quiz/ }).click();
await supplement.waitForSelector("#quiz-image");
if (await supplement.locator(".source-details").count()) findings.push("Supplement attribution leaked before submission");
await supplement.screenshot({ path: shot("supplement-ultrasound-preanswer.png"), fullPage: true });
await supplement.locator('[data-action="choose"]').first().click();
await supplement.locator('[data-action="submit"]').click();
if ((await supplement.locator('.source-details a[href^="https://"]').count()) !== 1) findings.push("Supplement verified-source attribution link missing after submission");
await supplement.screenshot({ path: shot("supplement-ultrasound-feedback.png"), fullPage: true });
await supplement.close();

await browser.close();
await writeFile(new URL("visual-check.json", out), JSON.stringify({ result: findings.length ? "FAIL" : "PASS", findings }, null, 2));
if (findings.length) {
  console.error(findings.join("\n"));
  process.exitCode = 1;
} else {
  console.log("PASS: desktop/mobile, source filtering, Learn/Exam reveal timing, locking, zoom, results, and photo-flag workflow verified.");
}
