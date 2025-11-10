# -*- coding: utf-8 -*-
"""
High-quality Gantt chart plotting utilities for scheduling timelines.

Design goals:
- Consistent, qualitative colors across processes (tab10 cycle).
- Crisp rendering for reports (dpi=300).
- Legends outside the axes to maximize data-ink ratio.
- Works with either single-slice-per-process or multi-slice (preemptive) timelines.

We use Axes.barh for simplicity and legibility. For very large numbers of slices,
you can switch to Axes.broken_barh which is optimized for many rectangles.

References / inspiration:
- Matplotlib qualitative colormaps (tab10) for categories. 
- Legend placement outside axes & tight bounding box on save.
- Constrained layout / tight layout notes from Matplotlib docs.

"""

from typing import Dict, Iterable, List, Tuple
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def _collect_pids(results: List[Dict]) -> List[int]:
    """Return a stable, sorted list of PIDs present in a results timeline."""
    pids = sorted({int(r["pid"]) for r in results})
    return pids


def _pid_to_label(pid: int) -> str:
    """Format a process label for display."""
    return f"P{pid}"


def _build_color_map(pids: Iterable[int]) -> Dict[int, Tuple[float, float, float, float]]:
    """
    Map each PID to a color from a qualitative palette (tab10).
    Cycles if there are more than 10 processes.
    """
    pids = list(pids)
    cmap = plt.cm.get_cmap("tab10")  # qualitative palette suited for categories
    colors = [cmap(i % 10) for i in range(len(pids))]
    return {pid: colors[i] for i, pid in enumerate(pids)}


def _normalize_slices(results: List[Dict]) -> List[Dict]:
    """
    Ensure each element behaves like a 'slice':
        {"pid": int, "start": float/int, "finish": float/int}
    Extra keys (waiting, turnaround, etc.) are ignored by the plotter.
    """
    slices = []
    for r in results:
        # Accept start/finish keys that already exist; skip if missing
        if "start" in r and "finish" in r and "pid" in r:
            slices.append({"pid": int(r["pid"]), "start": r["start"], "finish": r["finish"]})
    # Sort by start time to draw in temporal order
    slices.sort(key=lambda x: (x["start"], x["finish"], x["pid"]))
    return slices


