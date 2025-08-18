#!/usr/bin/env python3
"""
compare_by_content.py

Recursively compare two directories by file content (SHA-256), ignoring filenames.
CSV output has exactly two columns: A_file, B_file.
If a file has no content match on the other side, the opposite column is left blank.

Usage:
  python compare_by_content.py /path/to/dirA /path/to/dirB --csv out.csv
  python compare_by_content.py dirA dirB --csv out.csv --algo sha256

Notes:
- Matches are grouped by content hash; filenames/paths are ignored for matching.
- Duplicates (same content multiple times on a side) are expanded into multiple rows.
"""

import argparse
import hashlib
import os
import sys
import csv
from itertools import zip_longest

CHUNK_SIZE = 1024 * 1024  # 1 MiB

def hash_file(path: str, algo: str = "sha256") -> str:
    h = hashlib.new(algo)
    with open(path, "rb") as f:
        while True:
            chunk = f.read(CHUNK_SIZE)
            if not chunk:
                break
            h.update(chunk)
    return h.hexdigest()


def iter_files(root: str):
    for dirpath, _, filenames in os.walk(root):
        for name in filenames:
            full = os.path.join(dirpath, name)
            try:
                if os.path.islink(full) or not os.path.isfile(full):
                    continue
            except OSError:
                continue
            yield full


def build_hash_index(root: str, algo: str):
    """
    Returns: dict[hash] -> list[str] of absolute file paths
    """
    idx = {}
    for p in iter_files(root):
        try:
            h = hash_file(p, algo)
        except Exception as e:
            print(f"Warning: failed to hash {p}: {e}", file=sys.stderr)
            continue
        idx.setdefault(h, []).append(p)
    # Keep deterministic order per hash
    for k in idx:
        idx[k].sort()
    return idx


def write_two_column_csv(csv_path: str, labelA: str, labelB: str, idxA: dict, idxB: dict):
    """
    For each content hash, pair A_paths and B_paths row-by-row.
    If counts differ, blank cells are written for the shorter side.
    Also covers unmatched hashes that exist only on one side.
    """
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        # Header: two columns only
        w.writerow(["A_file", "B_file"])

        all_hashes = sorted(set(idxA.keys()) | set(idxB.keys()))
        for h in all_hashes:
            a_list = idxA.get(h, [])
            b_list = idxB.get(h, [])
            # Pair rows by content group
            for a_path, b_path in zip_longest(a_list, b_list, fillvalue=""):
                w.writerow([a_path, b_path])


def main():
    ap = argparse.ArgumentParser(description="Compare two directories by content and emit a two-column CSV.")
    ap.add_argument("dirA")
    ap.add_argument("dirB")
    ap.add_argument("--algo", default="sha256", help="Hash algorithm (default: sha256)")
    ap.add_argument("--csv", dest="csv_out", required=True, help="Path to write the two-column CSV report")
    args = ap.parse_args()

    dirA = os.path.abspath(args.dirA)
    dirB = os.path.abspath(args.dirB)

    if not os.path.isdir(dirA) or not os.path.isdir(dirB):
        print("Both arguments must be existing directories.", file=sys.stderr)
        sys.exit(2)

    print(f"Hashing A: {dirA}")
    idxA = build_hash_index(dirA, args.algo)
    print(f"Hashing B: {dirB}")
    idxB = build_hash_index(dirB, args.algo)

    write_two_column_csv(args.csv_out, dirA, dirB, idxA, idxB)
    print(f"Wrote CSV to: {args.csv_out}")
    print("Format: two columns [A_file,B_file]. Blank cell indicates no content match on that row.")


if __name__ == "__main__":
    main()
