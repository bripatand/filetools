#!/usr/bin/env python3
"""
Split a video into consecutive segments based on a CSV of (filename,timestamp).

CSV format (with or without header):
filename,timestamp
intro.mp4,00:00:00
chapter1.mp4,00:02:13.500
chapter2.mp4,00:10:00
...

Behavior:
- Copies all streams from the source (no re-encode): -c copy
- Exports segments [start_i -> start_{i+1}) and ALWAYS the final [start_last -> end-of-video]
- Overwrites existing files
- Includes subtitles/audio tracks (uses -map 0)

Usage:
  python split_by_csv.py segments.csv source.mp4 -o out_folder

Requirements:
  - ffmpeg (and optionally ffprobe) available on PATH.
"""

import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from typing import List, Tuple, Optional


def die(msg: str, code: int = 1):
    print(f"Error: {msg}", file=sys.stderr)
    sys.exit(code)


def which_ffmpeg() -> Optional[str]:
    return shutil.which("ffmpeg")


def ffprobe_duration(input_video: str) -> Optional[float]:
    """Return duration in seconds via ffprobe, or None if unavailable."""
    ffprobe = shutil.which("ffprobe")
    if not ffprobe:
        return None
    try:
        out = subprocess.check_output(
            [
                ffprobe,
                "-v", "error",
                "-show_entries", "format=duration",
                "-of", "default=noprint_wrappers=1:nokey=1",
                input_video,
            ],
            stderr=subprocess.STDOUT,
        )
        return float(out.decode().strip())
    except Exception:
        return None


def parse_timestamp(ts: str) -> float:
    """
    Accepts:
      - "HH:MM:SS" or "HH:MM:SS.mmm"
      - "MM:SS" or "MM:SS.mmm"
      - "SS" or "SS.mmm"
    Returns seconds (float).
    """
    ts = ts.strip()
    if re.fullmatch(r"\d+(\.\d+)?", ts):  # plain seconds
        return float(ts)

    parts = [p.strip() for p in ts.split(":")]
    if not all(parts):
        raise ValueError(f"Bad timestamp: '{ts}'")

    if len(parts) == 1:
        return float(parts[0])
    if len(parts) == 2:
        m = int(parts[0]); s = float(parts[1])
        return m * 60 + s
    if len(parts) == 3:
        h = int(parts[0]); m = int(parts[1]); s = float(parts[2])
        return h * 3600 + m * 60 + s
    raise ValueError(f"Bad timestamp (too many colons): '{ts}'")


def read_csv_rows(path: str) -> List[Tuple[str, str]]:
    """Return raw (filename, timestamp_str) rows; skip blank/malformed lines; auto-skip header."""
    rows: List[Tuple[str, str]] = []
    with open(path, newline='', encoding="utf-8-sig") as f:
        reader = csv.reader(f)
        for r in reader:
            if not r or len(r) < 2:
                continue
            fn, ts = r[0].strip(), r[1].strip()
            if not fn or not ts:
                continue
            rows.append((fn, ts))

    if not rows:
        die("CSV appears empty or has no valid rows.")

    # Drop header if first timestamp fails to parse
    try:
        parse_timestamp(rows[0][1])
    except Exception:
        if len(rows) == 1:
            die("CSV only contains a header and no data rows.")
        rows = rows[1:]

    return rows


def normalize_rows(raw: List[Tuple[str, str]]) -> List[Tuple[str, float]]:
    """Parse timestamps, sanitize filenames, ensure increasing order, and sort by time."""
    parsed: List[Tuple[str, float]] = []
    for fn, ts in raw:
        t = parse_timestamp(ts)
        fn = fn.strip()
        if not fn:
            die("Encountered empty output filename.")
        parsed.append((fn, t))

    parsed.sort(key=lambda x: x[1])

    result: List[Tuple[str, float]] = []
    last = -1.0
    for fn, t in parsed:
        if t <= last:
            continue
        result.append((fn, t))
        last = t

    if not result:
        die("No valid, increasing timestamps found after cleaning.")
    return result


def run_ffmpeg_copy(input_video: str, out_path: str, start: float, end: Optional[float]):
    """
    Copy all streams without re-encoding.
    Use -ss BEFORE -i and -t = (end - start) for consistent stream-copy cuts.
    """
    cmd = ["ffmpeg", "-hide_banner", "-loglevel", "warning"]

    # Fast seek
    cmd += ["-ss", f"{start:.6f}", "-i", input_video]

    # Duration if we have an end
    if end is not None:
        duration = max(0.0, end - start)
        cmd += ["-t", f"{duration:.6f}"]

    # Map all streams, copy, and optimize MP4 header
    cmd += ["-map", "0", "-c", "copy", "-movflags", "+faststart", "-y", out_path]

    print("Running:", " ".join(cmd))
    subprocess.check_call(cmd)


def main():
    ap = argparse.ArgumentParser(
        description="Split a video into segments defined by a CSV (filename,timestamp). "
                    "Copies all streams without re-encoding and always includes the last segment."
    )
    ap.add_argument("input_video", help="Path to the source video to split.")
    ap.add_argument("csv_path", help="Path to CSV with 'filename,timestamp'.")
    ap.add_argument("-o", "--out-dir", default="out", help="Output folder (default: ./out)")
    args = ap.parse_args()

    if not os.path.isfile(args.csv_path):
        die(f"CSV not found: {args.csv_path}")
    if not os.path.isfile(args.input_video):
        die(f"Input video not found: {args.input_video}")
    if not which_ffmpeg():
        die("ffmpeg not found on PATH. Please install ffmpeg and try again.")

    raw = read_csv_rows(args.csv_path)
    rows = normalize_rows(raw)

    os.makedirs(args.out_dir, exist_ok=True)

    names = [fn for fn, _ in rows]
    starts = [t for _, t in rows]

    total = ffprobe_duration(args.input_video)

    # Export consecutive pairs [start_i, start_{i+1})
    for i in range(len(rows) - 1):
        start = starts[i]
        end = starts[i + 1]
        if end <= start:
            continue

        out_name = names[i]
        base, ext = os.path.splitext(out_name)
        if ext == "":
            out_name = base + ".mp4"

        out_path = os.path.join(args.out_dir, out_name)
        run_ffmpeg_copy(args.input_video, out_path, start, end)

    # Always include the last chunk [start_last, end-of-video]
    last_start = starts[-1]
    if total is not None and last_start >= total:
        print(f"Skipping last segment: start {last_start:.3f}s >= video duration {total:.3f}s.")
        print("Done.")
        return

    last_name = names[-1]
    base, ext = os.path.splitext(last_name)
    if ext == "":
        last_name = base + ".mp4"
    last_out = os.path.join(args.out_dir, last_name)

    run_ffmpeg_copy(args.input_video, last_out, last_start, None)
    print("Done.")


if __name__ == "__main__":
    main()
