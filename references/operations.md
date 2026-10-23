# Operations Reference

## Contents

- CLI command map
- Connection and diagnostics
- Timeline inspection
- Media and sequence assembly
- Markers and clip properties
- Export and local self-test
- Safety and verification

## CLI command map

Run `python <skill-directory>/scripts/resolve_cli.py <command> [options]`.
Every command supports `--help`; use it for the exact arguments and defaults.

| Command | Purpose |
|---|---|
| `status` | Read connection, product, project, page, and current timeline |
| `list-projects` | List projects in the current database folder |
| `open-project --name NAME` | Open the explicitly selected project |
| `list-timelines` | List current project timelines and identify the active one |
| `inspect-timeline [--timeline NAME]` | Read tracks, items, source ranges, and markers |
| `list-media [--limit N]` | Recursively inspect media-pool items |
| `set-current-timeline --timeline NAME` | Navigate to a named timeline |
| `duplicate-timeline --name NEW_NAME` | Duplicate the selected/current timeline |
| `delete-timeline --name NAME --confirm` | Delete one explicitly selected timeline |
| `create-timeline --name NAME` | Create an empty timeline; optionally add a generator |
| `import-media PATH [PATH ...]` | Import files without appending them |
| `append-media PATH [PATH ...]` | Import and append files, optionally by source range |
| `append-media-item --media-id ID` | Append an existing pool item by source range |
| `insert-generator --generator NAME` | Insert a standard generator |
| `add-marker --frame N` | Add a timeline-relative marker and verify it |
| `set-clip-property --item-id ID --property NAME --value VALUE` | Set one item's property |
| `delete-clips --item-id ID --confirm` | Delete only specified item IDs |
| `export-timeline --timeline NAME --output PATH --format FORMAT` | Export OTIO, FCPXML, or DRT |
| `self-test` | Create and clean up a temporary test timeline; requires authorized mutation |

## Connection and diagnostics

Run `status` first. A usable response contains a product name, version, project name, page, timeline count, and current timeline. The helper searches:

- `RESOLVE_SCRIPT_API` and `RESOLVE_SCRIPT_LIB` when set;
- standard Blackmagic Developer Scripting locations;
- the installation directory of a running Resolve process;
- standard installation paths for Windows, macOS, and Linux.

The API must be allowed to run scripts. External scripting is local by default in Resolve preferences. Enabling LAN scripting is unnecessary and should not be requested for the local helper.

`RESOLVE_SCRIPT_API` points to the Scripting API directory containing
`Modules/DaVinciResolveScript.py`. `RESOLVE_SCRIPT_LIB` points to
`fusionscript.dll` on Windows, `fusionscript.so` on Linux, or the matching
library inside the macOS application bundle. Set these only when discovery
fails; follow the helper's actual diagnostic rather than guessing paths.

## Timeline inspection

`list-timelines` provides the frame rate, start and end frames, and current marker for every timeline.

`open-project` loads an existing project by its exact name. Inspect `list-projects`
first and use this only when the user selected that project or the active project
must be restored after a failed test.

`inspect-timeline` returns:

- timeline name, unique ID, frame range, start timecode, and frame rate;
- video, audio, and subtitle tracks;
- every timeline item with its unique ID, name, timeline position, duration, source range, and source file path when available;
- timeline markers.

Use item unique IDs to target clip-property and deletion operations. Names are not guaranteed to be unique.

For read-only style or version audits that need track/clip enabled state, make
each target timeline current before querying `GetIsTrackEnabled` and
`GetClipEnabled`. In locally observed Resolve behavior, querying a non-current
timeline could return misleading `False` values. Restore the original current
timeline and playhead after inspection; do not save unless the user requests it.

The CLI's compact item listing does not supply every style-audit field. When
needed, use the same official API connection for track/clip enable state, source
media frame rates, audio properties, and supported thumbnails. Missing fields
remain unknown; do not silently substitute the project or timeline frame rate.
See [style-audit.md](style-audit.md) for the analysis workflow.

## Media and sequence assembly

`list-media` recursively reads the current project's media pool. It reports file paths, media IDs, clip names, types, frame rates, source frame counts, and resolutions.

`import-media` imports paths into the current media pool folder. It does not append them to a timeline.

`append-media` imports paths and appends the resulting clips to the selected or current timeline. With `--start-frame` or `--end-frame`, it creates a subclip range. `--end-frame` is the last source frame. If only a start frame is supplied, the helper derives the end from the clip's `Frames` property.

`append-media-item` uses an existing project media-pool item by `media_id` and
therefore does not duplicate the import. This is the preferred path for
assembling a sequence from material already in the project.

`create-timeline` creates an empty timeline. `--generator` inserts a standard Resolve generator into the new timeline.

`duplicate-timeline` is the preferred starting point for exploratory edits because it preserves the original timeline.

`delete-timeline` accepts one exact name and requires `--confirm`. Use it only for
a timeline the user explicitly selected or a uniquely named disposable test
timeline created by this skill.

## Markers and clip properties

`add-marker` uses a timeline-relative integer frame. View marker state with `inspect-timeline` after adding it.

`set-clip-property` targets a unique timeline-item ID. Example properties are `Opacity`, `CropLeft`, `CropTop`, `Pan`, `Tilt`, `ZoomX`, and `ZoomY`. Use Resolve's documented ranges; values outside a supported range can be clipped by Resolve.

`delete-clips` accepts only explicit item IDs and requires `--confirm`. It never supports deleting all clips. Use the timeline's ripple boolean only when the user requested ripple deletion.

## Export and local self-test

`export-timeline` currently supports:

- `otio`
- `fcpxml` using FCPXML 1.10
- `drt`

The command creates the destination's parent directory and verifies both Resolve's
return value and the exported artifact. Some versions return an FCPXML package
directory containing `Info.fcpxml` instead of a single plain file, so verification
accepts either a file or directory and reports the artifact count and total bytes.

`self-test` is a non-destructive local smoke test. It:

1. Records the current timeline.
2. Creates a uniquely named temporary timeline in the current project.
3. Tries to insert a built-in color generator.
4. Adds a marker and reads it back.
5. Deletes only timelines it created.
6. Restores the original timeline when it still exists.

The test never switches projects or deletes user-created timelines. A result with `success: false` must be investigated before editing real timelines.

On the locally tested Resolve Studio 21.0.4 build, setting a transform property
on an API-created generator clip made Resolve unresponsive, while the same
operation succeeded on a real video clip. Keep property mutation, duplication,
deletion, and export as separate explicit commands rather than automatic
self-test steps. Work on a saved duplicate, use an external timeout, and inspect
Resolve afterward. Do not automatically retry an operation that made Resolve
unresponsive.

## Safety and verification

Before mutating an existing timeline:

1. Capture its unique ID and item count.
2. Duplicate it when the user's original must remain untouched.
3. Apply the operation.
4. Re-read the affected state and compare expected item count, names, ranges, markers, or properties.
5. Report failed API return values instead of assuming the UI completed the operation.

Resolve APIs are often asynchronous or dependent on the active page. If an operation fails, check `status`, confirm the project and timeline still match, and wait briefly before retrying. Never retry a destructive operation until its prior result is established.

