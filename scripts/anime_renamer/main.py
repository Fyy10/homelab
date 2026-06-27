#!/usr/bin/env python3
import argparse
import csv
import os
import re
from collections import Counter, defaultdict
from pathlib import Path

VIDEO_EXTS = {".mkv", ".mp4", ".m4v", ".avi", ".mov", ".wmv", ".flv", ".ts", ".webm"}
SUB_EXTS = {".ass", ".srt", ".ssa", ".vtt", ".sub"}
TITLE_STRIP_EXTS = VIDEO_EXTS | SUB_EXTS | {".mka", ".flac", ".cue", ".log", ".jpg", ".jpeg", ".png", ".webp", ".7z", ".zip", ".rar"}
EXTRA_RE = re.compile(
    r"(映像特典|次回予告|特典|番宣|予告|"
    r"(?<![A-Za-z0-9])(?:NCOP|NCED|OP|ED|PV|CM|MENU)\d*(?![A-Za-z0-9])|"
    r"(?<![A-Za-z0-9])(?:EXTRA|SPs?|Scan|Scans|Fonts)(?![A-Za-z0-9]))",
    re.I,
)
SPECIAL_RE = re.compile(r"\b(OVA|OAD|SP|Special|Bonus)\d*\b", re.I)
MOVIE_RE = re.compile(r"\b(Movie|The Movie|Chapter|劇場版|剧场版)\b", re.I)
BAD_CHARS_RE = re.compile(r'[<>:"/\\|?*\x00-\x1f]')
RANGE_RE = re.compile(r"^\d{1,3}\s*[-~]\s*\d{1,3}(?:\D.*)?$", re.I)
TITLE_EPISODE_RE = re.compile(r"(?:^|[\s._-])(?P<episode>\d{1,3})(?=\s*(?:\[[^\]]+\]\s*)*(?:\.[^.]+)?$)")
QUALITY_TAG_RE = re.compile(
    r"(?<![A-Za-z0-9])("
    r"2160p|1080p|720p|480p|1920x1080|1280x720|UHD|4K|HDR10\+?|DV|WEB-?DL|WEBRip|BluRay|BDRip|BD|"
    r"HEVC|H\.?265|x265|AVC|H\.?264|x264|AV1|10bit|Hi10P|YUV420P10|AAC|FLAC|OPUS|DTS|TrueHD|Atmos|Dual Audio|"
    r"CHS|CHT|GB|BIG5|MP4|MKV|ASSx?\d*|\u7b80|\u7e41|\u5185\u5c01|\u5916\u6302"
    r")(?![A-Za-z0-9])",
    re.I,
)
GROUP_HINT_RE = re.compile(
    r"(?<![A-Za-z0-9])(?:sub|raw|raws|studio|house|team|dmg|airota|loli|vcb|hysub|ktxp|caso|sumisora|comicat|uha-wings)(?![A-Za-z0-9])",
    re.I,
)
KNOWN_RELEASE_GROUPS = {"jyfansub", "moozzi2", "uha-wings"}
AUXILIARY_DIR_RE = re.compile(
    r"^(?:SPs?|Specials?|Extras?|Extra|Fonts?|Scans?|Scan|Menu|"
    r"NCOP(?:&|and)?NCED|NCOP|NCED|OP|ED|PV|CM|映像特典|特典|番宣|次回予告|予告)$",
    re.I,
)
SEASON_DIR_RE = re.compile(r"^(?:S(?P<season>\d{1,2})(?:\+OAD|\+OVA|\+SP)?|Season\s*(?P<season_word>\d{1,2}))$", re.I)


def clean_filename(name: str) -> str:
    name = BAD_CHARS_RE.sub(" ", name)
    name = re.sub(r"\s+", " ", name)
    return name.strip(" .")


def title_stem(name: str) -> str:
    path = Path(name)
    if path.suffix.lower() in TITLE_STRIP_EXTS:
        return path.stem
    return path.name


