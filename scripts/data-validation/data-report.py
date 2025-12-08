#!/usr/bin/env python3
"""
AudioMoth Wytham Woods Deployment Completeness Analyzer
Handles scheduled recording periods and continuous site deployments
Generates completeness statistics and daily recording heatmaps
"""

import os
from pathlib import Path
from datetime import datetime, timedelta, date
from collections import defaultdict
import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import argparse
import warnings

warnings.filterwarnings("ignore")


def parse_audiomoth_filename(filename: str) -> Optional[datetime]:
    """Parse AudioMoth filename format: YYYYMMDD_HHMMSS.WAV"""
    try:
        base = filename.replace(".WAV", "").replace(".wav", "")
        dt = datetime.strptime(base, "%Y%m%d_%H%M%S")
        # Filter out invalid timestamps (Unix epoch errors)
        if dt.year < 2024:
            return None
        return dt
    except:
        return None


def merge_continuous_deployments(site_dirs: List[Path]) -> Dict[str, List[Path]]:
    """
    Merge site directories that represent continuous deployments
    e.g., L5 and L5-2 -> L5
    """
    merged_sites = defaultdict(list)

    for site_dir in site_dirs:
        site_name = site_dir.name
        # Remove '-2', '-3', etc. suffixes to get base site name
        base_name = site_name.split("-")[0] if "-" in site_name else site_name
        merged_sites[base_name].append(site_dir)

    return merged_sites


def analyze_merged_site(
    site_paths: List[Path], recording_interval_sec: int = 60
) -> Dict:
    """
    Analyze data completeness for a site (potentially multiple deployment folders)
    """
    base_site_name = (
        site_paths[0].name.split("-")[0]
        if "-" in site_paths[0].name
        else site_paths[0].name
    )
    all_timestamps = []
    total_files = 0
    invalid_files = 0

    # Collect all timestamps from all deployment folders for this site
    for site_path in sorted(site_paths):
        wav_files = list(site_path.glob("*.WAV")) + list(site_path.glob("*.wav"))
        total_files += len(wav_files)

        for f in wav_files:
            ts = parse_audiomoth_filename(f.name)
            if ts:
                all_timestamps.append(ts)
            else:
                invalid_files += 1

    if not all_timestamps:
        return {
            "site": base_site_name,
            "deployment_folders": [p.name for p in site_paths],
            "n_folders": len(site_paths),
            "n_files": total_files,
            "invalid_files": invalid_files,
            "first_recording": None,
            "last_recording": None,
            "duration_days": 0,
            "actual_recordings": 0,
            "timestamps": [],
            "gaps": [],
            "daily_counts": {},
        }

    all_timestamps.sort()
    first_rec = all_timestamps[0]
    last_rec = all_timestamps[-1]
    duration_days = (last_rec - first_rec).total_seconds() / 86400

    # Calculate daily counts
    daily_counts = defaultdict(int)
    for ts in all_timestamps:
        daily_counts[ts.date()] += 1

    # Find gaps (>10 minutes to account for sleep cycles)
    gaps = find_gaps(all_timestamps, max_gap_minutes=10)

    # Calculate completeness: compare to median daily count for this site
    median_daily = np.median(list(daily_counts.values())) if daily_counts else 0
    expected_total = (
        int(median_daily * duration_days) if median_daily > 0 else len(all_timestamps)
    )
    completeness_pct = (
        (len(all_timestamps) / expected_total * 100) if expected_total > 0 else 100
    )

    return {
        "site": base_site_name,
        "deployment_folders": [p.name for p in site_paths],
        "n_folders": len(site_paths),
        "n_files": total_files,
        "invalid_files": invalid_files,
        "first_recording": first_rec,
        "last_recording": last_rec,
        "duration_days": duration_days,
        "actual_recordings": len(all_timestamps),
        "expected_recordings": expected_total,
        "completeness_pct": completeness_pct,
        "median_daily_recordings": median_daily,
        "timestamps": all_timestamps,
        "gaps": gaps,
        "daily_counts": daily_counts,
    }


