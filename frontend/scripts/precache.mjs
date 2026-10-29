import { createHash } from "node:crypto";
import { readFile, readdir, writeFile } from "node:fs/promises";
import { resolve } from "node:path";

const dist = resolve("dist");
async function files(directory, prefix = "") {
  const result = [];
  for (const entry of await readdir(directory, { withFileTypes: true })) {
    const name = `${prefix}${entry.name}`;
    if (entry.isDirectory())
      result.push(...(await files(resolve(directory, entry.name), `${name}/`)));
    else if (name !== "sw.js") result.push(name);
  }
  return result.sort();
}
const paths = await files(dist);
const digest = createHash("sha256");
for (const path of paths) digest.update(await readFile(resolve(dist, path)));
const revision = digest.digest("hex").slice(0, 16);
const source = await readFile(resolve(dist, "sw.js"), "utf8");
const precache = paths.map((path) =>
  path === "index.html" ? "/" : `/${path}`,
);
await writeFile(
  resolve(dist, "sw.js"),
  source
    .replace("vertical-shell-v1", `vertical-shell-${revision}`)
    .replace(
      /const PRECACHE = .*;/,
      `const PRECACHE = ${JSON.stringify(precache)};`,
    ),
);
console.log(`PWA: precached ${precache.length} public assets (${revision})`);