def is_quality_token(token: str) -> bool:
    return bool(QUALITY_TAG_RE.search(token))


def is_release_group_token(token: str, index: int) -> bool:
    if index != 0:
        return False
    normalized = re.sub(r"[\s._-]+", "", token).lower()
    return bool(
        "&" in token
        or normalized in {re.sub(r"[\s._-]+", "", group).lower() for group in KNOWN_RELEASE_GROUPS}
        or GROUP_HINT_RE.search(token)
    )


def is_non_title_token(token: str, index: int) -> bool:
    if not token:
        return True
    if is_release_group_token(token, index):
        return True
    if is_quality_token(token):
        return True
    if RANGE_RE.match(token):
        return True
    if re.fullmatch(r"S\d+(?:\+S\d+)?(?:\+\w+)*", token, re.I):
        return True
    if re.fullmatch(r"Vol\.?\s*\d+.*", token, re.I):
        return True
    if token.lower() in {"final", "fin", "rev", "extra", "menu", "sp"} or token in {"国漫"}:
        return True
    return False


def is_auxiliary_directory(name: str) -> bool:
    normalized = re.sub(r"[\s._-]+", " ", name).strip()
    compact = re.sub(r"[\s._-]+", "", name).strip()
    return bool(AUXILIARY_DIR_RE.fullmatch(normalized) or AUXILIARY_DIR_RE.fullmatch(compact))


def season_from_directory_name(name: str) -> str:
    normalized = re.sub(r"[\s._-]+", "", name).strip()
    if m := SEASON_DIR_RE.fullmatch(normalized):
        return str(int(m.group("season") or m.group("season_word")))
    return ""


def strip_season_suffix(title: str, raw_min_episode: int | None) -> tuple[str, str]:
    if raw_min_episode and raw_min_episode >= 13:
        if m := re.search(r"(.+?)(?:\s+|_)(?P<season>[2-9])$", title):
            return m.group(1), m.group("season")
    if m := re.search(r"(.+?)\s+S(?P<season>[1-9])$", title, re.I):
        return m.group(1), m.group("season")
    return title, ""


def clean_title(name: str, raw_min_episode: int | None = None) -> tuple[str, str]:
    stem = title_stem(name)
    bracket_tokens = re.findall(r"\[([^\]]+)\]", stem)
    outside = re.sub(r"\[[^\]]+\]", " ", stem)
    outside = re.sub(r"^\s*[-_]+", "", outside)
    outside = re.sub(r"\s+", " ", outside).strip(" -_.")
    if outside and not is_non_title_token(outside, 99):
        outside = re.sub(r"\b(S\d{1,2}E\d{1,3}|EP?\s*\d{1,3})\b.*$", "", outside, flags=re.I)
        outside = re.sub(r"\s+-\s+\d{1,3}.*$", "", outside)
        if raw_min_episode is not None and not re.search(r"\b(?:Chapter|Movie|Part)\s+\d{1,3}$", outside, re.I):
            outside = re.sub(r"(?<!\d)\s+\d{1,3}$", "", outside)
        outside, season_hint = strip_season_suffix(outside, raw_min_episode)
        return clean_filename(outside), season_hint

    if bracket_tokens:
        candidates = [token.strip() for i, token in enumerate(bracket_tokens) if not is_non_title_token(token.strip(), i)]
        if candidates:
            title = candidates[0]
            title, season_hint = strip_season_suffix(title, raw_min_episode)
            return clean_filename(title), season_hint

    title = re.sub(r"^\[[^\]]+\]\s*", "", stem)
    title = re.sub(r"\[([^\]]+)\]", lambda m: "" if is_non_title_token(m.group(1), 99) else m.group(0), title)
    title = re.sub(r"\b(S\d{1,2}E\d{1,3}|EP?\s*\d{1,3})\b.*$", "", title, flags=re.I)
    title = re.sub(r"\s+-\s+\d{1,3}.*$", "", title)
    title = re.sub(r"\[\d{1,3}\].*$", "", title)
    if raw_min_episode is not None and not re.search(r"\b(?:Chapter|Movie|Part)\s+\d{1,3}$", title, re.I):
        title = re.sub(r"(?<!\d)\s+\d{1,3}$", "", title)
    title = re.sub(r"\s+", " ", title)
    title, season_hint = strip_season_suffix(title, raw_min_episode)
    return clean_filename(title), season_hint


