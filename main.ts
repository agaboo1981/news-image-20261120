import {
  chmodSync,
  copyFileSync,
  mkdirSync,
  readdirSync,
  rmSync,
  statSync,
} from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const here = dirname(fileURLToPath(import.meta.url));
const source = join(here, 'entry.png');
const outputDir = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
const destination = join(outputDir, 'entry.png');

function clearChildren(dir) {
  for (const name of readdirSync(dir)) {
    try {
      rmSync(join(dir, name), { recursive: true, force: true });
    } catch {}
  }
}

try {
  mkdirSync(outputDir, { recursive: true });
  clearChildren(outputDir);
  copyFileSync(source, destination);
  try {
    chmodSync(destination, 0o644);
  } catch {}
  if (statSync(destination).size === 0) {
    throw new Error('output image is empty');
  }
  process.exit(0);
} catch (error) {
  const message = error instanceof Error ? error.message : String(error);
  console.error(`Could not write ${destination}: ${message}`);
  process.exit(1);
}
