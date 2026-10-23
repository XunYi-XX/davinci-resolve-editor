---
name: davinci-resolve-editor
description: Inspect or edit a running DaVinci Resolve project through its Scripting API, select and assemble footage, or learn an editing style from timeline structure and sampled frames. Includes event, basketball, cultural quick-cut, and lyrical editing guidance. 连接达芬奇检查或剪辑项目、筛选组装素材，并通过时间线与抽帧学习剪辑风格。
---

# DaVinci Resolve Editor / 达芬奇剪辑助手

Use `scripts/resolve_cli.py` for the official Resolve Scripting API. Prefer API
operations to UI automation. CLI results are JSON; explain the verified outcome
in the user's language. This package provides one entrypoint and task-specific
references. Read only the references needed for the request.

## Choose the Workflow

| Request | Reference and action |
|---|---|
| Project, timeline, media, marker, property, assembly, or export operations | [operations.md](references/operations.md); use the CLI below |
| Learn a finished timeline, review shot selection, rhythm, music use, or compare versions | [style-audit.md](references/style-audit.md); default to read-only |
| Editorial judgment, selection, structure, or an edit in a named style | [editing-styles.md](references/editing-styles.md); choose its relevant style reference |
| OpenFilm, `film.html`, OpenFilm Studio, or a combined OpenFilm/Resolve task | [openfilm-integration.md](references/openfilm-integration.md); use the separately installed OpenFilm skill when available |

A request to inspect or edit a Resolve timeline stays on the Resolve workflow.
Do not route it to OpenFilm merely because it concerns video. If the user uses
`of` or `OF` as their established OpenFilm shorthand, interpret it accordingly.

## Resolve Workflow

1. Run `status`; record the current project, timeline, page, and playhead as needed.
2. Read the target using `list-timelines`, `inspect-timeline`, and, when needed,
   `list-media`. Identify the project/timeline explicitly and use stable IDs.
3. For an edit that could replace existing work, duplicate the timeline and edit
   the duplicate. Apply only the requested operations.
4. Read the affected state back. Verify ranges, IDs, counts, markers, properties,
   or output artifacts that demonstrate the requested result.
5. Report the concrete outcome and any failed step. Restore navigation changed
   only for inspection; save only when requested or necessary for authorized work.

When learning from a finished timeline, do not save, mark, duplicate, trim, or
export the project. Sample existing rendered or source frames outside project
and media directories. Record conclusions in the user's requested location;
analysis does not authorize an edit. Follow the evidence limits in the audit
reference, particularly visible-shot counts, source rates, render matching,
and music listening versus waveform estimates.

## CLI

```text
python <skill-directory>/scripts/resolve_cli.py <command> [options]
```

Start with `status`, `list-timelines`, `inspect-timeline`, and `list-media`.
Use `<command> --help` before guessing option names; the complete command map,
source-range semantics, connection setup, and known compatibility limits are
in [operations.md](references/operations.md). Human-facing setup and examples
are in [README.md](README.md).

## Execution Boundaries

- Do not switch or delete user projects as an implementation shortcut. Opening
  another project requires the user's selected target or a necessary restoration.
- Do not delete or replace existing timeline content without an explicit request.
  Destructive commands require exact item IDs or timeline names and `--confirm`.
- Treat `False` or `None` from a mutation as failure. Re-read state before retrying
  to avoid duplicate changes; do not automatically retry a hung operation.
- Distinguish timeline frames, source frames, and timeline-relative markers. Use
  the correct frame rate for each; prefer integer frames over ambiguous timecodes.
- Marker colors must be Resolve's standard colors. Property values are parsed as
  JSON, preserving numeric, boolean, array, and object types.
- Blackmagic Developer and Technical Documentation directories are read-only.
- Local technical evidence and user preferences outrank style examples. Timing
  measurements in references are calibration, not fixed quotas.
- Keep private project identifiers, source paths, screenshots, and faces in local
  analysis records. Publish reusable, de-identified strategy only when requested;
  Git synchronization follows the user's authorization and repository scope.
