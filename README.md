# OpenWork SkillHub

OpenWork 的远程技能市场（Remote Skill Marketplace）。本仓库以 **OpenWork 名义独立编写并维护**一批能力型技能，将其打包为 OpenWork 扩展（Extension），通过 GitHub + jsDelivr CDN 以 `index.json` + `extensions/*.tgz` 的形式对外发布。OpenWork 客户端配置 `OPENWORK_HUB_URL` 后即可在「插件 / 技能市场」中浏览、安装、更新这些技能。

> 本仓库零客户端代码改动，完全基于 OpenWork 已有的 Extension Hub 机制对外提供扩展。

## 当前收录的技能（13 个）

| 技能 ID | 名称 | 版本 |
| --- | --- | --- |
| `agent-browser-core` | Agent Browser Core | 1.0.2 |
| `gongzhonghao-daily-v1` | 公众号日更 (WeChat Official Account Daily) | 1.0.0 |
| `grill-me` | Grill Me (需求深挖访谈) | 1.0.0 |
| `humanizer` | Humanizer (去 AI 味) | 2.1.1 |
| `ima-skills` | Ima Skills | 1.1.9 |
| `minimax-xlsx` | minimax-xlsx | 1.0.0 |
| `nano-banana-pro` | nano-banana-pro | 1.0.1 |
| `obsidian` | obsidian | 1.0.0 |
| `playwright-browser-automation` | Playwright Browser Automation | 2.0.0 |
| `qqbrowser-skill` | QQ Browser Use | 1.0.7 |
| `tencent-docs` | Tencent Docs | 1.0.36 |
| `tencentcloud-ocr` | Tencent Cloud General OCR (High Accuracy) | 1.0.4 |
| `wecom-unified` | Wecom Unified | 1.0.2 |

## 仓库结构

```
openwork-skillhub/
├── README.md
├── LICENSE
├── .gitignore
├── index.json                 # 市场目录（schemaVersion 1），由 build 脚本生成并提交
├── extensions/                # 各扩展的 .tgz（ZIP 格式），由 build 脚本生成并提交
│   ├── agent-browser-core.tgz
│   └── ...
├── _pkgs/                     # 扩展源（已提交，便于复现）
│   └── <skill-name>/
│       ├── openwork-extension.json   # 扩展清单（含 contributes.skills）
│       ├── SKILL.md                  # 技能定义
│       └── ...（references/scripts/assets 等）
└── scripts/
    ├── generate-packages.mjs # 把源技能打包进 _pkgs/（一次性辅助脚本）
    └── build-hub-catalog.mjs # 由 _pkgs/ 生成 index.json + extensions/*.tgz
```

## 消费方式（在 OpenWork 侧）

```bash
# 启动 OpenWork 前设置，注意末尾的斜杠 "/"
export OPENWORK_HUB_URL="https://cdn.jsdelivr.net/gh/OpenWorkai/openwork-skillhub@v1.1.0/"

# 正常启动 OpenWork（以 bun 为例）
bun run start
```

- `OPENWORK_HUB_URL` 支持逗号分隔的多个基址（按顺序回退）。
- 基址**必须**以 `/` 结尾，否则 tarball 路径会被错误拼接。
- 已发布的扩展会显示在「插件 / 技能市场」中，可一键安装；更新后以新版本号重新发布即可。

## 本地复现 / 重新生成

```bash
# 1) 可选：用辅助脚本重新生成 _pkgs/ 源（默认源路径见脚本顶部）
node scripts/generate-packages.mjs --src /path/to/openwork/src/process/resources/skills

# 2) 生成 index.json + extensions/*.tgz
node scripts/build-hub-catalog.mjs

# 3) 提交（index.json 与 extensions/*.tgz 需要提交，以便 jsDelivr 提供）
git add -A && git commit -m "rebuild hub catalog" && git push
```

> 注意：`.tgz` 实为 **ZIP 归档**（与 OpenWork 安装器的 yauzl 读取方式一致），
> 不要改成真正的 gzip/tar，否则安装器无法解压。

## 新增一个技能

1. 在 `_pkgs/<skill-name>/` 放入 `openwork-extension.json` + `SKILL.md` + 相关文件；
2. `openwork-extension.json` 的 `contributes.skills` 形如：
   ```json
   {
     "name": "<skill-name>",
     "displayName": "Human Friendly Name",
     "version": "1.0.0",
     "description": "What this skill does",
     "author": "OpenWork",
     "apiVersion": "^1.0.0",
     "engines": { "openwork": "^1.0.0" },
     "contributes": {
       "skills": [
         { "name": "<skill-name>", "description": "...", "file": "SKILL.md" }
       ]
     }
   }
   ```
3. 运行 `node scripts/build-hub-catalog.mjs` 并重新提交、推送。

## 说明

- 清单字段遵循 OpenWork `ExtensionManifestSchema`（`name` 必须为 kebab-case，
  且不能以 `openwork-`/`internal-`/`builtin-`/`system-` 开头）。
- `contributes.skills[].file` 为相对扩展根目录的路径，指向 `SKILL.md`。
- 完整性校验：安装器会对下载的 `.tgz` 计算 sha512，与 `index.json` 中的
  `dist.integrity`（sha512-SRI）比对，不一致则拒绝安装。

## 协议

本仓库以 Apache-2.0 许可证发布。各扩展的 `openwork-extension.json` 中 `author` 字段统一为 `OpenWork`，`license` 为 `Apache-2.0`，由 OpenWork 团队编写与维护。
