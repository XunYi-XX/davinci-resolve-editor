# DaVinci Resolve Editor / 达芬奇剪辑助手

通过 Blackmagic 官方 Scripting API 连接本机达芬奇，把项目操作、素材选取、
剪辑策略和成片风格学习组织在同一个 Skill 入口中。

Connect Codex to a local DaVinci Resolve session through the official Scripting
API, with one entrypoint for project operations, footage selection, editorial
strategy, and read-only style learning.

本包的 Resolve CLI 不依赖 MCP 服务或第三方 Python 库。OpenFilm 是可选的独立
技能，按需联动，不包含在本仓库中。

The Resolve CLI requires no MCP server or third-party Python libraries. OpenFilm
is an optional, separately installed skill, not a bundled runtime.

## 中文说明

### 统一任务入口

| 任务 | 工作方式 |
|---|---|
| 检查项目、时间线、轨道、源范围和素材库 | 官方 API 只读检查 |
| 组装时间线、导入素材、标记、片段属性、删除和导出 | 明确目标后执行，再读回核验 |
| 学习当前成片的选材、节奏、转场与配乐使用 | 时间线结构 + 可见画面抽帧 + 声音证据，默认只读 |
| 抒情情绪片、事件回顾、文化活动快剪、篮球活动片 | 读取对应专题策略，按素材和目标调整 |
| OpenFilm 制作与 Resolve 导入衔接 | 调用已安装的 OpenFilm 技能，先验证产物，再按授权导入 |

### 安装与环境

将整个 `davinci-resolve-editor` 文件夹放入：

```text
$CODEX_HOME/skills/davinci-resolve-editor
```

未设置 `CODEX_HOME` 时，通常为 `~/.codex/skills/davinci-resolve-editor`。
重新加载 Codex 后即可使用。Resolve 操作需要本机已打开达芬奇并加载项目，
以及 Python 3.8+、本机外部脚本访问权限；无需开启 LAN Scripting。

CLI 的连接与编辑曾在 Resolve Studio 21.0.4.5 上测试；只读项目和时间线检查
也在 Studio 21.1.1.10 上使用过。后者不代表所有写操作都已在该版本验证。

OpenFilm 联动需要独立安装 `openfilm` 技能。纯 Resolve 工作不依赖它。配置与
诊断详见 [操作参考](references/operations.md)。

### 使用示例

```text
使用 $davinci-resolve-editor 检查当前时间线，告诉我轨道和素材结构。

学习我现在打开的成片：分析素材选择、动作入出点、剪辑节奏和音乐交接，不修改项目。

按篮球活动片的风格，从已有素材组装一条新时间线，保留原片。

把我已经确认的 OpenFilm 片头导入指定的 Resolve 时间线，并核验位置和时长。
```

直接使用 CLI：

```text
python <skill-directory>/scripts/resolve_cli.py status
python <skill-directory>/scripts/resolve_cli.py list-timelines
python <skill-directory>/scripts/resolve_cli.py inspect-timeline --timeline "Timeline 11"
python <skill-directory>/scripts/resolve_cli.py list-media --limit 20
```

所有命令输出 JSON，并支持 `--help`。完整命令表和源入出点规则见
[操作参考](references/operations.md)。

### 策略与学习记录

- [策略索引](references/editing-styles.md)：按成片目标选择专题。
- [抒情情绪片](references/lyrical-emotional.md)：空间、人物、情绪展开与释放。
- [事件回顾](references/event-recap.md)：纪实蒙太奇、人物互动与现场声收束。
- [文化活动快剪](references/cultural-quick-cut.md)：细节、参与和表演的短片节奏。
- [篮球活动片](references/basketball-event-recap.md)：动作选段、疏密变化、应援与集体收尾。
- [只读风格审计](references/style-audit.md)：可见镜头计数、抽帧、变速、声音与证据边界。
- [OpenFilm 联动](references/openfilm-integration.md)：独立技能发现、产物验证与 Resolve 交接。

样片中的时长和节拍是参考证据，不是固定配额。区分实际听辨、波形测量与推断；
不凭文件名判断乐器，不凭素材帧率判断慢动作。具体项目信息和截图留在用户本地，
可复用策略去标识后再按用户要求同步 Git。

### 操作边界与验证

