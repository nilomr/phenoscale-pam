#!/usr/bin/env python3
"""
Create combined heatmap and completeness visualization of daily recording data.
Publication-ready figure with strict alignment and consistent aesthetics.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap, BoundaryNorm
from datetime import datetime, timedelta
import argparse
import matplotlib.dates as mdates


def compute_month_info(dates):
    """Return month ticks, labels, and boundaries for vertical separators."""
    ticks, labels, boundaries = [0], [dates[0].strftime("%b")], []
    current_month = dates[0].month

    for i, d in enumerate(dates[1:], 1):
        if d.month != current_month:
            ticks.append(i)
            labels.append(d.strftime("%b"))
            boundaries.append(i - 0.5)
            current_month = d.month

    return ticks, labels, boundaries


def smart_count_bins(data_matrix, max_bins=8):
    """Choose discrete bins for count data based on actual values."""
    vals = np.unique(data_matrix)
    if vals.size == 0 or (nonzero := vals[vals > 0]).size == 0:
        return np.array([0]), np.array([-0.5, 0.5])

    if nonzero.size <= max_bins:
        cats = np.concatenate(([0], nonzero))
    else:
        qs = np.linspace(0, 100, max_bins)
        reps = np.unique(np.percentile(nonzero, qs).round().astype(int))
        cats = np.unique(np.concatenate(([0], reps)))

    categories = np.sort(cats)
    bounds = [categories[0] - 0.5]
    for i in range(1, len(categories)):
        bounds.append((categories[i - 1] + categories[i]) / 2)
    bounds.append(categories[-1] + 0.5)

    return categories, np.array(bounds, dtype=float)


def add_month_separators(ax, boundaries, color="white", lw=2.5, alpha=0.9):
    """Add vertical white bars at month boundaries."""
    for boundary in boundaries:
        ax.axvline(x=boundary, color=color, linewidth=lw, alpha=alpha, zorder=10)


def style_axis(ax, spine_visible=False):
    """Apply consistent minimalistic styling."""
    for spine in ax.spines.values():
        spine.set_visible(spine_visible)
    ax.grid(False)


def create_combined_figure(daily_counts_csv, output_file="deployment_combined.png"):
    """Create combined publication-ready figure with heatmap and completeness plot."""

    # Load and prepare data
    df = pd.read_csv(daily_counts_csv)
    date_cols = [col for col in df.columns if col != "Site"]
    sites = df["Site"].values
    data_matrix = df[date_cols].values
    dates = [datetime.strptime(d, "%Y-%m-%d") for d in date_cols]

    # Sort sites by missing data
    row_means = data_matrix.mean(axis=1)
    overall_max = data_matrix.max() if data_matrix.size > 0 else 1
    overall_max = max(overall_max, 1)
    missing_score = 1.0 - (row_means / overall_max)
    sort_idx = np.argsort(missing_score)[::-1]
    sites, data_matrix = sites[sort_idx], data_matrix[sort_idx]

    # Month information
    month_ticks, month_labels, month_boundaries = compute_month_info(dates)

    # Create figure with two subplots using sharex=True for strict alignment
    # height_ratios: 2.5 vs 1.25 is exactly 2:1 ratio
    fig, (ax1, ax2) = plt.subplots(
        2,
        1,
        figsize=(26, 20),
        sharex=True,
        gridspec_kw={"height_ratios": [2.5, 1.25], "hspace": 0.05},
    )

    # ========== Panel A: Heatmap ==========

    # Colormap and bins
    categories, count_bounds = smart_count_bins(data_matrix, max_bins=7)
    colors = [
        "#d73027",
        "#fc8d59",
        "#fee08b",
        "#d9ef8b",
        "#91cf60",
        "#1a9850",
        "#006837",
    ]
    cmap = LinearSegmentedColormap.from_list("counts", colors, N=256)
    norm = BoundaryNorm(count_bounds, cmap.N)

    # Use imshow with datetime extent for alignment, padded for bar width
    extent = [
        mdates.date2num(dates[0]) - 0.5,
        mdates.date2num(dates[-1]) + 0.5,
        len(sites) - 0.5,
        -0.5,
    ]
    im = ax1.imshow(
        data_matrix,
        extent=extent,
        aspect="auto",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
    )

    # Month separators at date positions
    for tick in month_ticks[1:]:
        ax1.axvline(
            mdates.date2num(dates[tick]),
            color="white",
            linewidth=2.5,
            alpha=0.9,
            zorder=10,
        )

    # Axes styling
    ax1.set_yticks(np.arange(len(sites)))
    ax1.set_yticklabels([])
    ax1.tick_params(axis="y", length=0)
    ax1.set_ylabel("Recording site", fontsize=24, weight="bold", labelpad=15)
    ax1.text(
        -0.015,
        1.02,
        "A",
        transform=ax1.transAxes,
        fontsize=32,
        weight="bold",
        va="bottom",
    )

    # Colorbar: Positioned higher to avoid overlap
    axins = ax1.inset_axes([0.75, 1.05, 0.25, 0.03])
    cbar = plt.colorbar(
        im, cax=axins, orientation="horizontal", boundaries=count_bounds
    )

    tick_centers = [
        0.5 * (count_bounds[i] + count_bounds[i + 1]) for i in range(len(categories))
    ]
    cbar.set_ticks(tick_centers)
    cbar.set_ticklabels([str(int(v)) for v in categories])
    cbar.set_label("Recordings/day", fontsize=20, weight="bold", labelpad=10)
    cbar.ax.tick_params(labelsize=17)
    cbar.ax.xaxis.set_label_position("top")
    cbar.ax.xaxis.set_ticks_position("bottom")

    style_axis(ax1)

    # ========== Panel B: Completeness ==========

    # Calculate missing percentage
    mode_per_day = np.array(
        [
            np.bincount(data_matrix[:, i].astype(int)).argmax()
            for i in range(data_matrix.shape[1])
        ]
    )
    reference_per_day = mode_per_day * len(sites)
    effective_matrix = np.minimum(data_matrix, mode_per_day[None, :])
    total_effective = effective_matrix.sum(axis=0)
    pct_missing = ((reference_per_day - total_effective) / reference_per_day) * 100
    pct_non_missing = 100 - pct_missing

    # Stacked bars
    ax2.bar(
        dates,
        pct_non_missing,
        width=1,
        color="#1a9850",
        edgecolor="none",
        label="Complete",
    )
    ax2.bar(
        dates,
        pct_missing,
        width=1,
        bottom=pct_non_missing,
        color="#d73027",
        edgecolor="none",
        label="Missing",
    )

    # Month separators
    for tick in month_ticks[1:]:
        ax2.axvline(
            dates[tick],
            color="white",
            linestyle="-",
            linewidth=2.5,
            alpha=0.9,
            zorder=10,
        )

    # Axes
    # Set xlim to match padded extent
    ax2.set_xlim(dates[0] - timedelta(days=0.5), dates[-1] + timedelta(days=0.5))
    ax2.set_ylim(0, 100)
    ax2.set_xticks([dates[i] for i in month_ticks])
    ax2.set_xticklabels(month_labels, fontsize=22, weight="bold")
    ax2.set_xlabel("Month (2025)", fontsize=24, weight="bold", labelpad=15)
    ax2.set_ylabel("Completeness (%)", fontsize=24, weight="bold", labelpad=15)
    ax2.text(
        -0.015,
        1.02,
        "B",
        transform=ax2.transAxes,
        fontsize=32,
        weight="bold",
        va="bottom",
    )
    ax2.legend(loc="lower right", fontsize=18, frameon=False)
    ax2.grid(axis="y", alpha=0.25, linestyle="-", linewidth=0.5)
    ax2.tick_params(axis="both", labelsize=18)

    style_axis(ax2)

    # Adjust layout to ensure everything fits
    plt.tight_layout()

    # Increase top margin for colorbar
    plt.subplots_adjust(top=0.95)

    plt.savefig(output_file, dpi=300, bbox_inches="tight", facecolor="white")
    print(f"✓ Saved combined figure: {output_file}")
    print(f"  Panel A: Daily recording counts ({len(sites)} sites × {len(dates)} days)")
    print(f"  Panel B: Daily recording completeness")

    return fig


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Create combined deployment visualization"
    )
    parser.add_argument("daily_counts_csv", help="Path to daily counts CSV")
    parser.add_argument(
        "--output", default="deployment_combined.png", help="Output filename"
    )
    args = parser.parse_args()

    create_combined_figure(args.daily_counts_csv, args.output)
