# Basketball and Sports-Event Recaps

Use [style-audit.md](style-audit.md) for the shared measurement, privacy, and
read-only workflow; [operations.md](operations.md) covers Resolve commands.

Use for basketball-event footage selection, recap editing, and learning from
a finished sports timeline. Adapt to the user's purpose: an event recap may
need participation and supporters; a competitive highlight or team story may
give those elements different weight. This is guidance, not a fixed template.

## Select Ranges by Their Editorial Job

- **Identity and space:** campus or venue, event banner, court geography,
  basket, team or event graphics. Prefer a few readable views to repeated signs.
- **Action:** jump ball, drive, pursuit, contest, shot release, rebound, or
  change of possession. Look for a change in the action or relationship.
- **Participation:** casual shooting, queues, different participants, and
  interaction beyond the main match, when the film represents the whole event.
- **People and roles:** referee, coach, organizer, or player expression. Choose
  a readable gesture or role cue rather than an interchangeable portrait.
- **Supporters and collective closure:** signs, raised hands, reactions, crowd
  interaction, and a group view. These can turn physical action into shared emotion.

Select the usable action interval before choosing its final duration. Preserve
enough setup to understand the move and enough outcome for the intended claim.
A short shot may isolate one release or gesture; a key drive may need several
seconds to develop. Follow the subject's action rather than automatically
starting at the head of the camera take.

Low camera positions and close following can strengthen speed and opposition.
Tilt or brief motion blur can coexist with a strong action; they are not goals
in themselves. Check that the ball, principal player, and relevant space remain
readable at the decisive moment.

Do not infer that a shot release and basket close-up from separate files depict
the same possession without supporting evidence. Distinguish visual association
from verified event continuity.

## Shape Density Across Sections

A useful event-recap arc is:

`event identity and space → first action passage → participation/change of
pressure → person or role bridge → renewed action → supporters and collective
closure → event card`

Move or omit sections when the footage and purpose call for it. Organize by
information and energy, while keeping factual relationships clear.

One frame-audited, approximately 72-second reference used these visible-media
segment averages:

| Passage | Average segment length |
|---|---:|
| Environment and identity | 1.23 s |
| First action passage | 3.10 s |
| Participation burst | 0.94 s |
| Role bridge and renewed action | 1.74 s |
| Closing action, supporters, and group | 1.09 s |

Its median visible segment was 1.27 seconds, while one action held for 5.77
seconds. These are calibration evidence, not quotas. Preserve the contrast
between dense passages and action that needs room to resolve.

That reference contained 45 visible media segments after merging one contiguous
same-source split, including a baked intro and closing image. Such a count is
not the number of all visual cuts inside the pre-rendered intro. Occluded media
and transition objects must not inflate the visible shot count.

## Cuts, Motifs, and Speed

- Use action, motion direction, framing, or musical phrasing to join the main
  game coverage. Do not cover every action cut with a transition.
- A family of moving transitions can link short supporter-sign or crowd
  sequences and provide an opening/ending motif. Concentrate it where that
  visual relationship exists.
- A crash zoom may mark a structural move into live footage or a final group
  view. A short dissolve may soften a specific handoff or end card.
- Compress stable aerial or spatial moves when their information remains
  legible. Source-span/timeline-duration ratios describe average speed, not
  the shape of a speed ramp.
- Read each source's frame rate. A 59.94 fps source in a 29.97 fps timeline
  does not by itself prove half-speed playback.
- Check whether reuse is a new source interval or nearly the same action.
  The audited reference reused one near-identical interval; that observation
  does not establish a general preference for repetition or long-source mining.

## Music Selection and Sound Structure

Choose music with clear rhythmic support, room for important action, changes
in energy that can support sections, and an ending that can resolve with the
picture. Assess timbre through listening; do not infer genre or instruments
from a filename, waveform, or tempo estimate.

An intro soundtrack can continue after the picture enters live footage, with
the main music arriving underneath it. The audited reference overlapped the
two audio items for about 3.87 seconds and retained about two seconds of
location sound at its opening jump ball. Learn continuity and selective presence
from that structure; overlap alone does not prove a crossfade or its curve.

The reference's main music yielded a strong estimated period near 118 BPM,
with other metrical interpretations present. At that rate, two beats are about
1.02 seconds and four beats about 2.03 seconds, useful scales for its short
shots. Longer action crossed more beats. Do not turn this estimate into a fixed
tempo requirement or claim exact beat synchronization without measured beat
positions. Fitting a beat-grid phase to cuts is not independent proof of sync.

The music's measured energy dip roughly coincided with the move into
participation footage. An energy dip supports a statement about contrast; it
does not establish a tempo change, a drum dropout, or a new instrument.

For each audio item, record enabled state, placement, readable source range,
overlap, and supported gain properties. Audio source frames may use the media
pool's imported rate rather than the timeline rate. In the reference, a roughly
65-second MP3 reported 24 fps source frames in a 29.97 fps timeline; dividing
those source frames by the timeline rate would incorrectly suggest a roughly
52-second source range and false retiming.

When the user explicitly requests acoustic instrumentation, carry that choice
into music selection and arrangement: recorded acoustic instruments, no synths,
electronic drums, or electronic effects. If the user also requests gradual tempo
changes and a light pulse during reduced layers, preserve those requirements.
These are user preferences, not properties established by this reference's
waveform. For OpenFilm arrangements, keep requested instruments on separate
tracks so the user can adjust them.