- 学习成片时不保存、标记、复制、裁切或导出工程；检查结束恢复为检查而改变的页面和播放头。
- 修改前读取目标身份与状态；可能替换现有内容时优先使用复制时间线。
- 删除必须明确指定时间线名称或片段 ID，并使用 `--confirm`。
- API 返回成功不等于结果正确，必须读回核验；失败结果未确定前不盲目重试。
- Blackmagic Developer 和 Technical Documentation 目录始终只读。

`self-test` 会在当前项目创建并清理临时时间线，属于会写入工程的测试，不用于只读
风格学习。在 Studio 21.0.4.5 上，对 API 新建 `Solid Color` 生成器写属性曾使
Resolve 无响应；生成器属性修改不包含在自动自测中。按操作参考在已保存的副本上
处理这类已知风险，不自动重试造成无响应的操作。

## English Guide

### Install and connect

Place the complete folder under `$CODEX_HOME/skills/davinci-resolve-editor`, or
`~/.codex/skills/davinci-resolve-editor` when that variable is unset. Reload Codex.
Resolve operations require a running Resolve project, Python 3.8+, and local
external scripting access. LAN scripting is unnecessary.

Connection and editing were tested on Studio 21.0.4.5; read-only inspection was
also used on Studio 21.1.1.10. This does not certify every mutation on the latter.
OpenFilm is optional and separately installed. Read [operations](references/operations.md)
for diagnostics, environment overrides, the command map, and compatibility notes.

### Choose a workflow

- Inspect or edit projects, timelines, media, markers, and properties through
  the CLI. Identify the target first and verify mutations by readback.
- For learning from a finished film, follow the
  [read-only audit](references/style-audit.md): inspect structure, account for
  visible shots, sample frames, and distinguish listening from signal estimates.
- For editorial choices, use the [strategy index](references/editing-styles.md)
  to select lyrical, documentary-event, cultural quick-cut, or basketball guidance.
- For a combined task, follow [OpenFilm integration](references/openfilm-integration.md),
  read the installed peer skill, verify its artifact, then perform only the
  authorized Resolve handoff.

```text
Use $davinci-resolve-editor to inspect my current Resolve timeline.
Learn shot selection, rhythm, and music handoffs from this film without editing it.
```

```text
python <skill-directory>/scripts/resolve_cli.py status
python <skill-directory>/scripts/resolve_cli.py inspect-timeline
```

Every command supports `--help` and returns JSON. Use timeline or source frame
rates correctly; do not assume they equal the project default. Reference timings
are evidence, not quotas. Keep identifying source evidence local and publish
only authorized, de-identified reusable strategy.

### Safety and verification

Read-only learning must not save, mark, duplicate, trim, or export the project.
Restore navigation changed for inspection. Before a requested mutation, inspect
IDs and state; use a duplicate when replacement could affect existing work.
Deletion requires explicit targets and `--confirm`. Establish the prior result
before retrying an operation. Blackmagic documentation directories are read-only.

`self-test` creates and removes a temporary timeline and is not a read-only audit.
On Studio 21.0.4.5, setting a transform property on an API-created `Solid Color`
generator caused a hang; generator property mutation is excluded from that test.
Follow the operations reference and do not automatically retry a hung operation.

## Package layout / 文件结构

```text
davinci-resolve-editor/
|-- SKILL.md                         # Unified agent entrypoint
|-- README.md                        # Human-facing bilingual guide
|-- agents/
|   `-- openai.yaml                  # Existing UI and implicit invocation policy
|-- references/
|   |-- operations.md                # API/CLI semantics and compatibility
|   |-- editing-styles.md            # Editorial strategy index
|   |-- lyrical-emotional.md         # Lyrical emotional film
|   |-- event-recap.md               # Documentary event recap
|   |-- cultural-quick-cut.md        # Short cultural/social recap
|   |-- basketball-event-recap.md    # Sports and basketball recap
|   |-- style-audit.md               # Read-only style extraction
|   `-- openfilm-integration.md      # Optional peer-skill handoff
`-- scripts/
    `-- resolve_cli.py               # Dependency-free official-API CLI
```

The installed OpenFilm peer skill owns its current instructions and runtime
workflow. This package links the handoff without bundling a second copy.
