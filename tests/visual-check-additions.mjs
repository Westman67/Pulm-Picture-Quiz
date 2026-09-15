import { mkdir, writeFile } from "node:fs/promises";
import { createRequire } from "node:module";
import { fileURLToPath } from "node:url";

const require = createRequire(import.meta.url);
const { chromium } = require("/Users/chriselwell/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules/playwright");

const base = "http://127.0.0.1:4173";
const out = new URL("../reports/visual-review/additions/", import.meta.url);
const shot = (name) => fileURLToPath(new URL(name, out));
await mkdir(out, { recursive: true });

const cases = [
  { slug: "epiglottitis", category: "Upper-airway imaging", stem: "enlarged thumb-shaped epiglottic shadow", answer: "Acute epiglottitis with a thumb sign" },
  { slug: "dvt-ultrasound", category: "Venous thromboembolism", stem: "failure to collapse indicate", answer: "Acute deep venous thrombosis" },
  { slug: "saddle-pe", category: "Venous thromboembolism", stem: "spanning the pulmonary-artery bifurcation", answer: "Saddle pulmonary embolism" },
  { slug: "pancoast", category: "Lung cancer", stem: "right apical mass extending", answer: "Pancoast tumor with chest-wall extension" },
  { slug: "diaphragmatic-rupture", category: "Thoracic trauma", stem: "bowel loops in the left hemithorax", answer: "Left diaphragmatic rupture with bowel herniation" },
  { slug: "pulmonary-contusion", category: "Thoracic trauma", stem: "irregular peripheral nonlobar opacity", answer: "Pulmonary contusion" },
  { slug: "ttn", category: "Neonatal lung disease", stem: "perihilar streaking, and fissural fluid", answer: "Transient tachypnea of the newborn" },
  { slug: "split-pleura", category: "Pleural infection", stem: "enhancing pleural layers surrounding", answer: "Split pleura sign of empyema" },
  { slug: "nsip", category: "Interstitial lung disease", stem: "interstitial-lung-disease pattern", answer: "Nonspecific interstitial pneumonia pattern" },
  { slug: "tree-in-bud", category: "Small-airway infection", stem: "branching peripheral opacities and their nodular tips", answer: "Tree-in-bud pattern" },
  { slug: "pneumocystis", category: "Opportunistic infection", stem: "paired H&E and silver-stained sections", answer: "Pneumocystis jirovecii pneumonia" },
  { slug: "retropharyngeal-abscess", category: "Upper-airway infection", stem: "deep neck-space infection", answer: "Retropharyngeal abscess" },
  { slug: "svc-syndrome", category: "Lung cancer complications", stem: "intrathoracic obstruction and upper-body venous findings", answer: "Superior vena cava syndrome" },
  { slug: "traumatic-hemothorax", category: "Thoracic trauma", stem: "traumatic pleural diagnosis", answer: "Traumatic hemothorax" },
  { slug: "pathoma-ghon-focus", category: "Tuberculosis", stem: "gross pulmonary lesion", answer: "Ghon focus of primary tuberculosis" },
  { slug: "pathoma-caseating-granuloma", category: "Tuberculosis", stem: "pathologic process", answer: "Caseating granuloma of tuberculosis" },
  { slug: "pathoma-lateral-emphysema", category: "COPD imaging", stem: "lateral chest-radiograph appearance", answer: "Emphysema with increased anteroposterior diameter" },
  { slug: "pathoma-plexiform-lesion", category: "Pulmonary vascular disease", stem: "pulmonary vascular lesion", answer: "Plexiform lesion of pulmonary arterial hypertension" },
  { slug: "pathoma-adenocarcinoma-mucin", category: "Lung cancer", stem: "lung-cancer subtype", answer: "Pulmonary adenocarcinoma with gland formation and mucin" },
  { slug: "pathoma-lepidic-growth", category: "Lung cancer", stem: "neoplastic growth pattern", answer: "Lepidic growth pattern of pulmonary adenocarcinoma" },
  { slug: "pathoma-carcinoid-ihc", category: "Lung cancer", stem: "immunohistochemical pattern", answer: "Chromogranin-positive pulmonary carcinoid tumor" },
  { slug: "pathoma-carcinoid-gross", category: "Lung cancer", stem: "gross airway lesion", answer: "Endobronchial pulmonary carcinoid tumor" },
];