def find_gaps(
    timestamps: List[datetime], max_gap_minutes: int = 10
) -> List[Tuple[datetime, datetime, float]]:
    """
    Find gaps larger than max_gap_minutes between consecutive recordings
    Returns list of (start_time, end_time, gap_duration_hours)
    """
    gaps = []

    for i in range(len(timestamps) - 1):
        gap_seconds = (timestamps[i + 1] - timestamps[i]).total_seconds()
        gap_minutes = gap_seconds / 60

        if gap_minutes > max_gap_minutes:
            gap_hours = gap_seconds / 3600
            gaps.append((timestamps[i], timestamps[i + 1], gap_hours))

    return gaps


def create_daily_heatmap_data(site_results: List[Dict]) -> pd.DataFrame:
    """
    Create a matrix of daily recording counts for heatmap visualization
    Rows = sites, Columns = dates
    """
    # Get all unique dates across all sites
    all_dates = set()
    for result in site_results:
        all_dates.update(result["daily_counts"].keys())

    if not all_dates:
        return pd.DataFrame()

    all_dates = sorted(all_dates)

    # Create matrix
    heatmap_data = []
    for result in site_results:
        row = {"Site": result["site"]}
        for d in all_dates:
            row[d.strftime("%Y-%m-%d")] = result["daily_counts"].get(d, 0)
        heatmap_data.append(row)

    df = pd.DataFrame(heatmap_data)
    return df


