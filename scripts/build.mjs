import { cp, mkdir, rm, stat } from "node:fs/promises";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

const project = fileURLToPath(new URL("..", import.meta.url));
const dist = join(project, "dist");
await rm(dist, { recursive: true, force: true });
await mkdir(dist, { recursive: true });
for (const name of ["index.html", "src", "data", "public"]) {
  await cp(join(project, name), join(dist, name), { recursive: true });
}
const info = await stat(join(dist, "data", "question-bank.json"));
console.log(`Production build ready at ${dist} (${info.size} byte bank).`);
