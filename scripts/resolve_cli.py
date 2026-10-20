#!/usr/bin/env python3
"""Small, dependency-free CLI for DaVinci Resolve's official scripting API."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Sequence, Tuple


MARKER_COLORS = {
    "blue",
    "cyan",
    "green",
    "yellow",
    "red",
    "pink",
    "purple",
    "fuchsia",
    "rose",
    "lavender",
    "sky",
    "mint",
    "lemon",
    "sand",
    "cocoa",
    "cream",
}


class ResolveSkillError(RuntimeError):
    """An actionable connection or API error."""


def _existing_file(path: Optional[str]) -> Optional[Path]:
    if not path:
        return None
    candidate = Path(path).expanduser()
    return candidate if candidate.is_file() else None


def _api_root_candidates() -> List[Path]:
    candidates: List[Path] = []
    configured = os.environ.get("RESOLVE_SCRIPT_API")
    if configured:
        candidates.append(Path(configured).expanduser())

    if sys.platform.startswith("win"):
        program_data = os.environ.get("PROGRAMDATA", r"C:\ProgramData")
        candidates.append(
            Path(program_data)
            / "Blackmagic Design"
            / "DaVinci Resolve"
            / "Support"
            / "Developer"
            / "Scripting"
        )
    elif sys.platform == "darwin":
        candidates.append(
            Path(
                "/Library/Application Support/Blackmagic Design/"
                "DaVinci Resolve/Developer/Scripting"
            )
        )
    else:
        candidates.extend(
            [
                Path("/opt/resolve/Developer/Scripting"),
                Path("/home/resolve/Developer/Scripting"),
            ]
        )
    return candidates


def _running_resolve_executable() -> Optional[Path]:
    if not sys.platform.startswith("win"):
        return None
    command = (
        "Get-Process -ErrorAction SilentlyContinue | "
        "Where-Object { $_.ProcessName -in @('Resolve','DaVinci Resolve') -and $_.Path } | "
        "Select-Object -First 1 -ExpandProperty Path"
    )
    try:
        completed = subprocess.run(
            ["powershell", "-NoProfile", "-Command", command],
            capture_output=True,
            text=True,
            timeout=8,
            check=False,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
        )
    except (OSError, subprocess.SubprocessError):
        return None
    lines = completed.stdout.strip().splitlines()
    if not lines:
        return None
    candidate = Path(lines[0].strip())
    return candidate if candidate.is_file() else None


def _lib_candidates() -> List[Path]:
    candidates: List[Path] = []
    configured = _existing_file(os.environ.get("RESOLVE_SCRIPT_LIB"))
    if configured:
        candidates.append(configured)

    running = _running_resolve_executable()
    if running:
        candidates.append(running.parent / "fusionscript.dll")

    if sys.platform.startswith("win"):
        for env_name in ("PROGRAMFILES", "PROGRAMFILES(X86)"):
            root = os.environ.get(env_name)
            if root:
                candidates.append(
                    Path(root)
                    / "Blackmagic Design"
                    / "DaVinci Resolve"
                    / "fusionscript.dll"
                )
    elif sys.platform == "darwin":
        candidates.append(
            Path(
                "/Applications/DaVinci Resolve/DaVinci Resolve.app/"
                "Contents/Libraries/Fusion/fusionscript.so"
            )
        )
    else:
        candidates.extend(
            [
                Path("/opt/resolve/libs/Fusion/fusionscript.so"),
                Path("/home/resolve/libs/Fusion/fusionscript.so"),
            ]
        )
    return candidates


def _first_existing_file(paths: Iterable[Path], label: str) -> Path:
    checked = []
    for path in paths:
        checked.append(str(path))
        if path.is_file():
            return path
    detail = "\n".join("  - " + item for item in checked)
    raise ResolveSkillError(
        "Could not locate {}. Set the corresponding Resolve environment "
        "variable. Checked:\n{}".format(label, detail)
    )


def _first_existing_directory(paths: Iterable[Path], label: str) -> Path:
    checked = []
    for path in paths:
        checked.append(str(path))
        if path.is_dir():
            return path
    detail = "\n".join("  - " + item for item in checked)
    raise ResolveSkillError(
        "Could not locate {}. Set the corresponding Resolve environment "
        "variable. Checked:\n{}".format(label, detail)
    )


def connect() -> Tuple[Any, Dict[str, str]]:
    api_root = _first_existing_directory(
        _api_root_candidates(), "Resolve scripting API directory"
    )
    module_dir = api_root / "Modules"
    if not (module_dir / "DaVinciResolveScript.py").is_file():
        raise ResolveSkillError(
            "DaVinciResolveScript.py is missing under {}".format(module_dir)
        )

    lib_path = _first_existing_file(_lib_candidates(), "fusionscript library")
    os.environ["RESOLVE_SCRIPT_API"] = str(api_root)
    os.environ["RESOLVE_SCRIPT_LIB"] = str(lib_path)

    if sys.platform.startswith("win") and hasattr(os, "add_dll_directory"):
        try:
            os.add_dll_directory(str(lib_path.parent))
        except OSError:
            pass

    module_path = str(module_dir)
    if module_path not in sys.path:
        sys.path.insert(0, module_path)
    try:
        dvr = importlib.import_module("DaVinciResolveScript")
    except Exception as exc:
        raise ResolveSkillError(
            "Unable to import DaVinciResolveScript from {}: {}".format(module_dir, exc)
        ) from exc

    try:
        resolve = dvr.scriptapp("Resolve")
    except Exception as exc:
        raise ResolveSkillError(
            "Resolve is installed but its scripting bridge could not initialize: "
            "{}".format(exc)
        ) from exc
    if resolve is None:
        raise ResolveSkillError(
            "Resolve returned no application object. Keep Resolve open and verify "
            "that local external scripting is enabled."
        )

    return resolve, {
        "api_root": str(api_root),
        "lib_path": str(lib_path),
    }


def _project(resolve: Any) -> Any:
    manager = resolve.GetProjectManager()
    if manager is None:
        raise ResolveSkillError("Resolve did not return a project manager.")
    project = manager.GetCurrentProject()
    if project is None:
        raise ResolveSkillError("No project is currently open in Resolve.")
    return project


def _timeline(project: Any, name: Optional[str] = None) -> Any:
    if name:
        count = int(project.GetTimelineCount() or 0)
        for index in range(1, count + 1):
            candidate = project.GetTimelineByIndex(index)
            if candidate is not None and candidate.GetName() == name:
                if not project.SetCurrentTimeline(candidate):
                    raise ResolveSkillError(
                        "Could not make timeline '{}' current.".format(name)
                    )
                return candidate
        raise ResolveSkillError("Timeline not found: {}".format(name))

    current = project.GetCurrentTimeline()
    if current is None:
        raise ResolveSkillError("The current project has no active timeline.")
    return current


def _jsonable(value: Any) -> Any:
    if value is None or isinstance(value, (bool, int, float, str)):
        return value
    if isinstance(value, Path):
        return str(value)
    if isinstance(value, dict):
        return {str(key): _jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_jsonable(item) for item in value]
    return str(value)


def _number(value: Any) -> Optional[float]:
    if value is None or value == "":
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _safe_call(obj: Any, method: str, default: Any = None, *args: Any) -> Any:
    function = getattr(obj, method, None)
    if function is None:
        return default
    try:
        return function(*args)
    except Exception:
        return default


def _project_summary(project: Any) -> Dict[str, Any]:
    current = project.GetCurrentTimeline()
    return {
        "name": project.GetName(),
        "unique_id": _safe_call(project, "GetUniqueId"),
        "timeline_count": int(project.GetTimelineCount() or 0),
        "current_timeline": current.GetName() if current is not None else None,
        "frame_rate": project.GetSetting("timelineFrameRate"),
        "resolution": {
            "width": project.GetSetting("timelineResolutionWidth"),
            "height": project.GetSetting("timelineResolutionHeight"),
        },
    }


def _timeline_summary(timeline: Any) -> Dict[str, Any]:
    return {
        "name": timeline.GetName(),
        "unique_id": _safe_call(timeline, "GetUniqueId"),
        "start_frame": _safe_call(timeline, "GetStartFrame"),
        "end_frame": _safe_call(timeline, "GetEndFrame"),
        "start_timecode": _safe_call(timeline, "GetStartTimecode"),
        "frame_rate": _safe_call(timeline, "GetSetting", None, "timelineFrameRate"),
        "tracks": {
            track_type: int(_safe_call(timeline, "GetTrackCount", 0, track_type) or 0)
            for track_type in ("video", "audio", "subtitle")
        },
    }


def _media_item_summary(item: Any) -> Dict[str, Any]:
    properties = _safe_call(item, "GetClipProperty", {}) or {}
    return {
        "media_id": _safe_call(item, "GetMediaId"),
        "name": item.GetName(),
        "file_name": properties.get("File Name"),
        "file_path": properties.get("File Path"),
        "frames": properties.get("Frames"),
        "frame_rate": properties.get("Frame Rate") or properties.get("FPS"),
        "type": properties.get("Type"),
        "video_codec": properties.get("Video Codec"),
        "audio_codec": properties.get("Audio Codec"),
        "resolution": properties.get("Resolution"),
    }


def _timeline_item_summary(
    item: Any, track_type: str, track_index: int
) -> Dict[str, Any]:
    source = _safe_call(item, "GetMediaPoolItem")
    source_properties = _safe_call(source, "GetClipProperty", {}) or {}
    return {
        "item_id": _safe_call(item, "GetUniqueId"),
        "name": item.GetName(),
        "track_type": track_type,
        "track_index": track_index,
        "start": _safe_call(item, "GetStart"),
        "end": _safe_call(item, "GetEnd"),
        "duration": _safe_call(item, "GetDuration"),
        "source_start": _safe_call(item, "GetSourceStartFrame"),
        "source_end": _safe_call(item, "GetSourceEndFrame"),
        "source_file": source_properties.get("File Path"),
        "media_id": _safe_call(source, "GetMediaId"),
    }


def _timeline_details(timeline: Any) -> Dict[str, Any]:
    result = _timeline_summary(timeline)
    tracks: Dict[str, List[Dict[str, Any]]] = {}
    for track_type in ("video", "audio", "subtitle"):
        track_count = int(_safe_call(timeline, "GetTrackCount", 0, track_type) or 0)
        for track_index in range(1, track_count + 1):
            items = _safe_call(
                timeline, "GetItemListInTrack", [], track_type, track_index
            ) or []
            tracks["{}{}".format(track_type, track_index)] = [
                _timeline_item_summary(item, track_type, track_index) for item in items
            ]
    result["tracks_by_index"] = tracks
    result["markers"] = _safe_call(timeline, "GetMarkers", {}) or {}
    result["current_timecode"] = _safe_call(timeline, "GetCurrentTimecode")
    return result


def _walk_media(folder: Any, parent: str = "", depth: int = 0) -> List[Dict[str, Any]]:
    if folder is None or depth > 64:
        return []
    folder_name = folder.GetName()
    path = "{}/{}".format(parent, folder_name).strip("/")
    results = []
    for clip in _safe_call(folder, "GetClipList", []) or []:
        item = _media_item_summary(clip)
        item["folder"] = path
        results.append(item)
    for child in _safe_call(folder, "GetSubFolderList", []) or []:
        results.extend(_walk_media(child, path, depth + 1))
    return results


def _find_media_item(folder: Any, media_id: str, depth: int = 0) -> Optional[Any]:
    if folder is None or depth > 64:
        return None
    for clip in _safe_call(folder, "GetClipList", []) or []:
        if str(_safe_call(clip, "GetMediaId")) == media_id:
            return clip
    for child in _safe_call(folder, "GetSubFolderList", []) or []:
        found = _find_media_item(child, media_id, depth + 1)
        if found is not None:
            return found
    return None


def _validate_paths(paths: Sequence[str]) -> List[Path]:
    validated = []
    for raw in paths:
        path = Path(raw).expanduser().resolve()
        if not path.exists():
            raise ResolveSkillError("Media path does not exist: {}".format(path))
        validated.append(path)
    if not validated:
        raise ResolveSkillError("At least one media path is required.")
    return validated


def _import_media(media_pool: Any, paths: Sequence[str]) -> List[Any]:
    validated = _validate_paths(paths)
    imported = media_pool.ImportMedia([str(path) for path in validated])
    if not imported:
        raise ResolveSkillError(
            "Resolve could not import the supplied media. Check codec support and "
            "the current media pool folder."
        )
    return list(imported)


def _clip_info(
    clip: Any,
    start_frame: Optional[int],
    end_frame: Optional[int],
    record_frame: Optional[int],
    track_index: Optional[int],
) -> Any:
    if (
        start_frame is None
        and end_frame is None
        and record_frame is None
        and track_index is None
    ):
        return clip

    start = 0 if start_frame is None else start_frame
    end = end_frame
    if end is None:
        frames = _number(_safe_call(clip, "GetClipProperty", None, "Frames"))
        if frames is None or frames < 1:
            raise ResolveSkillError(
                "Could not derive the source end frame; pass --end-frame explicitly."
            )
        end = int(frames) - 1
    if end < start:
        raise ResolveSkillError(
            "Source end frame {} is before start frame {}.".format(end, start)
        )

    info: Dict[str, Any] = {
        "mediaPoolItem": clip,
        "startFrame": start,
        "endFrame": end,
    }
    if record_frame is not None:
        info["recordFrame"] = record_frame
    if track_index is not None:
        info["trackIndex"] = track_index
    return info


def _find_items(timeline: Any, item_ids: Sequence[str]) -> List[Any]:
    wanted = set(item_ids)
    found: List[Any] = []
    for track_type in ("video", "audio", "subtitle"):
        track_count = int(_safe_call(timeline, "GetTrackCount", 0, track_type) or 0)
        for track_index in range(1, track_count + 1):
            items = _safe_call(
                timeline, "GetItemListInTrack", [], track_type, track_index
            ) or []
            for item in items:
                if str(_safe_call(item, "GetUniqueId")) in wanted:
                    found.append(item)
    missing = wanted - {str(_safe_call(item, "GetUniqueId")) for item in found}
    if missing:
        raise ResolveSkillError(
            "Timeline item IDs not found: {}".format(", ".join(sorted(missing)))
        )
    return found


def _parse_property_value(raw: str) -> Any:
    try:
        return json.loads(raw)
    except json.JSONDecodeError:
        return raw


def command_status(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, connection = connect()
    manager = resolve.GetProjectManager()
    database = _safe_call(manager, "GetCurrentDatabase", {}) or {}
    project = manager.GetCurrentProject()
    return {
        "connected": True,
        "product": _safe_call(resolve, "GetProductName"),
        "version": _safe_call(resolve, "GetVersionString"),
        "page": _safe_call(resolve, "GetCurrentPage"),
        "database": database,
        "project": _project_summary(project) if project is not None else None,
        "connection": connection,
    }


def command_list_projects(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    manager = resolve.GetProjectManager()
    current = manager.GetCurrentProject()
    return {
        "current_project": current.GetName() if current is not None else None,
        "projects": list(manager.GetProjectListInCurrentFolder() or []),
    }


def command_open_project(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    manager = resolve.GetProjectManager()
    project = manager.LoadProject(args.name)
    if project is None:
        raise ResolveSkillError(
            "Could not open project '{}'. Confirm its exact name with "
            "list-projects.".format(args.name)
        )
    return {
        "project": _project_summary(project),
        "page": _safe_call(resolve, "GetCurrentPage"),
    }


def command_list_timelines(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    current = project.GetCurrentTimeline()
    current_id = _safe_call(current, "GetUniqueId") if current is not None else None
    timelines = []
    count = int(project.GetTimelineCount() or 0)
    for index in range(1, count + 1):
        timeline = project.GetTimelineByIndex(index)
        if timeline is None:
            continue
        summary = _timeline_summary(timeline)
        summary["index"] = index
        summary["current"] = _safe_call(timeline, "GetUniqueId") == current_id
        timelines.append(summary)
    return {"project": project.GetName(), "timelines": timelines}


def command_inspect_timeline(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    timeline = _timeline(project, args.timeline)
    return {"project": project.GetName(), "timeline": _timeline_details(timeline)}


def command_list_media(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    media = _walk_media(project.GetMediaPool().GetRootFolder())
    return {
        "project": project.GetName(),
        "count": len(media),
        "returned": min(len(media), args.limit),
        "items": media[: args.limit],
    }


def command_set_current_timeline(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    timeline = _timeline(project, args.timeline)
    return {
        "project": project.GetName(),
        "current_timeline": timeline.GetName(),
        "timeline_id": _safe_call(timeline, "GetUniqueId"),
    }


def command_duplicate_timeline(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    source = _timeline(project, args.timeline)
    duplicate = source.DuplicateTimeline(args.name)
    if duplicate is None:
        raise ResolveSkillError("Resolve did not create the duplicate timeline.")
    return {
        "project": project.GetName(),
        "source": source.GetName(),
        "created": _timeline_details(duplicate),
    }


def command_delete_timeline(args: argparse.Namespace) -> Dict[str, Any]:
    if not args.confirm:
        raise ResolveSkillError("delete-timeline requires --confirm.")
    resolve, _ = connect()
    project = _project(resolve)
    target = _timeline(project, args.name)
    target_id = _safe_call(target, "GetUniqueId")
    before = int(project.GetTimelineCount() or 0)
    ok = project.GetMediaPool().DeleteTimelines([target])
    if not ok:
        raise ResolveSkillError(
            "Resolve did not delete timeline '{}'.".format(args.name)
        )
    remaining = []
    for index in range(1, int(project.GetTimelineCount() or 0) + 1):
        timeline = project.GetTimelineByIndex(index)
        if timeline is not None:
            remaining.append(timeline.GetName())
    return {
        "project": project.GetName(),
        "deleted_timeline": args.name,
        "deleted_timeline_id": target_id,
        "timeline_count_before": before,
        "timeline_count_after": len(remaining),
        "remaining_timelines": remaining,
    }


def command_create_timeline(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    media_pool = project.GetMediaPool()
    timeline = media_pool.CreateEmptyTimeline(args.name)
    if timeline is None:
        raise ResolveSkillError(
            "Could not create timeline '{}'. Choose a unique name.".format(args.name)
        )
    project.SetCurrentTimeline(timeline)
    inserted = None
    if args.generator:
        inserted = timeline.InsertGeneratorIntoTimeline(args.generator)
        if inserted is None:
            raise ResolveSkillError(
                "Timeline was created, but generator '{}' was not recognized.".format(
                    args.generator
                )
            )
    return {
        "project": project.GetName(),
        "timeline": _timeline_details(timeline),
        "generator_inserted": inserted is not None,
    }


def command_import_media(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    clips = _import_media(project.GetMediaPool(), args.paths)
    return {
        "project": project.GetName(),
        "count": len(clips),
        "imported": [_media_item_summary(clip) for clip in clips],
    }


def command_append_media(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    timeline = _timeline(project, args.timeline)
    media_pool = project.GetMediaPool()
    clips = _import_media(media_pool, args.paths)
    infos = [
        _clip_info(
            clip,
            args.start_frame,
            args.end_frame,
            args.record_frame,
            args.track_index,
        )
        for clip in clips
    ]
    appended = media_pool.AppendToTimeline(infos)
    if not appended:
        raise ResolveSkillError(
            "Media was imported but Resolve did not append it to '{}'.".format(
                timeline.GetName()
            )
        )
    return {
        "project": project.GetName(),
        "timeline": timeline.GetName(),
        "appended": [
            _timeline_item_summary(item, "unknown", 0) for item in appended
        ],
        "timeline_end_frame": timeline.GetEndFrame(),
    }


def command_append_media_item(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    timeline = _timeline(project, args.timeline)
    media_pool = project.GetMediaPool()
    clip = _find_media_item(media_pool.GetRootFolder(), args.media_id)
    if clip is None:
        raise ResolveSkillError(
            "Media-pool item not found: {}".format(args.media_id)
        )
    info = _clip_info(
        clip,
        args.start_frame,
        args.end_frame,
        args.record_frame,
        args.track_index,
    )
    appended = media_pool.AppendToTimeline([info])
    if not appended:
        raise ResolveSkillError(
            "Resolve did not append media item '{}' to '{}'.".format(
                args.media_id, timeline.GetName()
            )
        )
    return {
        "project": project.GetName(),
        "timeline": timeline.GetName(),
        "source_item": _media_item_summary(clip),
        "appended": [
            _timeline_item_summary(item, "unknown", 0) for item in appended
        ],
        "timeline_end_frame": timeline.GetEndFrame(),
    }


def command_insert_generator(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    timeline = _timeline(project, args.timeline)
    inserted = timeline.InsertGeneratorIntoTimeline(args.generator)
    if inserted is None:
        raise ResolveSkillError(
            "Generator '{}' was not accepted by Resolve.".format(args.generator)
        )
    return {
        "project": project.GetName(),
        "timeline": timeline.GetName(),
        "item": _timeline_item_summary(inserted, "video", 0),
    }


def command_add_marker(args: argparse.Namespace) -> Dict[str, Any]:
    color = args.color.capitalize()
    if color.lower() not in MARKER_COLORS:
        raise ResolveSkillError(
            "Unsupported marker color '{}'. Use one of: {}.".format(
                args.color, ", ".join(sorted(MARKER_COLORS))
            )
        )
    resolve, _ = connect()
    project = _project(resolve)
    timeline = _timeline(project, args.timeline)
    ok = timeline.AddMarker(
        args.frame,
        color,
        args.name,
        args.note,
        args.duration,
        args.custom_data,
    )
    if not ok:
        raise ResolveSkillError(
            "Resolve did not add the marker at frame {}.".format(args.frame)
        )
    markers = timeline.GetMarkers() or {}
    verified = any(str(marker_frame) == str(args.frame) for marker_frame in markers)
    return {
        "project": project.GetName(),
        "timeline": timeline.GetName(),
        "frame": args.frame,
        "verified": verified,
        "marker": markers.get(args.frame),
    }


def command_set_clip_property(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    timeline = _timeline(project, args.timeline)
    items = _find_items(timeline, [args.item_id])
    value = _parse_property_value(args.value)
    ok = items[0].SetProperty(args.property, value)
    if not ok:
        raise ResolveSkillError(
            "Resolve rejected property '{}' with value {!r}.".format(
                args.property, value
            )
        )
    return {
        "project": project.GetName(),
        "timeline": timeline.GetName(),
        "item_id": args.item_id,
        "property": args.property,
        "value": value,
        "read_back": items[0].GetProperty(args.property),
    }


def command_delete_clips(args: argparse.Namespace) -> Dict[str, Any]:
    if not args.confirm:
        raise ResolveSkillError("delete-clips requires --confirm.")
    resolve, _ = connect()
    project = _project(resolve)
    timeline = _timeline(project, args.timeline)
    items = _find_items(timeline, args.item_id)
    before = timeline.GetEndFrame()
    ok = timeline.DeleteClips(items, args.ripple)
    if not ok:
        raise ResolveSkillError("Resolve did not delete the requested timeline items.")
    return {
        "project": project.GetName(),
        "timeline": timeline.GetName(),
        "deleted_item_ids": args.item_id,
        "ripple": args.ripple,
        "timeline_end_before": before,
        "timeline_end_after": timeline.GetEndFrame(),
    }


def command_export_timeline(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, _ = connect()
    project = _project(resolve)
    timeline = _timeline(project, args.timeline)
    output = Path(args.output).expanduser().resolve()
    output.parent.mkdir(parents=True, exist_ok=True)

    export_types = {
        "otio": ("EXPORT_OTIO", "EXPORT_NONE"),
        "fcpxml": ("EXPORT_FCPXML_1_10", "EXPORT_NONE"),
        "drt": ("EXPORT_DRT", "EXPORT_NONE"),
    }
    type_name, subtype_name = export_types[args.format]
    export_type = getattr(resolve, type_name, None)
    export_subtype = getattr(resolve, subtype_name, None)
    if export_type is None or export_subtype is None:
        raise ResolveSkillError(
            "This Resolve version does not expose {}.".format(args.format)
        )
    ok = timeline.Export(str(output), export_type, export_subtype)
    produced = output.is_file() or output.is_dir()
    artifacts = (
        [path for path in output.rglob("*") if path.is_file()]
        if output.is_dir()
        else [output]
    )
    if not ok or not produced or not artifacts:
        raise ResolveSkillError(
            "Resolve did not produce the export at {}.".format(output)
        )
    return {
        "project": project.GetName(),
        "timeline": timeline.GetName(),
        "format": args.format,
        "output": str(output),
        "output_type": "directory-package" if output.is_dir() else "file",
        "artifact_count": len(artifacts),
        "bytes": sum(path.stat().st_size for path in artifacts),
    }


def command_self_test(args: argparse.Namespace) -> Dict[str, Any]:
    resolve, connection = connect()
    project = _project(resolve)
    manager = project.GetMediaPool()
    original = project.GetCurrentTimeline()
    original_id = _safe_call(original, "GetUniqueId") if original is not None else None
    stamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S_%f")
    test_name = "CODEX_SKILL_TEST_{}".format(stamp)
    test_timeline = None
    created_timelines: List[Any] = []
    steps: List[Dict[str, Any]] = []
    error: Optional[str] = None
    cleanup_ok = False

    try:
        test_timeline = manager.CreateEmptyTimeline(test_name)
        if test_timeline is None:
            raise ResolveSkillError("Temporary timeline creation failed.")
        project.SetCurrentTimeline(test_timeline)
        created_timelines.append(test_timeline)
        steps.append(
            {
                "operation": "create-empty-timeline",
                "ok": True,
                "timeline": test_timeline.GetName(),
            }
        )

        inserted = None
        used_generator = None
        for generator in ("Solid Color", "Color Generator", "Color Bars"):
            try:
                inserted = test_timeline.InsertGeneratorIntoTimeline(generator)
            except Exception:
                inserted = None
            if inserted is not None:
                used_generator = generator
                break
        steps.append(
            {
                "operation": "insert-generator",
                "ok": inserted is not None,
                "generator": used_generator,
            }
        )

        marker_ok = test_timeline.AddMarker(
            0,
            "Blue",
            "Codex Skill Test",
            "Local API write test",
            1,
            "codex-selftest",
        )
        markers = test_timeline.GetMarkers() or {}
        marker_verified = any(str(frame) == "0" for frame in markers)
        steps.append(
            {
                "operation": "add-marker",
                "ok": bool(marker_ok),
                "verified": marker_verified,
            }
        )
        if not marker_ok or not marker_verified:
            raise ResolveSkillError("Marker write or read-back verification failed.")

    except Exception as exc:
        error = str(exc)
    finally:
        if created_timelines:
            created_ids = {
                str(_safe_call(timeline, "GetUniqueId"))
                for timeline in created_timelines
            }
            if original_id is not None and str(original_id) in created_ids:
                cleanup_ok = False
                error = error or "Refused to delete the original timeline."
            else:
                cleanup_ok = bool(manager.DeleteTimelines(created_timelines))
        else:
            cleanup_ok = True

        if original is not None:
            try:
                project.SetCurrentTimeline(original)
                restored = project.GetCurrentTimeline()
                if restored is None or _safe_call(restored, "GetUniqueId") != original_id:
                    error = error or "Could not restore the original current timeline."
            except Exception as exc:
                error = error or "Could not restore the original timeline: {}".format(exc)

    write_steps = [
        step for step in steps if step["operation"] != "create-empty-timeline"
    ]
    write_test_ok = any(step.get("ok") for step in write_steps)
    current_after = project.GetCurrentTimeline()
    return {
        "success": error is None and write_test_ok and cleanup_ok,
        "connected": True,
        "project": project.GetName(),
        "original_timeline": original.GetName() if original is not None else None,
        "temporary_timeline": test_name,
        "steps": steps,
        "cleanup_ok": cleanup_ok,
        "original_restored": (
            current_after is not None
            and _safe_call(current_after, "GetUniqueId") == original_id
        ),
        "error": error,
        "connection": connection,
        "timeline_count_after": project.GetTimelineCount(),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Inspect and edit a running DaVinci Resolve Studio project."
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    subparsers.add_parser("status", help="Show Resolve and current-project status.")
    subparsers.add_parser("list-projects", help="List projects in the current folder.")
    open_project = subparsers.add_parser(
        "open-project", help="Open an existing project by exact name."
    )
    open_project.add_argument("--name", required=True)
    subparsers.add_parser("list-timelines", help="List timelines in the current project.")

    inspect = subparsers.add_parser(
        "inspect-timeline", help="Inspect timeline tracks, clips, and markers."
    )
    inspect.add_argument("--timeline")

    media = subparsers.add_parser("list-media", help="List the project media pool.")
    media.add_argument("--limit", type=int, default=500)

    set_current = subparsers.add_parser(
        "set-current-timeline", help="Make a named timeline current."
    )
    set_current.add_argument("--timeline", required=True)

    duplicate = subparsers.add_parser(
        "duplicate-timeline", help="Duplicate a timeline without changing its source."
    )
    duplicate.add_argument("--timeline")
    duplicate.add_argument("--name", required=True)

    delete_timeline = subparsers.add_parser(
        "delete-timeline", help="Delete one explicitly named timeline."
    )
    delete_timeline.add_argument("--name", required=True)
    delete_timeline.add_argument("--confirm", action="store_true")

    create = subparsers.add_parser("create-timeline", help="Create an empty timeline.")
    create.add_argument("--name", required=True)
    create.add_argument("--generator")

    import_media = subparsers.add_parser(
        "import-media", help="Import media into the current media pool folder."
    )
    import_media.add_argument("paths", nargs="+")

    append_media = subparsers.add_parser(
        "append-media", help="Import and append media to a timeline."
    )
    append_media.add_argument("paths", nargs="+")
    append_media.add_argument("--timeline")
    append_media.add_argument("--start-frame", type=int)
    append_media.add_argument("--end-frame", type=int)
    append_media.add_argument("--record-frame", type=int)
    append_media.add_argument("--track-index", type=int)

    append_item = subparsers.add_parser(
        "append-media-item",
        help="Append an existing media-pool item without importing it again.",
    )
    append_item.add_argument("--media-id", required=True)
    append_item.add_argument("--timeline")
    append_item.add_argument("--start-frame", type=int)
    append_item.add_argument("--end-frame", type=int)
    append_item.add_argument("--record-frame", type=int)
    append_item.add_argument("--track-index", type=int)

    generator = subparsers.add_parser(
        "insert-generator", help="Insert a standard generator into a timeline."
    )
    generator.add_argument("--generator", required=True)
    generator.add_argument("--timeline")

    marker = subparsers.add_parser("add-marker", help="Add and verify a timeline marker.")
    marker.add_argument("--frame", type=int, required=True)
    marker.add_argument("--timeline")
    marker.add_argument("--name", default="Codex Marker")
    marker.add_argument("--note", default="")
    marker.add_argument("--color", default="Blue")
    marker.add_argument("--duration", type=int, default=1)
    marker.add_argument("--custom-data", default="")

    prop = subparsers.add_parser(
        "set-clip-property", help="Set a property on one timeline item."
    )
    prop.add_argument("--item-id", required=True)
    prop.add_argument("--property", required=True)
    prop.add_argument("--value", required=True)
    prop.add_argument("--timeline")

    delete = subparsers.add_parser(
        "delete-clips", help="Delete explicit timeline item IDs."
    )
    delete.add_argument("--item-id", action="append", required=True)
    delete.add_argument("--timeline")
    delete.add_argument("--ripple", action="store_true")
    delete.add_argument("--confirm", action="store_true")

    export = subparsers.add_parser(
        "export-timeline", help="Export a timeline as OTIO, FCPXML, or DRT."
    )
    export.add_argument("--timeline", required=True)
    export.add_argument("--output", required=True)
    export.add_argument("--format", choices=("otio", "fcpxml", "drt"), required=True)

    subparsers.add_parser(
        "self-test", help="Run a reversible local read/write/cleanup smoke test."
    )
    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")

    parser = build_parser()
    args = parser.parse_args(argv)
    handlers = {
        "status": command_status,
        "list-projects": command_list_projects,
        "open-project": command_open_project,
        "list-timelines": command_list_timelines,
        "inspect-timeline": command_inspect_timeline,
        "list-media": command_list_media,
        "set-current-timeline": command_set_current_timeline,
        "duplicate-timeline": command_duplicate_timeline,
        "delete-timeline": command_delete_timeline,
        "create-timeline": command_create_timeline,
        "import-media": command_import_media,
        "append-media": command_append_media,
        "append-media-item": command_append_media_item,
        "insert-generator": command_insert_generator,
        "add-marker": command_add_marker,
        "set-clip-property": command_set_clip_property,
        "delete-clips": command_delete_clips,
        "export-timeline": command_export_timeline,
        "self-test": command_self_test,
    }
    try:
        result = handlers[args.command](args)
        print(json.dumps(_jsonable(result), ensure_ascii=False, indent=2))
        if isinstance(result, dict) and result.get("success") is False:
            return 1
        return 0
    except ResolveSkillError as exc:
        print(json.dumps({"success": False, "error": str(exc)}, ensure_ascii=False))
        return 1
    except Exception as exc:
        print(
            json.dumps(
                {
                    "success": False,
                    "error": "{}: {}".format(type(exc).__name__, exc),
                },
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())