def analyze_all_sites(
    base_dir: str,
    recording_interval_sec: int = 60,
    sleep_duration_sec: int = 300,
    output_prefix: str = "deployment",
):
    """
    Analyze completeness for all sites, merging continuous deployments
    """
    base_path = Path(base_dir)

    if not base_path.exists():
        print(f"ERROR: Directory not found: {base_dir}")
        return None, None, None, None

    # Get all subdirectories
    site_dirs = [d for d in base_path.iterdir() if d.is_dir()]

    # Merge continuous deployments (e.g., L5 + L5-2)
    merged_sites = merge_continuous_deployments(site_dirs)

    print(f"\n{'=' * 80}")
    print(f"AudioMoth Wytham Woods Deployment Analysis")
    print(f"{'=' * 80}")
    print(f"Base directory: {base_dir}")
    print(f"Physical site folders: {len(site_dirs)}")
    print(f"Unique recording sites: {len(merged_sites)}")
    print(f"Recording schedule: Scheduled sunrise/sunset periods (not 24/7)")
    print(
        f"Recording cycle: {recording_interval_sec}s record, {sleep_duration_sec}s sleep\n"
    )

    # Analyze each merged site
    site_results = []
    all_timestamps = []
    total_invalid = 0

    for base_site_name, site_paths in sorted(merged_sites.items()):
        result = analyze_merged_site(site_paths, recording_interval_sec)
        site_results.append(result)
        all_timestamps.extend(result["timestamps"])
        total_invalid += result["invalid_files"]

        folder_str = ", ".join(result["deployment_folders"])
        completeness_str = (
            f"{result['completeness_pct']:.1f}%"
            if result["completeness_pct"] > 0
            else "N/A"
        )
        print(
            f"✓ {result['site']:6s} | {folder_str:20s} | "
            f"{result['n_files']:6d} files | {completeness_str:6s} complete | "
            f"{len(result['gaps']):4d} gaps"
        )

    # Create site summary DataFrame
    summary_df = pd.DataFrame(
        [
            {
                "Site": r["site"],
                "Deployment_Folders": ", ".join(r["deployment_folders"]),
                "Total_Files": r["n_files"],
                "Invalid_Files": r["invalid_files"],
                "Valid_Recordings": r["actual_recordings"],
                "Expected_Recordings": r["expected_recordings"],
                "Completeness_pct": round(r["completeness_pct"], 2),
                "Median_Daily_Recordings": int(r["median_daily_recordings"]),
                "First_Recording": r["first_recording"],
                "Last_Recording": r["last_recording"],
                "Duration_days": round(r["duration_days"], 2),
                "N_Gaps_10min": len(r["gaps"]),
            }
            for r in site_results
        ]
    )

    # Create gaps DataFrame
    gaps_data = []
    for r in site_results:
        for gap_start, gap_end, gap_hours in r["gaps"]:
            gaps_data.append(
                {
                    "Site": r["site"],
                    "Gap_Start": gap_start,
                    "Gap_End": gap_end,
                    "Gap_Duration_hours": round(gap_hours, 2),
                }
            )

    gaps_df = pd.DataFrame(gaps_data) if gaps_data else pd.DataFrame()

    # Create daily heatmap data
    print(f"\nGenerating daily recording heatmap...")
    heatmap_df = create_daily_heatmap_data(site_results)

    # Global statistics
    if all_timestamps:
        all_timestamps.sort()
        global_first = all_timestamps[0]
        global_last = all_timestamps[-1]
        global_duration = (global_last - global_first).total_seconds() / 86400
        total_recordings = len(all_timestamps)

        # Calculate global completeness
        global_median_daily = np.median(
            [
                r["median_daily_recordings"]
                for r in site_results
                if r["median_daily_recordings"] > 0
            ]
        )
        global_expected = int(global_median_daily * global_duration * len(merged_sites))
        global_completeness = (
            (total_recordings / global_expected * 100) if global_expected > 0 else 0
        )

        print(f"\n{'=' * 80}")
        print(f"GLOBAL SUMMARY")
        print(f"{'=' * 80}")
        print(f"Unique recording sites:   {len(merged_sites)}")
        print(f"Site deployment folders:  {len(site_dirs)}")
        print(f"First recording:          {global_first}")
        print(f"Last recording:           {global_last}")
        print(
            f"Deployment duration:      {global_duration:.1f} days ({global_duration / 30:.1f} months)"
        )
        print(f"Valid recordings:         {total_recordings:,}")
        print(f"Expected recordings:      {global_expected:,}")
        print(f"Global completeness:      {global_completeness:.1f}%")
        print(f"Invalid timestamps:       {total_invalid:,}")
        print(f"Total gaps (>10 min):     {len(gaps_data):,}")
        print(f"{'=' * 80}\n")

    # Save outputs
    summary_df.to_csv(f"{output_prefix}_site_summary.csv", index=False)
    print(f"✓ Saved: {output_prefix}_site_summary.csv")

    if not gaps_df.empty:
        gaps_df.to_csv(f"{output_prefix}_gaps.csv", index=False)
        print(f"✓ Saved: {output_prefix}_gaps.csv")

    if not heatmap_df.empty:
        heatmap_df.to_csv(f"{output_prefix}_daily_counts.csv", index=False)
        print(f"✓ Saved: {output_prefix}_daily_counts.csv (use for heatmap)")

    # Save global stats
    if all_timestamps:
        global_stats = {
            "Unique_Sites": len(merged_sites),
            "Deployment_Folders": len(site_dirs),
            "First_Recording": global_first,
            "Last_Recording": global_last,
            "Duration_days": round(global_duration, 2),
            "Valid_Recordings": total_recordings,
            "Expected_Recordings": global_expected,
            "Global_Completeness_pct": round(global_completeness, 2),
            "Invalid_Timestamps": total_invalid,
            "Total_Gaps_10min": len(gaps_data),
        }
        global_df = pd.DataFrame([global_stats])
        global_df.to_csv(f"{output_prefix}_global_summary.csv", index=False)
        print(f"✓ Saved: {output_prefix}_global_summary.csv\n")

    return site_results, summary_df, gaps_df, heatmap_df


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Analyze Wytham Woods AudioMoth deployment completeness",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python analyze_deployment_completeness.py /mnt/bio-lv-colefs01/2025-wytham-acoustics
  python analyze_deployment_completeness.py /path/to/data --output wytham2025
        """,
    )
    parser.add_argument(
        "base_dir", type=str, help="Base directory containing site folders"
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Recording duration in seconds (default: 60)",
    )
    parser.add_argument(
        "--sleep",
        type=int,
        default=300,
        help="Sleep duration in seconds (default: 300)",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="deployment",
        help="Output file prefix (default: deployment)",
    )

    args = parser.parse_args()

    analyze_all_sites(args.base_dir, args.interval, args.sleep, args.output)