def extract_release_tags(*names: str) -> str:
    tags: list[str] = []
    for name in names:
        current_tags: list[str] = []
        for bracketed in re.findall(r"\[([^\]]+)\]", name):
            if is_quality_token(bracketed):
                current_tags.append(clean_filename(bracketed))

        if not current_tags:
            loose = " ".join(QUALITY_TAG_RE.findall(name))
            if loose:
                current_tags.append(clean_filename(loose))

        if current_tags:
            tags.extend(current_tags)
            break

    seen: set[str] = set()
    deduped: list[str] = []
    for tag in tags:
        key = tag.lower()
        if key not in seen:
            seen.add(key)
            deduped.append(tag)
    return " ".join(f"[{tag}]" for tag in deduped)


def guess_episode(name: str) -> tuple[str, str, str, str, str]:
    if m := re.search(r"S(?P<season>\d{1,2})E(?P<episode>\d{1,3})", name, re.I):
        return str(int(m.group("season"))), str(int(m.group("episode"))), str(int(m.group("episode"))), "high", "SxxEyy"
    if m := re.search(r"\b(?:SP|OVA|OAD|Special)\s*(?P<episode>\d{1,3})\b", name, re.I):
        return "0", str(int(m.group("episode"))), str(int(m.group("episode"))), "medium", "special nn"
    if m := re.search(r"\[(?P<episode>\d{1,3})\]", name):
        return "1", str(int(m.group("episode"))), str(int(m.group("episode"))), "medium", "[nn]"
    if m := re.search(r"(?:^|\s-\s)(?P<episode>\d{1,3})(?:\D|$)", name):
        return "1", str(int(m.group("episode"))), str(int(m.group("episode"))), "medium", "- nn"
    if not MOVIE_RE.search(name):
        if m := TITLE_EPISODE_RE.search(name):
            return "1", str(int(m.group("episode"))), str(int(m.group("episode"))), "medium", "title nn"
    return "", "", "", "low", ""


def has_continuous_episode_numbers(paths: list[Path]) -> bool:
    numbers: list[int] = []
    for path in paths:
        _season, _episode, raw_episode, confidence, _pattern = guess_episode(path.name)
        if confidence == "low" or not raw_episode:
            continue
        if EXTRA_RE.search(str(path)) or SPECIAL_RE.search(str(path)) or MOVIE_RE.search(path.name):
            continue
        numbers.append(int(raw_episode))

    if len(numbers) < 3:
        return False

    unique_numbers = sorted(set(numbers))
    if len(unique_numbers) != len(numbers):
        return False

    return unique_numbers == list(range(unique_numbers[0], unique_numbers[-1] + 1))


def append_note(row: dict[str, str], note: str) -> None:
    notes = [current for current in row.get("notes", "").split(";") if current]
    notes.append(note)
    row["notes"] = ";".join(dict.fromkeys(notes))


def annotate_destination_conflicts(rows: list[dict[str, str]]) -> None:
    destinations: dict[str, list[dict[str, str]]] = defaultdict(list)
    for row in rows:
        try:
            destination = destination_for(row, Path("__DEST__"), append_release_tags=False)
        except (TypeError, ValueError):
            continue
        destinations[str(destination).lower()].append(row)

    for conflict_rows in destinations.values():
        source_paths = {row["source_path"] for row in conflict_rows}
        if len(source_paths) <= 1:
            continue
        for row in conflict_rows:
            append_note(row, "destination_conflict")


