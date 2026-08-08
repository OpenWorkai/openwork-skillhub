/**
 * @license
 * Copyright 2026 OpenWork SkillHub
 * SPDX-License-Identifier: Apache-2.0
 *
 * build-hub-catalog.mjs
 *
 * Regenerates this SkillHub's marketplace catalog (`index.json` at the repo
 * root) from the unpacked extension packages under `_pkgs/<name>/`.
 *
 * For every package it:
 *   1. zips the package directory into `extensions/<name>.tgz`
 *   2. computes a sha512 integrity hash
 *   3. records a registry entry in `index.json` (schemaVersion 1)
 *
 * The output schema mirrors what OpenWork's `HubIndexManager` /
 * `HubInstaller` consume, so a fresh clone can rebuild the catalog locally
 * instead of relying on committed artifacts.
 *
 * IMPORTANT: The `.tgz` files produced here are ZIP archives (the consumer
 * reads them with a ZIP reader, e.g. yauzl). This matches the format expected
 * by OpenWork's installer — do NOT switch to a real gzip/tar stream, or the
 * installer will fail to extract them. Requires the system `zip` binary.
 *
 * Unlike OpenWork's in-repo `resources/hub` (which is gitignored and rebuilt
 * at build time), THIS repo commits both `index.json` and `extensions/*.tgz`
 * so the GitHub + jsDelivr CDN can serve them as a remote hub.
 *
 * Usage:
 *   node scripts/build-hub-catalog.mjs [--clean]
 *
 *   --clean   Remove the previously generated index.json + extensions/*.tgz
 *             before rebuilding (keeps the source `_pkgs` directory intact).
 */

import fs from 'fs';
import path from 'path';
import { execSync } from 'child_process';
import crypto from 'crypto';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..');
const pkgsDir = path.join(repoRoot, '_pkgs');
const extOutDir = path.join(repoRoot, 'extensions');
const indexPath = path.join(repoRoot, 'index.json');

const args = process.argv.slice(2);
const clean = args.includes('--clean');

function fail(message) {
  console.error(`[build-hub-catalog] ${message}`);
  process.exit(1);
}

if (!fs.existsSync(pkgsDir)) {
  fail(`Missing packages directory: ${pkgsDir}`);
}

// Verify the system `zip` binary is available before doing any work.
try {
  execSync('zip -v', { stdio: 'ignore' });
} catch {
  fail("The 'zip' binary is required but was not found on PATH. Install it (e.g. `brew install zip` on macOS) and retry.");
}

if (clean) {
  if (fs.existsSync(indexPath)) fs.rmSync(indexPath, { force: true });
  if (fs.existsSync(extOutDir)) {
    for (const entry of fs.readdirSync(extOutDir)) {
      if (entry.endsWith('.tgz')) fs.rmSync(path.join(extOutDir, entry), { force: true });
    }
  }
  console.log('[build-hub-catalog] Cleaned previous index.json + extensions/*.tgz');
}

fs.mkdirSync(extOutDir, { recursive: true });

const names = fs.readdirSync(pkgsDir).filter((n) => fs.statSync(path.join(pkgsDir, n)).isDirectory());

if (names.length === 0) {
  fail(`No packages found in ${pkgsDir}`);
}

const extensions = {};
for (const name of names) {
  const pkgDir = path.join(pkgsDir, name);
  const manifestPath = path.join(pkgDir, 'openwork-extension.json');
  if (!fs.existsSync(manifestPath)) {
    console.warn(`[build-hub-catalog] Skipping "${name}": missing openwork-extension.json`);
    continue;
  }
  const manifest = JSON.parse(fs.readFileSync(manifestPath, 'utf-8'));

  // Name must be kebab-case and not use reserved prefixes (validated by OpenWork at install).
  if (!/^[a-z0-9-]+$/.test(manifest.name || '')) {
    console.warn(`[build-hub-catalog] Skipping "${name}": manifest name "${manifest.name}" is not kebab-case`);
    continue;
  }

  const tgz = path.join(extOutDir, `${name}.tgz`);
  // ZIP the package contents (the "." includes everything at the package root,
  // which is how the installer expects to find openwork-extension.json etc.).
  execSync(`cd "${pkgDir}" && zip -r -q "${tgz}" .`, { stdio: 'ignore' });
  const buf = fs.readFileSync(tgz);
  const integrity = 'sha512-' + crypto.createHash('sha512').update(buf).digest('base64');

  const contributes = manifest.contributes || {};
  const hubCategories = Object.keys(contributes).length ? Object.keys(contributes) : ['skills'];

  extensions[name] = {
    name: manifest.name,
    displayName: manifest.displayName || manifest.name,
    version: manifest.version || '1.0.0',
    description: manifest.description || '',
    author: manifest.author || 'OpenWork',
    icon: manifest.icon,
    dist: { tarball: `extensions/${name}.tgz`, integrity, unpackedSize: buf.length },
    engines: manifest.engines || { openwork: '^1.0.0' },
    hubs: hubCategories,
    contributes,
    tags: [manifest.name],
  };
}

const builtNames = Object.keys(extensions);
if (builtNames.length === 0) {
  fail('No valid extension packages were found to build the catalog.');
}

const index = { schemaVersion: 1, generatedAt: new Date().toISOString(), extensions };
fs.writeFileSync(indexPath, JSON.stringify(index, null, 2) + '\n');
console.log(`[build-hub-catalog] Wrote index.json with ${builtNames.length} extensions: ${builtNames.join(', ')}`);