def plot_gantt(
    results: List[Dict],
    title: str = "Gantt Chart",
    filename: str = "gantt_chart.png",
    processes: List[Dict] = None,
    show_labels: bool = True,
    bar_height: float = 0.5,
):
    """
    Plot a clean, publication-ready Gantt chart for a single algorithm timeline.

    Parameters
    ----------
    results : list of dict
        Timeline entries (slices or per-process blocks) with keys:
        - pid, start, finish (required)
        - waiting, turnaround (ignored here)
    title : str
        Plot title.
    filename : str
        Where to save the PNG (dpi=300).
    processes : list of dict, optional
        Original process list; helps order legend labels consistently (by PID).
    show_labels : bool
        Whether to draw "start–finish" labels centered on each bar.
    bar_height : float
        Height of each horizontal bar.
    """
    slices = _normalize_slices(results)
    if not slices:
        print("plot_gantt: no slices to plot; skipped figure.")
        return

    # Figure / Axes with constrained layout to help manage the external legend
    fig, ax = plt.subplots(figsize=(11, 5), layout="constrained")

    # Collect processes and colors
    unique_pids = _collect_pids(slices)
    pid_order = unique_pids
    if processes:
        # Prefer legend ordering by original 'processes' list if available
        pid_order = sorted({int(p["pid"]) for p in processes if "pid" in p})
    colors = _build_color_map(pid_order)

    # Build Y positions: one lane per PID (sorted)
    # We use categorical y labels (e.g., "P1", "P2"), letting barh handle positioning.
    for sl in slices:
        pid = sl["pid"]
        left = sl["start"]
        width = sl["finish"] - sl["start"]
        ax.barh(
            _pid_to_label(pid),
            width,
            left=left,
            height=bar_height,
            color=colors.get(pid, (0.3, 0.3, 0.3, 1.0)),
            edgecolor="black",
            linewidth=0.8,
        )
        if show_labels and width > 0:
            ax.text(
                left + width / 2.0,
                _pid_to_label(pid),
                f"{sl['start']}–{sl['finish']}",
                ha="center",
                va="center",
                color="white",
                fontsize=9,
                fontweight="bold",
            )

    # Axes cosmetics
    ax.set_xlabel("Time")
    ax.set_ylabel("Process")
    ax.set_title(title, fontsize=14, weight="bold")
    ax.grid(True, axis="x", linestyle="--", alpha=0.6)

    # Legend outside the plot (right side)
    handles = [mpatches.Patch(color=colors[pid], label=_pid_to_label(pid)) for pid in pid_order if pid in colors]
    if handles:
        ax.legend(
            handles=handles,
            title="Processes",
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
            borderaxespad=0.0,
        )

    # Save crisp PNG (300 DPI) with tight bounding box so legend is not clipped
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_gantt_grid(
    algorithms_results: Dict[str, List[Dict]],
    filename: str = "gantt_comparison_panel.png",
    show_labels: bool = False,
    bar_height: float = 0.45,
):
    """
    Draw multiple Gantt charts (one per algorithm) stacked vertically, sharing a
    consistent color mapping for processes to ease visual comparison.

    Parameters
    ----------
    algorithms_results : dict
        Mapping: algorithm name -> results list (timeline slices)
    filename : str
        Output PNG path.
    show_labels : bool
        Whether to draw "start–finish" labels on each bar.
    bar_height : float
        Height of bars in each panel.
    """
    if not algorithms_results:
        print("plot_gantt_grid: no algorithms to compare; skipped figure.")
        return

    # Build a *global* color map from all PIDs across all timelines
    all_pids = sorted({
        int(r["pid"])
        for results in algorithms_results.values()
        for r in results
        if "pid" in r
    })
    colors = _build_color_map(all_pids)

    n = len(algorithms_results)
    fig, axes = plt.subplots(
        n, 1,
        figsize=(13, max(3.0, 2.6 * n)),
        sharex=False,
        layout="constrained"
    )
    if n == 1:
        axes = [axes]

    for ax, (alg_name, results) in zip(axes, algorithms_results.items()):
        slices = _normalize_slices(results)
        if not slices:
            ax.set_title(f"{alg_name} (no data)")
            ax.axis("off")
            continue

        # Keep Y lanes consistent (sorted PIDs found in this algorithm)
        pids_here = _collect_pids(slices)

        for sl in slices:
            pid = sl["pid"]
            left = sl["start"]
            width = sl["finish"] - sl["start"]
            ax.barh(
                _pid_to_label(pid),
                width,
                left=left,
                height=bar_height,
                color=colors.get(pid, (0.3, 0.3, 0.3, 1.0)),
                edgecolor="black",
                linewidth=0.8,
            )
            if show_labels and width > 0:
                ax.text(
                    left + width / 2.0,
                    _pid_to_label(pid),
                    f"{sl['start']}–{sl['finish']}",
                    ha="center",
                    va="center",
                    color="white",
                    fontsize=8,
                    fontweight="bold",
                )

        ax.set_title(alg_name, fontsize=12, weight="bold")
        ax.set_xlabel("Time")
        ax.set_ylabel("Process")
        ax.grid(True, axis="x", linestyle="--", alpha=0.6)

    # Global legend for all processes (top-right outside last axes)
    handles = [mpatches.Patch(color=colors[pid], label=_pid_to_label(pid)) for pid in all_pids]
    # Attach legend to the last axes (it will be positioned outside with bbox)
    axes[-1].legend(
        handles=handles,
        title="Processes",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        borderaxespad=0.0,
        ncol=1
    )

    fig.suptitle("Gantt Chart Comparison Panel", fontsize=15, weight="bold")
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