def infer_directory_context(paths: list[Path]) -> dict[str, str]:
    raw_numbers: list[int] = []
    explicit_seasons: list[int] = []
    for path in paths:
        season, _episode, raw_episode, confidence, _pattern = guess_episode(path.name)
        if raw_episode:
            raw_numbers.append(int(raw_episode))
        if confidence == "high" and season:
            explicit_seasons.append(int(season))

    raw_min = min(raw_numbers) if raw_numbers else None
    raw_max = max(raw_numbers) if raw_numbers else None
    title_source_dir = paths[0].parent
    if is_auxiliary_directory(title_source_dir.name) and title_source_dir.parent != title_source_dir:
        title_source_dir = title_source_dir.parent

    directory_season_hint = season_from_directory_name(title_source_dir.name)
    if directory_season_hint and title_source_dir.parent != title_source_dir:
        title_source_dir = title_source_dir.parent

    parent_title, parent_season_hint = clean_title(title_source_dir.name, raw_min)
    file_title, file_season_hint = clean_title(paths[0].name, raw_min)
    title = parent_title or file_title

    season_hint = ""
    notes: list[str] = []
    if explicit_seasons:
        season_hint = str(Counter(explicit_seasons).most_common(1)[0][0])
    elif directory_season_hint:
        season_hint = directory_season_hint
        notes.append("season_from_directory")
    elif parent_season_hint:
        season_hint = parent_season_hint
        notes.append("season_from_directory")
    elif file_season_hint:
        season_hint = file_season_hint
        notes.append("season_from_filename")

    episode_offset = 0
    if raw_min and raw_max and raw_min >= 13 and raw_max <= raw_min + 30:
        if season_hint and int(season_hint) > 1:
            episode_offset = raw_min - 1
            notes.append(f"absolute_episode_offset={episode_offset}")
        else:
            notes.append("absolute_episode_range_needs_review")

    return {
        "title": title,
        "season_hint": season_hint,
        "episode_offset": str(episode_offset),
        "notes": ";".join(notes),
    }


def make_plan(source_root: Path, include_extras: bool, include_specials: bool) -> list[dict[str, str]]:
    video_files = sorted(path for path in source_root.rglob("*") if path.is_file() and path.suffix.lower() in VIDEO_EXTS)
    by_dir: dict[Path, list[Path]] = defaultdict(list)
    for path in video_files:
        by_dir[path.parent].append(path)

    rows: list[dict[str, str]] = []
    for _directory, paths in sorted(by_dir.items()):
        context = infer_directory_context(paths)
        continuous_episodes = has_continuous_episode_numbers(paths)
        for path in paths:
            season, episode, raw_episode, confidence, pattern = guess_episode(path.name)
            notes = [note for note in context["notes"].split(";") if note]
            title = context["title"]
            category = "Episode"
            library = "Anime"
            include = "true"

            if context["season_hint"] and confidence != "high":
                season = context["season_hint"]
            if raw_episode and context["episode_offset"] != "0":
                episode = str(int(raw_episode) - int(context["episode_offset"]))

            full_text = str(path)
            if EXTRA_RE.search(full_text):
                category = "Extra"
                include = "true" if include_extras else "false"
                notes.append("extra_keyword")
            elif SPECIAL_RE.search(full_text) and confidence == "low":
                category = "Special"
                season = "0"
                include = "false"
                notes.append("special_needs_mapping")
            elif SPECIAL_RE.search(full_text) and season == "0":
                category = "Special"
                include = "true" if include_specials else "false"
            elif MOVIE_RE.search(path.name) and confidence == "low":
                category = "Movie"
                library = "Anime Movies"
            elif confidence == "low":
                include = "false"
                notes.append("needs_manual_episode")

            if category == "Episode" and continuous_episodes and confidence == "medium":
                confidence = "high"
                notes.append("continuous_episode_sequence")

            if category == "Episode" and raw_episode and int(raw_episode) > 99:
                include = "false"
                notes.append("episode_number_suspicious")

            rows.append(
                {
                    "include": include,
                    "category": category,
                    "library": library,
                    "title": title,
                    "year": "",
                    "season": season,
                    "episode": episode,
                    "raw_episode": raw_episode,
                    "episode_title": "",
                    "release_tags": extract_release_tags(path.name, path.parent.name),
                    "source_path": str(path),
                    "confidence": confidence,
                    "pattern": pattern,
                    "notes": ";".join(dict.fromkeys(notes)),
                }
            )
    annotate_destination_conflicts(rows)
    return rows


