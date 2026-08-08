/**
 * @license
 * Copyright 2026 OpenWork SkillHub
 * SPDX-License-Identifier: Apache-2.0
 *
 * generate-packages.mjs
 *
 * One-time helper that stages the OpenWork-authored skill packages into this
 * OpenWork repo (`src/process/resources/skills/<name>/`) into this SkillHub
 * repo's `_pkgs/<name>/` staging area, and writes a correct
 * `openwork-extension.json` manifest for each (with `contributes.skills`
 * pointing at the package-root `SKILL.md`).
 *
 * After running this, commit `_pkgs/` and run `build-hub-catalog.mjs` to
 * (re)generate `index.json` + `extensions/*.tgz`.
 *
 * Usage:
 *   node scripts/generate-packages.mjs [--src <openwork-skills-dir>]
 *
 * The `--src` defaults to the path below (the OpenWork repo's bundled skills).
 */

import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const repoRoot = path.resolve(__dirname, '..');
const pkgsDir = path.join(repoRoot, '_pkgs');

const args = process.argv.slice(2);
const srcIdx = args.indexOf('--src');
const DEFAULT_SRC = '/Users/myking/workspaces/claude-projects/openwork/src/process/resources/skills';
const srcRoot = srcIdx >= 0 ? args[srcIdx + 1] : DEFAULT_SRC;

const SKILLS = [
  'agent-browser-core',
  'gongzhonghao-daily-v1',
  'grill-me',
  'humanizer',
  'ima-skills',
  'minimax-xlsx',
  'nano-banana-pro',
  'obsidian',
  'playwright-browser-automation',
  'qqbrowser-skill',
  'tencent-docs',
  'tencentcloud-ocr',
  'wecom-unified',
];

// Files / dirs that must never be copied into a published package.
const EXCLUDE_NAMES = new Set(['node_modules', '__pycache__', '.git', '.DS_Store', 'package-lock.json', 'yarn.lock', '_skillhub_meta.json', '_icon.png', 'thumbs.db']);
function isExcluded(relPath) {
  const parts = relPath.split(path.sep);
  return parts.some((p) => EXCLUDE_NAMES.has(p) || p.startsWith('.'));
}

/** Minimal YAML frontmatter scalar reader — good enough for our needs. */
function parseFrontmatter(md) {
  const m = md.match(/^---\s*\n([\s\S]*?)\n---/);
  if (!m) return {};
  const block = m[1];
  const out = {};
  for (const raw of block.split('\n')) {
    if (!raw.includes(':')) continue;
    const idx = raw.indexOf(':');
    const key = raw.slice(0, idx).trim();
    let val = raw.slice(idx + 1).trim();
    if ((val.startsWith('"') && val.endsWith('"')) || (val.startsWith("'") && val.endsWith("'"))) {
      val = val.slice(1, -1);
    }
    if (key && val && !(key in out)) out[key] = val;
  }
  return out;
}

function copyRecursive(src, dest, relBase = '') {
  const stat = fs.statSync(src);
  if (stat.isDirectory()) {
    if (isExcluded(relBase)) return;
    fs.mkdirSync(dest, { recursive: true });
    for (const entry of fs.readdirSync(src)) {
      copyRecursive(path.join(src, entry), path.join(dest, entry), path.join(relBase, entry));
    }
  } else {
    if (isExcluded(relBase)) return;
    fs.mkdirSync(path.dirname(dest), { recursive: true });
    fs.copyFileSync(src, dest);
  }
}

function firstPresent(obj, keys) {
  for (const k of keys) if (obj[k]) return obj[k];
  return '';
}

function truncate(s, n) {
  if (!s) return s;
  return s.length > n ? s.slice(0, n - 1).trimEnd() + '…' : s;
}

if (!fs.existsSync(srcRoot)) {
  console.error(`[generate-packages] Source skills dir not found: ${srcRoot}`);
  process.exit(1);
}

fs.mkdirSync(pkgsDir, { recursive: true });

let ok = 0;
for (const name of SKILLS) {
  const srcDir = path.join(srcRoot, name);
  const skillMd = path.join(srcDir, 'SKILL.md');
  if (!fs.existsSync(skillMd)) {
    console.warn(`[generate-packages] Skipping "${name}": no SKILL.md at ${skillMd}`);
    continue;
  }
  const fm = parseFrontmatter(fs.readFileSync(skillMd, 'utf-8'));

  const pkgDir = path.join(pkgsDir, name);
  fs.rmSync(pkgDir, { recursive: true, force: true });
  fs.mkdirSync(pkgDir, { recursive: true });
  copyRecursive(srcDir, pkgDir, name);

  // Friendly marketplace display names for skills that ship only a raw kebab name.
  const DISPLAY_NAME_OVERRIDES = {
    'gongzhonghao-daily-v1': '公众号日更 (WeChat Official Account Daily)',
    'grill-me': 'Grill Me (需求深挖访谈)',
    humanizer: 'Humanizer (去 AI 味)',
    'playwright-browser-automation': 'Playwright Browser Automation',
  };
  const displayName = DISPLAY_NAME_OVERRIDES[name] || firstPresent(fm, ['display_name_en', 'display_name', 'name']) || name;
  const version = (fm.version || '1.0.0').replace(/^v/, '');
  const description = truncate(firstPresent(fm, ['description_en', 'description_zh', 'description']), 280);
  const author = fm.author || 'OpenWork';

  const manifest = {
    name,
    displayName,
    version,
    description,
    author,
    apiVersion: '^1.0.0',
    engines: { openwork: '^1.0.0' },
    contributes: {
      skills: [
        {
          name,
          description: description || `Skill from ${name}`,
          file: 'SKILL.md',
        },
      ],
    },
  };

  fs.writeFileSync(path.join(pkgDir, 'openwork-extension.json'), JSON.stringify(manifest, null, 2) + '\n');
  const fileCount = (function count(dir) {
    let n = 0;
    for (const e of fs.readdirSync(dir, { withFileTypes: true })) {
      const p = path.join(dir, e.name);
      if (e.isDirectory()) n += count(p);
      else n += 1;
    }
    return n;
  })(pkgDir);
  console.log(`[generate-packages] ${name} -> ${fileCount} files, v${version}, "${displayName}"`);
  ok += 1;
}

console.log(`[generate-packages] Done. Packaged ${ok}/${SKILLS.length} skills into ${pkgsDir}`);
