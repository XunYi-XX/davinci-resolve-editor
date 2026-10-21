---
name: davinci-resolve-editor
description: Connect to a running DaVinci Resolve Studio instance to inspect or edit projects, timelines, media, markers, clip properties, and exports, or analyze timeline structure and sample frames to learn an editing style. 连接正在运行的达芬奇，检查或剪辑项目、时间线、素材、标记、片段属性及导出内容，也可分析时间线与画面帧、学习剪辑风格。
---

# DaVinci Resolve Editor / 达芬奇剪辑助手

Use the official scripting API through `scripts/resolve_cli.py`. Prefer API operations over mouse and keyboard automation. Keep all output machine-readable JSON.

For the full user-facing bilingual overview, read [README.md](README.md). The
remainder of this file is the concise execution contract for the agent.

## Integrated Related Workflows

Related workflows bundled under `skills/` are not automatically activated as
separate top-level Codex skills. When a request matches one, read its
`SKILL.md` in full and execute it in the same turn instead of only suggesting
that the user invoke another skill.

- For OpenFilm, web-native films, `film.html`, motion graphics, explainers,
  launch films, music videos, or OpenFilm Studio, read
  [skills/openfilm/SKILL.md](skills/openfilm/SKILL.md) and follow it.
- If the combined task also needs DaVinci Resolve, complete the OpenFilm
  creation or export first, then use this skill's Resolve checks, imports, and
  read-back verification afterward.
- Keep ordinary DaVinci project, timeline, media, marker, and clip-property
  requests on this skill's Resolve workflow; do not redirect them to OpenFilm.

## Workflow

1. Confirm Resolve is open and run `status`.
2. Read the target before changing it with `list-timelines`, `inspect-timeline`, and `list-media`.
3. Identify the project and timeline explicitly. If the request could replace existing work, duplicate the timeline first and edit the duplicate.
4. Perform the smallest operation that meets the request.
5. Re-read the affected timeline or marker state. Report the concrete changes and any cleanup or failed steps.

Do not switch or delete user projects as an implementation shortcut. Do not delete or replace existing timeline content unless the user explicitly asked for that edit. For destructive edits, require exact item IDs or timeline names and pass the CLI's explicit confirmation flag.

## Commands

Run commands with:

```text
python <skill-directory>/scripts/resolve_cli.py <command> [options]
```

Core commands:

```text
status
list-projects
open-project --name NAME
list-timelines
inspect-timeline [--timeline NAME]
list-media [--limit N]
set-current-timeline --timeline NAME
duplicate-timeline [--timeline NAME] --name NEW_NAME
delete-timeline --name NAME --confirm
create-timeline --name NAME [--generator NAME]
import-media PATH [PATH ...]
append-media PATH [PATH ...] [--timeline NAME] [--start-frame N] [--end-frame N]
append-media-item --media-id ID [--timeline NAME] [--start-frame N] [--end-frame N]
insert-generator --generator NAME [--timeline NAME]
add-marker --frame N [--timeline NAME] [--name TEXT] [--color Blue]
export-timeline --timeline NAME --output PATH --format otio
set-clip-property --item-id ID --property Opacity --value 80
delete-clips --item-id ID [--item-id ID ...] --confirm
self-test
```

Use `--help` on a command before guessing option names. Read [references/operations.md](references/operations.md) for command semantics, API constraints, and verification details.

## Blackmagic documentation

Treat Blackmagic Developer and Technical Documentation directories as strictly
read-only. Read files there when API or product behavior is unclear, but never
edit, generate, rename, delete, or reorganize files inside those directories.

## Editing Rules

- Frames are integers and use the timeline's frame rate. Prefer frame values over timecode text for API operations.
- `append-media` imports and appends media. Use `--start-frame` and `--end-frame` for source ranges when assembling trimmed sequences.
- Marker colors are case-insensitive but must be one of the standard Resolve colors.
- Clip property values are parsed as JSON when possible, so numbers, booleans, arrays, and objects retain their types.
- Treat a `False` or `None` return from a mutation as failure. Never report success until a read-back confirms the expected state.
- Save the project only when the user requested it or when doing so is a necessary part of the requested workflow.

## Narrative and Style

For editorial recommendations, emotional montage, event recaps, frame-audited
style learning, or a style described as `抒情情绪片`, read
[references/editing-styles.md](references/editing-styles.md). Use its structure
and rhythm ranges as adaptable guidance; the footage, music, and explicit user
intent take priority.

When the user asks to learn from an existing timeline rather than revise it,
treat the workflow as read-only: do not save, mark, duplicate, trim, or export
the project. Inspect timeline and source ranges, sample rendered or source
frames outside the project, and record conclusions in the user's requested
knowledge location. Do not infer permission to update the project from a style
analysis request.

## Connection

The helper discovers the standard API directories and the running Resolve installation. If discovery fails, set:

```text
RESOLVE_SCRIPT_API
RESOLVE_SCRIPT_LIB
```

`RESOLVE_SCRIPT_LIB` should point to `fusionscript.dll` on Windows, `fusionscript.so` on Linux, or the equivalent library inside the macOS application bundle.

