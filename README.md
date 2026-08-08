# OpenWork SkillHub

OpenWork 的远程技能市场（Remote Skill Marketplace）。本仓库把一批来自 WorkBuddy 的能力型
Skill 打包成 OpenWork 扩展（Extension），通过 GitHub + jsDelivr CDN 以
`index.json` + `extensions/*.tgz` 的形式对外发布，OpenWork 客户端配置
`OPENWORK_HUB_URL` 后即可在「插件 / 技能市场」中浏览、安装、更新这些技能。

> 本仓库对应方案 E：把 "SkillHub 市场那批" 技能接进 OpenWork 的远程扩展市场，
> 零客户端代码改动（仅依赖已有的 Extension Hub 机制）。

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
    ├── generate-packages.mjs # 从 OpenWork 仓库的 bundled skills 生成 _pkgs/
    └── build-hub-catalog.mjs # 由 _pkgs/ 生成 index.json + extensions/*.tgz
```

## 消费方式（在 OpenWork 侧）

```bash
# 启动 OpenWork 前设置，注意末尾的斜杠 "/"
export OPENWORK_HUB_URL="https://cdn.jsdelivr.net/gh/Myking1983/openwork-skillhub@main/"

# 然后正常启动（开发模式示例）
env -u ELECTRON_RUN_AS_NODE -u CODEBUDDY_SAFE_DELETE_BULK_STATE_DIR -u CODEBUDDY_TOOL_CALL_ID \
  ELECTRON_DISABLE_SANDBOX=1 OPENWORK_HUB_URL="$OPENWORK_HUB_URL" bun run start
```

- `OPENWORK_HUB_URL` 支持逗号分隔的多个基址（按顺序回退）。
- 基址**必须**以 `/` 结尾，否则 tarball 路径会被错误拼接。
- 已发布的扩展会显示在「插件 / 技能市场」中，可一键安装；更新后以新版本号重新发布即可。

## 本地复现 / 重新生成

```bash
# 1) 从 OpenWork 仓库的 bundled skills 重新生成 _pkgs/（可选，默认源路径见脚本顶部）
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
     "author": "WorkBuddy",
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

Apache-2.0（与 OpenWork 主仓库一致）。技能内容归各自原作者所有。
