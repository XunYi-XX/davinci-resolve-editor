# OpenFilm and Resolve Integration

Use this reference only for an explicit OpenFilm workflow or a deliverable
that requires both OpenFilm and Resolve. General Resolve timeline requests use
[operations.md](operations.md). An established user shorthand `of` / `OF` may
refer to OpenFilm; ordinary prose containing those letters is not a trigger.

## One Task, Separate Maintained Skills

OpenFilm is an optional, separately installed peer skill. Do not ship a stale
nested copy or represent this Resolve package as containing the OpenFilm runtime.
Discover the installed `openfilm` skill from the available-skills catalog and
read its `SKILL.md`; a common sibling location is `../openfilm/SKILL.md` relative
to this skill root. Use its actual installed instructions, including its current
manual/setup workflow, rather than duplicating them here.

If the OpenFilm skill is unavailable, explain that dependency for the OpenFilm
part and complete any independent Resolve inspection already authorized. Do not
silently install packages or substitute another tool for a specified workflow.
Resolve-only use does not require OpenFilm.

## Combined Workflow

1. Establish the intended artifact and handoff: for example, an OpenFilm intro
   or music arrangement that will be brought into an existing Resolve project.
2. Inspect the Resolve destination as needed to establish format and track
   requirements without mutating it. Use the destination timeline's actual
   frame rate and resolution rather than assuming project defaults.
3. Create and verify the OpenFilm artifact under that skill's instructions.
   Produce the appropriate media export before importing it into Resolve.
4. Use the Resolve CLI to import or assemble it only when that handoff is within
   the user's request. Duplicate a destination timeline when replacement could
   affect existing work.
5. Read back destination items, positions, source ranges, and tracks. Verify
   audible/visible output through the supported artifact or review workflow;
   a successful import alone is not proof of a correct final composition.

Carry the user's sound preferences across the handoff. When requested, keep
instruments on separate OpenFilm audio tracks and retain separation in exported
stems or delivered assets where supported. Preserve gradual tempo transitions,
a light pulse during reduced layers, and acoustic-only instrumentation when
those are explicit user requirements; do not impose them on unrelated films.

A request to analyze an existing Resolve film does not authorize OpenFilm
generation, Resolve export, project saving, or changes to its content.
