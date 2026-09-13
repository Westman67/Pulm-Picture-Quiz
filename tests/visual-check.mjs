import { mkdir, writeFile } from "node:fs/promises";
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
await desktop.screenshot({ path: shot("desktop-learn-preanswer.png"), fullPage: true });
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
  console.log("PASS: desktop/mobile, Learn/Exam reveal timing, locking, zoom, and results states verified.");
}