const browser = await chromium.launch({
  headless: true,
  executablePath: "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
});
const findings = [];

async function openCase(item, viewport) {
  const page = await browser.newPage({ viewport });
  page.on("console", (message) => { if (message.type() === "error") findings.push(`${item.slug}: console: ${message.text()}`); });
  page.on("pageerror", (error) => findings.push(`${item.slug}: pageerror: ${error.message}`));
  await page.goto(base, { waitUntil: "networkidle" });
  await page.evaluate(() => localStorage.clear());
  await page.reload({ waitUntil: "networkidle" });
  await page.locator('select[name="category"]').selectOption({ label: item.category });
  await page.locator('input[name="length"][value="all"]').check({ force: true });
  await page.getByRole("button", { name: /Start ID quiz/ }).click();
  await page.waitForSelector("#quiz-image");

  let found = false;
  for (let index = 0; index < 40; index += 1) {
    const stem = await page.locator(".question-heading h1").textContent();
    if (stem?.includes(item.stem)) {
      found = true;
      break;
    }
    const next = page.locator('[data-action="next"]');
    if (!(await next.count()) || /summary|finish/i.test(await next.textContent())) break;
    await next.click();
  }
  if (!found) {
    findings.push(`${item.slug}: target question not found in ${item.category}`);
    await page.close();
    return;
  }

  await page.waitForFunction(() => {
    const image = document.querySelector("#quiz-image");
    return image && image.complete && image.naturalWidth > 0 && image.naturalHeight > 0;
  });
  const metrics = await page.locator("#quiz-image").evaluate((image) => {
    const box = image.getBoundingClientRect();
    return { naturalRatio: image.naturalWidth / image.naturalHeight, renderedRatio: box.width / box.height };
  });
  if (Math.abs(metrics.naturalRatio / metrics.renderedRatio - 1) > 0.015) findings.push(`${item.slug}: image appears distorted`);
  if (!(await page.locator(".case-context").count())) findings.push(`${item.slug}: clinical context is missing`);
  const visualTarget = await page.locator(".visual-target").textContent();
  if (!visualTarget || /complete displayed image$/i.test(visualTarget.trim())) findings.push(`${item.slug}: visual target is not specific`);
  if ((await page.locator('[data-action="previous"]').count()) !== 1 || (await page.locator('[data-action="next"]').count()) !== 1) {
    findings.push(`${item.slug}: persistent Back/Next controls are missing`);
  }
  if (await page.locator(".feedback").count()) findings.push(`${item.slug}: answer feedback leaked before submission`);
  await page.screenshot({ path: shot(`${item.slug}-preanswer.png`), fullPage: true });

  const option = page.locator('[data-action="choose"]').filter({ hasText: item.answer });
  if ((await option.count()) !== 1) {
    findings.push(`${item.slug}: keyed choice was not uniquely selectable`);
  } else {
    await option.click();
    await page.locator('[data-action="submit"]').click();
    if ((await page.locator(".feedback").count()) !== 1) findings.push(`${item.slug}: Learn feedback missing after answer lock`);
    if ((await page.locator(".rationale").count()) !== 4) findings.push(`${item.slug}: four aligned rationales are not visible`);
  }
  await page.close();
}

for (const [index, item] of cases.entries()) {
  await openCase(item, index === 1 ? { width: 390, height: 844 } : { width: 1440, height: 1000 });
}

await browser.close();
await writeFile(new URL("visual-check-additions.json", out), JSON.stringify({ result: findings.length ? "FAIL" : "PASS", checked: cases.map((item) => item.slug), findings }, null, 2));
if (findings.length) {
  console.error(findings.join("\n"));
  process.exitCode = 1;
} else {
  console.log("PASS: all fourteen retained full-comparison additions and all eight Pathoma additions render naturally with specific targets, clinical context, persistent navigation, and four-rationale feedback.");
}
