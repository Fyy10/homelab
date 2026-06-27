# Anime Renamer

`anime_renamer` builds a reviewable CSV plan from a messy anime download
directory, then applies that plan by creating hard links in a Jellyfin-friendly
folder layout.

The script does not move or delete source files. It links selected video files
and matching external subtitle files into the destination library.

## Requirements

- Python 3.10 or newer.
- Source and destination paths must be on the same filesystem for hard links to
  work.
- The source files referenced in the plan must exist at the exact paths stored
  in `source_path`.

## Basic Workflow

1. Generate a plan:

   ```bash
   python3 scripts/anime_renamer/main.py \
     --source /srv/media/library/Animation \
     --dest /srv/media/library \
     --plan scripts/anime_renamer/plan.csv \
     --include-extras \
     --include-specials
   ```

2. Review and edit the CSV.

3. Run a dry run:

   ```bash
   python3 scripts/anime_renamer/main.py \
     --source /srv/media/library/Animation \
     --dest /srv/media/library \
     --plan scripts/anime_renamer/plan.csv \
     --apply \
     --dry-run
   ```

4. Apply the plan:

   ```bash
   python3 scripts/anime_renamer/main.py \
     --source /srv/media/library/Animation \
     --dest /srv/media/library \
     --plan scripts/anime_renamer/plan.csv \
     --apply
   ```

## Plan Generation

Without `--apply`, the script scans `--source`, creates rows for video files,
and writes them to `--plan`.

If the plan file already exists, the script will not overwrite it unless
`--refresh-plan` is provided:

```bash
python3 scripts/anime_renamer/main.py \
  --source /srv/media/library/Animation \
  --dest /srv/media/library \
  --plan scripts/anime_renamer/plan.csv \
  --refresh-plan
```

Use `--include-extras` to include NCOP, NCED, PV, CM, menu, and similar extra
videos in the generated plan.

Use `--include-specials` to include OVA, OAD, SP, Special, and Bonus rows that
the script can confidently map.

## CSV Fields

The apply step uses these fields:

- `include`: only rows with `true`, `yes`, or `1` are linked.
- `category`: controls destination layout. Common values are `Episode`,
  `Special`, `Movie`, and `Extra`.
- `library`: destination library folder under `--dest`, such as `Anime` or
  `Anime Movies`.
- `title`: series or movie title used in destination folders and filenames.
- `year`: optional year suffix, written as `Title (Year)`.
- `season`: season number for episode-style destinations.
- `episode`: episode number for episode-style destinations.
- `episode_title`: optional title appended to the destination filename.
- `release_tags`: only used when applying with `--append-release-tags`.
- `source_path`: exact source video path to link from.

These fields are for review and troubleshooting only during apply:

- `raw_episode`
- `confidence`
- `pattern`
- `notes`

## Destination Layout

Episode and numbered special rows are written as:

```text
DEST/LIBRARY/Title/Season 01/Title - S01E01.mkv
```

Special rows with `season` set to `0` are written under `Season 00`:

```text
DEST/LIBRARY/Title/Season 00/Title - S00E01.mkv
```

Movie rows are written as:

```text
DEST/LIBRARY/Title/Title.mkv
```

Extra rows are written as:

```text
DEST/LIBRARY/Title/extras/original-extra-filename.mkv
```

## Subtitle Handling

External subtitles are not listed as CSV rows. During apply, each included video
row is linked first, then the script scans the video's source directory for
matching subtitle files.

Supported subtitle extensions:

```text
.ass .srt .ssa .vtt .sub
```

Language suffixes such as `.tc.ass`, `.sc.ass`, `.chs.ass`, `.cht.ass`, and
`.jpn.ass` are supported because the final suffix is still `.ass`.

Subtitle matching is prefix-based. A subtitle is linked only when its filename
starts with the full video stem.

This works:

```text
Show [01].mkv
Show [01].tc.ass
```

This does not match automatically:

```text
[Group] Show - 01 [BD 1080p].mkv
Show 01.chs.ass
```

Before applying, check for subtitle files whose names do not share the video
stem. Rename them or adjust the script if those subtitles must be carried into
the destination library.

## Dry Run vs Apply

`--dry-run` uses the same plan fields and destination logic as a real apply,
but it only prints the hard-link actions:

```text
DRY LINK source -> destination
```

It does not create directories or links.

Without `--dry-run`, the script creates parent directories as needed and uses
`os.link()` to create hard links. If a destination path already exists, it is
skipped and not overwritten.

## Tree Analysis

You can inspect a UTF-8 `tree` output without generating or applying a plan:

```bash
python3 scripts/anime_renamer/main.py --tree dir.txt
```

This prints counts for detected video files, extensions, episode patterns,
extras, specials, and movies.

## Important Notes

- Review `include=false`, `confidence=low`, `needs_manual_episode`,
  `special_needs_mapping`, `absolute_episode_range_needs_review`, and
  `destination_conflict` rows before applying.
- Put Jellyfin specials in `season=0` when you want them under `Season 00`.
- `--source` is required by the CLI, but during `--apply` the script links from
  each row's `source_path`. Changing `--source` does not rewrite existing plan
  paths.
- Hard links do not duplicate file data, but deleting the final remaining link
  to a file deletes the data. Keep the original download tree until the new
  library has been verified.
- The script sanitizes destination filenames by replacing characters that are
  invalid on common filesystems.
