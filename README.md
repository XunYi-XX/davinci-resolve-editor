# DaVinci Resolve Editor / 达芬奇剪辑助手

通过 Blackmagic 官方 Scripting API 连接本机达芬奇，让 Codex 检查项目、组装时间线并执行经过验证的剪辑操作。

Connect Codex to a local DaVinci Resolve session through Blackmagic's official
Scripting API for project inspection, timeline assembly, and verified edits.

> 这个 Skill 不依赖 MCP 服务。  
> This Skill does not require an MCP server.

## 中文说明

### 功能

- 检测并连接正在运行的 DaVinci Resolve Studio。
- 读取项目、时间线、轨道、片段、源入点/出点、素材库和标记。
- 创建、切换、复制和删除明确指定的时间线。
- 导入素材，或将已有素材按源范围追加到时间线。
- 插入生成器、标记和标题相关基础对象。
- 设置片段属性，例如透明度、裁切、位置、缩放和旋转。
- 删除明确指定的时间线片段。
- 导出 OTIO、FCPXML 1.10 或 DRT。
- 运行会自动清理测试时间线的本地自测。
- 所有命令输出 JSON，便于 Codex 核验实际结果。

### 环境要求

- DaVinci Resolve 已打开，并已加载项目。
- Python 3.8 或更高版本；CLI 不使用第三方 Python 依赖。
- 允许本机外部脚本访问。通常不需要开启 LAN Scripting。
- 已在 DaVinci Resolve Studio 21.0.4.5 上完成本地实测。

### 安装

将整个 `davinci-resolve-editor` 文件夹放入 Codex 用户技能目录：

```text
$CODEX_HOME/skills/davinci-resolve-editor
```

如果未设置 `CODEX_HOME`，默认位置通常是：

```text
~/.codex/skills/davinci-resolve-editor
```

重新加载 Codex 后，可显式调用：

```text
使用 $davinci-resolve-editor 检查当前项目，并告诉我当前时间线的内容
```

### 直接使用 CLI

```text
python <skill-directory>/scripts/resolve_cli.py status
```

常用示例：

```text
python <skill-directory>/scripts/resolve_cli.py list-timelines
python <skill-directory>/scripts/resolve_cli.py inspect-timeline --timeline "Timeline 11"
python <skill-directory>/scripts/resolve_cli.py duplicate-timeline --timeline "Timeline 11" --name "Timeline 11 Edit"
python <skill-directory>/scripts/resolve_cli.py append-media-item --media-id MEDIA_ID --timeline "Timeline 11 Edit" --start-frame 100 --end-frame 220
python <skill-directory>/scripts/resolve_cli.py add-marker --timeline "Timeline 11 Edit" --frame 120 --color Green --name "Review"
python <skill-directory>/scripts/resolve_cli.py self-test
```

每个子命令都支持 `--help`。

### 命令概览

| 命令 | 用途 |
| --- | --- |
| `status` | 显示 Resolve、当前项目和页面状态 |
| `list-projects` | 列出当前数据库文件夹中的项目 |
| `open-project --name NAME` | 按完整名称打开项目 |
| `list-timelines` | 列出项目时间线 |
| `inspect-timeline` | 显示轨道、片段、源范围和标记 |
| `list-media` | 递归列出素材库 |
| `set-current-timeline` | 将指定时间线设为当前时间线 |
| `duplicate-timeline` | 复制时间线，适合无损试验 |
| `delete-timeline` | 删除一条明确命名的时间线 |
| `create-timeline` | 创建空时间线或插入生成器 |
| `import-media` | 将文件导入素材库 |
| `append-media` | 导入并追加文件到时间线 |
| `append-media-item` | 按素材 ID 追加项目内已有素材 |
| `insert-generator` | 插入标准生成器 |
| `add-marker` | 添加并核验时间线标记 |
| `set-clip-property` | 设置指定片段属性 |
| `delete-clips` | 删除明确列出的片段 ID |
| `export-timeline` | 导出 OTIO、FCPXML 或 DRT |
| `self-test` | 创建临时时间线、写入并自动清理 |

### 安全规则

- Blackmagic 的 Developer 和 Technical Documentation 目录始终只读。
- 修改现有时间线前先读取其唯一 ID、片段数量和标记。
- 可能影响现有内容的操作优先在复制时间线上进行。
- `delete-timeline` 和 `delete-clips` 必须提供 `--confirm`。
- 删除片段时默认只处理传入的 ID；链接的视频和音频通常需要分别指定。
- 不要仅凭 API 返回值报告成功，必须重新读取并核验。
- 自动重试可能导致 Resolve 无响应的操作是不允许的。

### 已知兼容性

在本地测试的 Resolve Studio 21.0.4.5 中，对通过 API 新建的 `Solid Color`
生成器片段直接调用属性写入曾使 Resolve 无响应；对真实视频片段执行同类属性
写入正常。生成器属性操作不在自动自测中。修改属性前请先保存项目并操作复制
时间线。