def destination_for(row: dict[str, str], dest_root: Path, append_release_tags: bool) -> Path:
    title = clean_filename(row["title"])
    year_suffix = f" ({row['year']})" if row.get("year") else ""
    display_title = f"{title}{year_suffix}"
    ext = Path(row["source_path"]).suffix
    release_tags = f" {row.get('release_tags', '').strip()}" if append_release_tags and row.get("release_tags") else ""

    if row["category"] == "Movie":
        return dest_root / row["library"] / display_title / f"{display_title}{release_tags}{ext}"

    if row["category"] == "Extra":
        return dest_root / row["library"] / display_title / "extras" / clean_filename(Path(row["source_path"]).name)

    if row["category"] == "Special" and not row.get("episode"):
        return dest_root / row["library"] / display_title / "Season 00" / clean_filename(Path(row["source_path"]).name)

    season = int(row["season"])
    episode = int(row["episode"])
    episode_title = f" - {clean_filename(row['episode_title'])}" if row.get("episode_title") else ""
    return (
        dest_root
        / row["library"]
        / display_title
        / f"Season {season:02d}"
        / f"{display_title} - S{season:02d}E{episode:02d}{episode_title}{release_tags}{ext}"
    )


def hardlink(src: Path, dst: Path, dry_run: bool) -> None:
    if dst.exists():
        print(f"SKIP exists (not overwritten): {dst}")
        return
    if dry_run:
        print(f"DRY LINK {src} -> {dst}")
        return
    dst.parent.mkdir(parents=True, exist_ok=True)
    os.link(src, dst)
    print(f"LINK {src} -> {dst}")


def link_matching_subtitles(src: Path, dst: Path, dry_run: bool) -> None:
    src_stem = src.stem
    for sub in src.parent.iterdir():
        if not sub.is_file() or sub.suffix.lower() not in SUB_EXTS:
            continue
        if not sub.name.lower().startswith(src_stem.lower()):
            continue
        suffix = sub.name[len(src_stem) :]
        hardlink(sub, dst.with_name(dst.stem + suffix), dry_run)


def read_plan(plan_path: Path) -> list[dict[str, str]]:
    with plan_path.open("r", newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_plan(plan_path: Path, rows: list[dict[str, str]]) -> None:
    plan_path.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "include",
        "category",
        "library",
        "title",
        "year",
        "season",
        "episode",
        "raw_episode",
        "episode_title",
        "release_tags",
        "source_path",
        "confidence",
        "pattern",
        "notes",
    ]
    with plan_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def print_plan_summary(rows: list[dict[str, str]]) -> None:
    print(f"rows: {len(rows)}")
    print("category:", dict(Counter(row["category"] for row in rows)))
    print("confidence:", dict(Counter(row["confidence"] for row in rows)))
    print("included:", dict(Counter(row["include"] for row in rows)))
    needs_review = [row for row in rows if row["include"] != "true" or "review" in row["notes"] or row["confidence"] == "low"]
    print(f"review_suggested: {len(needs_review)}")


