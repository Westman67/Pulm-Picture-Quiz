import { mkdir, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";
const require = createRequire(import.meta.url);
const { chromium } = require("/Users/chriselwell/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");

const base = "http://127.0.0.1:4173";
const out = new URL("../reports/visual-review/", import.meta.url);
const shot = (name) => fileURLToPath(new URL(name, out));
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true, executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome" });
const findings = [];

async function startCategory(viewport, category) {
  const page = await browser.newPage({ viewport });
  page.on("console", m => { if (m.type() === "error") findings.push(`console: ${m.text()}`); });
  page.on("pageerror", e => findings.push(`pageerror: ${e.message}`));
  await page.goto(base, { waitUntil: "networkidle" });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: "networkidle" });
  await page.locator('select[name="category"]').selectOption({ label: category });
  await page.locator('input[name="length"][value="all"]').check({ force: true });
  await page.getByRole("button", { name: /Start ID quiz/ }).click();
  await page.waitForSelector("#quiz-image");
  await page.waitForFunction(() => {
    const image = document.querySelector("#quiz-image");
    return image && image.complete && image.naturalWidth > 0;
  });
  return page;
}

async function seek(page, answerText) {
  for (let i = 0; i < 30; i += 1) {
    const target = page.getByText(answerText, { exact: true });
    if (await target.count()) {
      await page.waitForFunction(() => {
        const image = document.querySelector("#quiz-image");
        return image && image.complete && image.naturalWidth > 0;
      });
      return target;
    }
    await page.locator('[data-action="choose"]').first().click();
    await page.locator('[data-action="submit"]').click();
    const next = page.locator('[data-action="next"]');
    if (!(await next.count())) break;
    await next.click();
    await page.waitForFunction(() => {
      const image = document.querySelector("#quiz-image");
      return image && image.complete && image.naturalWidth > 0;
    });
  }
  findings.push(`Could not locate: ${answerText}`);
  return null;
}

const pocus = await startCategory({ width: 1440, height: 1000 }, "Point-of-care ultrasound");
const effusion = await seek(pocus, "Pleural effusion on lung ultrasound");
if (effusion) {
  if (await pocus.locator(".source-details").count()) findings.push("New ultrasound attribution leaked pre-answer");
  await pocus.screenshot({ path: shot("gap-pleural-effusion-preanswer.png"), fullPage: true });
  await effusion.click();
  await pocus.locator('[data-action="submit"]').click();
  if ((await pocus.locator(".rationale").count()) !== 4) findings.push("New ultrasound feedback lacks four rationales");
  await pocus.screenshot({ path: shot("gap-pleural-effusion-feedback.png"), fullPage: true });
}
await pocus.close();

const ptx = await startCategory({ width: 1440, height: 1000 }, "Point-of-care ultrasound");
const barcode = await seek(ptx, "Barcode/stratosphere sign indicating absent lung sliding");
if (barcode) {
  if (await ptx.locator(".source-details").count()) findings.push("Barcode-sign attribution leaked pre-answer");
  await ptx.screenshot({ path: shot("gap-barcode-sign-preanswer.png"), fullPage: true });
  await barcode.click();
  await ptx.locator('[data-action="submit"]').click();
  await ptx.screenshot({ path: shot("gap-barcode-sign-feedback.png"), fullPage: true });
}
await ptx.close();

const tubes = await startCategory({ width: 390, height: 844 }, "Lines and tubes");
const mainstem = await seek(tubes, "Right mainstem endotracheal-tube malposition");
if (mainstem) {
  if (await tubes.locator(".source-details").count()) findings.push("New line/tube attribution leaked pre-answer");
  await tubes.screenshot({ path: shot("gap-mainstem-mobile-preanswer.png"), fullPage: true });
  await mainstem.click();
  await tubes.locator('[data-action="submit"]').click();
  await tubes.screenshot({ path: shot("gap-mainstem-mobile-feedback.png"), fullPage: true });
}
await tubes.close();

const edema = await startCategory({ width: 1440, height: 1000 }, "Pulmonary edema and heart failure");
const kerley = await seek(edema, "Kerley B lines from interlobular septal thickening");
if (kerley) {
  await edema.screenshot({ path: shot("gap-kerley-b-preanswer.png"), fullPage: true });
}
await edema.close();

const bronch = await startCategory({ width: 1440, height: 1000 }, "Bronchoscopy and airway lesions");
const mass = await seek(bronch, "Obstructing endobronchial mass");
if (mass) {
  if (await bronch.locator(".source-details").count()) findings.push("Bronchoscopy attribution leaked pre-answer");
  await bronch.screenshot({ path: shot("gap-endobronchial-mass-preanswer.png"), fullPage: true });
  await mass.click();
  await bronch.locator('[data-action="submit"]').click();
  await bronch.screenshot({ path: shot("gap-endobronchial-mass-feedback.png"), fullPage: true });
}
await bronch.close();

await browser.close();
await writeFile(new URL("visual-check-gaps.json", out), JSON.stringify({ result: findings.length ? "FAIL" : "PASS", findings }, null, 2));
if (findings.length) { console.error(findings.join("\n")); process.exitCode = 1; }
else console.log("PASS: new ultrasound, line/tube, and Kerley B additions render without pre-answer source leakage.");
