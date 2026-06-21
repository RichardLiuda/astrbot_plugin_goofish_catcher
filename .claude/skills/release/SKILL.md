---
name: release
description: 为 astrbot_plugin_goofish_catcher 发布新版本。当用户说"发版"、"发布"、"release"、"推版本"、"打 tag"时触发。完整流程：确定新版本号 → 更新 CHANGELOG.md → 更新 metadata.yaml → 提交 → 推送 → 打 tag → 创建 GitHub Release。
---

# Release 发版流程

## 版本号规则（Semantic Versioning）

- **patch**（默认）：bug 修复、文档，不影响接口 → `v2.2.3` → `v2.2.4`
- **minor**：新功能、向下兼容 → `v2.2.3` → `v2.3.0`
- **major**：破坏性变更 → `v2.2.3` → `v3.0.0`

用户未指定时根据本次改动判断，有疑问时直接选 patch。

## 执行步骤

### 1. 确认当前状态

```bash
git log --oneline -5
cat metadata.yaml   # 读取当前版本
git diff HEAD       # 确认未提交改动
```

若有未提交改动，先询问用户是否纳入本次 release，再决定是否先提交。

### 2. 确定新版本号

从 `metadata.yaml` 读取 `version: vX.Y.Z`，按上述规则递增。

### 3. 更新 CHANGELOG.md

在 `## [上一版本]` 条目**前**插入：

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added / Changed / Fixed（按实际选）

- 改动描述，简明扼要，面向用户
```

日期用当天日期（`date +%Y-%m-%d`）。改动内容从对话上下文或 `git log` 提炼，不要照抄 commit message。

**Worker 兼容性行**：CHANGELOG 顶部有一行：

```markdown
当前插件版本（vX.Y.Z）需要 Worker **≥ vA.B.C**。
```

每次发版都要把括号里的插件版本号更新为新版本号。**只有**本次改动涉及 Worker 接口变更（breaking change）时，才同时更新 `≥ vA.B.C` 部分。

### 4. 更新 metadata.yaml

将 `version: vX.Y.Z` 改为新版本号。

### 5. 提交

```bash
git add CHANGELOG.md metadata.yaml
git commit -m "release: bump version to vX.Y.Z"
git push origin master
```

### 6. 打 Tag 并推送

```bash
git tag vX.Y.Z
git push origin vX.Y.Z
```

### 7. 创建 GitHub Release

```bash
gh release create vX.Y.Z \
  --title "vX.Y.Z" \
  --notes "$(从 CHANGELOG 摘取本版本的条目内容)"
```

`--notes` 内容直接取 CHANGELOG 中本次版本的 `### Added/Changed/Fixed` 部分，不要加版本号标题行。

## 注意事项

- 如果 `gh` 未登录（`gh auth status` 失败），告知用户执行 `gh auth login` 后再继续
- 若有未推送的功能性提交不在 CHANGELOG 里，先补充再发版
- 不要改动 `requirements.txt`、`_conf_schema.json` 等非版本文件
