# Extract a Style from an Existing Timeline

For editorial interpretation, select a relevant reference from
[editing-styles.md](editing-styles.md). Use [operations.md](operations.md) for
connection and API constraints. Keep observations, inferences, and recommendations
distinct, and state what was visually reviewed or actually heard.

When asked to learn from an existing Resolve timeline, default to read-only.
Do not save the project, add markers, duplicate timelines, alter clips, or
export unless the user separately requests those operations.

1. Record the project and timeline names/IDs privately, plus the timeline frame
   rate, duration, current render, and whether the project has unsaved changes.
   If dirty-state or another field is unavailable through the API, record it as
   unknown; do not save or export merely to obtain it.
2. Count items by track and separate real media clips from transition objects
   and generated graphics. Record whether each track and clip is enabled; a
   long muted section may be a discarded or reference version. Query enabled
   state with each target timeline made current, because Resolve may report
   misleading `False` values for a non-current timeline; restore the original
   current timeline and playhead afterward without saving.
   Account for higher-track occlusion before counting visible shots. Merge a
   continuous same-source split when it is not a real picture change; retain
   both raw item counts and the visible-shot definition. Baked intros can
   contain internal cuts absent from timeline item counts.
3. Calculate shot-length minimum, maximum, mean, median, useful percentiles,
   and counts by duration band. Also calculate cut density by narrative chapter
   rather than relying on one whole-film average.
4. Resolve each source item's actual media frame rate before calculating a
   retiming ratio. Compare source-range duration with timeline duration to
   distinguish normal, slow, fast, and reversed playback.
5. Group source ranges by media ID. Record unique-source count and repeated,
   non-contiguous ranges; these often reveal the editor's long-source mining
   strategy.
6. Sample at least one midpoint frame from every real timeline shot. For
   representative shots and all notable long sources, sample source in, middle,
   and out frames. Verify whether the chosen range starts on an action, reaction,
   gesture, or readable composition.
7. Use visual and sound changes to define chapters, then compute shot count,
   average/median length, and cuts per minute for each chapter. This exposes
   rhythm contrast that whole-timeline statistics hide.
8. Record transition types, exact timeline positions, durations, and what
   narrative change each supports. Separate hard cuts from transition objects.
9. Record overlay and title holds, distinguishing timeline graphics from
   source-baked text. Note unused tracks.
10. Inspect audio layering by track: music beds, location sound, speech,
    overlaps, fades, local gain changes, and where live sound becomes primary.
    Check whether a musical phrase is reused at the opening and coda.
    Convert audio source frames using the media's actual imported frame rate;
    compare with file duration to avoid false retiming. Separate listening
    findings from waveform energy or automatic pulse estimates. Overlap does
    not prove a crossfade, and an energy dip does not prove a tempo or instrument
    change. Do not identify music timbre from filenames.
11. Check sequence continuity, source reuse, marker use, and whether the final
    delivered render matches the inspected timeline duration.
    Matching duration and representative order support using an existing render
    as a reference, not a claim that all current grades/effects match it. If
    live thumbnails fail, disclose the existing-render/source-frame fallback.
12. Re-read project/timeline identity and item counts after frame extraction to
    confirm the analysis remained non-destructive.
13. Generalize only patterns supported by multiple shots or an explicit
    structural function. Label project-specific measurements as evidence, not
    universal rules.
14. If the project has multiple similar timelines, compare enabled state, true
    picture end, shared media IDs, source-range changes, speed ratios,
    transitions, audio beds, and ending cards before deciding which is active.
15. Remove project names, timeline IDs, file paths, faces, and other identifying
    details before publishing the learned style publicly.

Keep case-specific measurements and private frame sheets in the user's local
knowledge location. When the user requests a reusable strategy update, store
de-identified patterns in the relevant style reference and link it from the
index. Sync only the authorized strategy changes to the intended Git repository;
do not include unrelated edits or local source evidence by default.

When frame extraction is needed, write temporary images outside the project and
the media directories. Do not save the Resolve project merely to produce
analysis frames.