def analyze_tree(tree_path: Path) -> None:
    text = tree_path.read_text(encoding="utf-8")
    names = []
    for line in text.splitlines():
        name = re.sub(r"^[│\s]*(?:├──|└──)\s*", "", line.replace("\u00a0", " "))
        if name:
            names.append(name)

    videos = [name for name in names if Path(name).suffix.lower() in VIDEO_EXTS]
    guessed = [guess_episode(name) for name in videos]
    print(f"tree_lines: {len(text.splitlines())}")
    print(f"tree_video_files: {len(videos)}")
    print("tree_video_exts:", dict(Counter(Path(name).suffix.lower() for name in videos)))
    print("tree_guess_confidence:", dict(Counter(confidence for _season, _episode, _raw, confidence, _pattern in guessed)))
    print("tree_guess_patterns:", dict(Counter(pattern or "none" for _season, _episode, _raw, _confidence, pattern in guessed)))
    print("tree_patterns:", {
        "SxxEyy": sum(bool(re.search(r"S\d{1,2}E\d{1,3}", name, re.I)) for name in videos),
        "[nn]": sum(bool(re.search(r"\[\d{1,3}\]", name)) for name in videos),
        "- nn": sum(bool(re.search(r"(?:^|\s-\s)\d{1,3}(?:\D|$)", name)) for name in videos),
        "title nn": sum(pattern == "title nn" for _season, _episode, _raw, _confidence, pattern in guessed),
        "extras": sum(bool(EXTRA_RE.search(name)) for name in videos),
        "specials": sum(bool(SPECIAL_RE.search(name)) for name in videos),
        "movies": sum(bool(MOVIE_RE.search(name)) for name in videos),
    })


def main() -> int:
    parser = argparse.ArgumentParser(description="Create a reviewable anime hardlink plan, then apply it.")
    parser.add_argument("--source", type=Path, help="Existing messy media/download root")
    parser.add_argument("--dest", type=Path, help="New normalized Jellyfin library root")
    parser.add_argument("--plan", default=Path("media-hardlink-plan.csv"), type=Path)
    parser.add_argument("--tree", type=Path, help="Analyze a UTF-8 Linux tree listing for planning only")
    parser.add_argument("--refresh-plan", action="store_true", help="Regenerate an existing plan")
    parser.add_argument("--include-extras", action="store_true", help="Include NCOP/NCED/PV/CM/Menu/etc in the plan")
    parser.add_argument("--include-specials", action="store_true", help="Include OVA/OAD/SP/Special rows as Season 00 placeholders")
    parser.add_argument("--append-release-tags", action="store_true", help="Append quality/codec/audio tags to destination filenames")
    parser.add_argument("--apply", action="store_true", help="Create hardlinks from the edited CSV plan")
    parser.add_argument("--dry-run", action="store_true", help="Print hardlink actions without creating links")
    args = parser.parse_args()

    if args.tree:
        analyze_tree(args.tree)

    if not args.source or not args.dest:
        if args.tree:
            return 0
        parser.error("--source and --dest are required unless only --tree is used")

    source = args.source.resolve()
    dest = args.dest.resolve()

    if not args.apply:
        if args.plan.exists() and not args.refresh_plan:
            print(f"Plan exists: {args.plan}")
            print("Use --refresh-plan to regenerate it, or --apply to create hardlinks from it.")
            return 0
        rows = make_plan(source, args.include_extras, args.include_specials)
        write_plan(args.plan, rows)
        print(f"Wrote plan: {args.plan}")
        print_plan_summary(rows)
        print("Edit include/title/year/season/episode/episode_title, then rerun with --apply --dry-run first.")
        return 0

    for row in read_plan(args.plan):
        if row.get("include", "").lower() not in {"true", "yes", "1"}:
            continue
        dst = destination_for(row, dest, args.append_release_tags)
        src = Path(row["source_path"])
        hardlink(src, dst, args.dry_run)
        link_matching_subtitles(src, dst, args.dry_run)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