## English Guide

### What it does

- Detects and connects to a running DaVinci Resolve Studio instance.
- Reads projects, timelines, tracks, clips, source ranges, media pools, and markers.
- Creates, selects, duplicates, and deletes explicitly named timelines.
- Imports media or appends an existing media-pool item using a source range.
- Inserts generators and basic timeline objects.
- Sets clip properties such as opacity, crop, pan, zoom, and rotation.
- Deletes explicit timeline item IDs.
- Exports OTIO, FCPXML 1.10, or DRT.
- Provides a reversible local self-test.
- Returns machine-readable JSON from every command for reliable verification.

### Requirements

- DaVinci Resolve is running with a project loaded.
- Python 3.8 or newer; the CLI has no third-party Python dependencies.
- Local external scripting is enabled. LAN scripting is normally unnecessary.
- Locally tested with DaVinci Resolve Studio 21.0.4.5.

### Installation

Place the complete `davinci-resolve-editor` folder under the Codex user skill
directory:

```text
$CODEX_HOME/skills/davinci-resolve-editor
```

When `CODEX_HOME` is unset, the usual location is:

```text
~/.codex/skills/davinci-resolve-editor
```

Reload Codex, then invoke:

```text
Use $davinci-resolve-editor to inspect the current project and describe the current timeline.
```

### CLI usage

```text
python <skill-directory>/scripts/resolve_cli.py status
```

Common examples:

```text
python <skill-directory>/scripts/resolve_cli.py list-timelines
python <skill-directory>/scripts/resolve_cli.py inspect-timeline --timeline "Timeline 11"
python <skill-directory>/scripts/resolve_cli.py duplicate-timeline --timeline "Timeline 11" --name "Timeline 11 Edit"
python <skill-directory>/scripts/resolve_cli.py append-media-item --media-id MEDIA_ID --timeline "Timeline 11 Edit" --start-frame 100 --end-frame 220
python <skill-directory>/scripts/resolve_cli.py add-marker --timeline "Timeline 11 Edit" --frame 120 --color Green --name "Review"
python <skill-directory>/scripts/resolve_cli.py self-test
```

Every subcommand supports `--help`.

### Command overview

| Command | Purpose |
| --- | --- |
| `status` | Show Resolve, project, and page status |
| `list-projects` | List projects in the current database folder |
| `open-project --name NAME` | Open a project by exact name |
| `list-timelines` | List project timelines |
| `inspect-timeline` | Show tracks, clips, source ranges, and markers |
| `list-media` | Recursively list the media pool |
| `set-current-timeline` | Select a named timeline |
| `duplicate-timeline` | Duplicate a timeline for non-destructive work |
| `delete-timeline` | Delete one explicitly named timeline |
| `create-timeline` | Create an empty timeline or insert a generator |
| `import-media` | Import files into the media pool |
| `append-media` | Import files and append them to a timeline |
| `append-media-item` | Append an existing project media item by ID |
| `insert-generator` | Insert a standard generator |
| `add-marker` | Add and verify a timeline marker |
| `set-clip-property` | Set a property on one timeline item |
| `delete-clips` | Delete explicitly listed timeline item IDs |
| `export-timeline` | Export OTIO, FCPXML, or DRT |
| `self-test` | Create, edit, verify, and clean up a temporary timeline |

### Safety rules

- Always treat Blackmagic Developer and Technical Documentation as read-only.
- Inspect the target timeline's IDs, item count, and markers before mutation.
- Prefer a duplicated timeline when the original must remain untouched.
- `delete-timeline` and `delete-clips` require `--confirm`.
- Deletion handles only explicitly supplied IDs; pass the linked video and audio
  IDs separately when both must be removed.
- Verify every mutation by reading the affected state back.
- Never automatically retry an operation that made Resolve unresponsive.

### Known compatibility note

On the locally tested Resolve Studio 21.0.4.5 build, setting a transform
property on an API-created `Solid Color` generator clip made Resolve
unresponsive. The same property operation succeeded on a real video clip.
Generator property mutation is excluded from the automatic self-test. Save the
project and work on a duplicate before changing clip properties.

## Files / 文件结构

```text
davinci-resolve-editor/
|-- SKILL.md
|-- README.md
|-- agents/
|   `-- openai.yaml
|-- references/
|   `-- operations.md
`-- scripts/
    `-- resolve_cli.py
```

- `SKILL.md`: concise execution instructions for Codex.  
  Codex 使用的精简执行规则。
- `README.md`: bilingual human-facing documentation.  
  面向用户和 GitHub 访客的双语说明。
- `references/operations.md`: detailed English operations reference.  
  英文详细操作参考。
- `scripts/resolve_cli.py`: dependency-free Resolve CLI.  
  无第三方依赖的达芬奇命令行工具。
- `agents/openai.yaml`: UI metadata and invocation policy.  
  界面元数据与自动调用策略。
