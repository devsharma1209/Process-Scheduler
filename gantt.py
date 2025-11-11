# -*- coding: utf-8 -*-
"""
High-quality Gantt chart plotting utilities for scheduling timelines.

Design goals:
- Consistent, qualitative colors across processes (tab10 cycle).
- Crisp rendering for reports (dpi=300).
- Legends outside the axes to maximize data-ink ratio.
- Works with either single-slice-per-process or multi-slice (preemptive) timelines.
"""

from typing import Dict, Iterable, List, Tuple
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches


def _collect_pids(results: List[Dict]) -> List[int]:
    pids = sorted({int(r["pid"]) for r in results})
    return pids


def _pid_to_label(pid: int) -> str:
    return f"P{pid}"


def _build_color_map(pids: Iterable[int]) -> Dict[int, Tuple[float, float, float, float]]:
    pids = list(pids)
    cmap = plt.cm.get_cmap("tab10")
    colors = [cmap(i % 10) for i in range(len(pids))]
    return {pid: colors[i] for i, pid in enumerate(pids)}


def _normalize_slices(results: List[Dict]) -> List[Dict]:
    slices = []
    for r in results:
        if "start" in r and "finish" in r and "pid" in r:
            slices.append({"pid": int(r["pid"]), "start": r["start"], "finish": r["finish"]})
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
    slices = _normalize_slices(results)
    if not slices:
        print("plot_gantt: no slices to plot; skipped figure.")
        return

    fig, ax = plt.subplots(figsize=(11, 5), layout="constrained")

    unique_pids = _collect_pids(slices)
    pid_order = unique_pids
    if processes:
        pid_order = sorted({int(p["pid"]) for p in processes if "pid" in p})
    colors = _build_color_map(pid_order)

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

    ax.set_xlabel("Time")
    ax.set_ylabel("Process")
    ax.set_title(title, fontsize=14, weight="bold")
    ax.grid(True, axis="x", linestyle="--", alpha=0.6)

    handles = [mpatches.Patch(color=colors[pid], label=_pid_to_label(pid)) for pid in pid_order if pid in colors]
    if handles:
        ax.legend(
            handles=handles,
            title="Processes",
            loc="center left",
            bbox_to_anchor=(1.02, 0.5),
        )

    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_gantt_grid(
    algorithms_results: Dict[str, List[Dict]],
    filename: str = "gantt_comparison_panel.png",
    show_labels: bool = False,
    bar_height: float = 0.45,
):
    if not algorithms_results:
        print("plot_gantt_grid: no algorithms to compare; skipped figure.")
        return

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

    handles = [mpatches.Patch(color=colors[pid], label=_pid_to_label(pid)) for pid in all_pids]
    axes[-1].legend(
        handles=handles,
        title="Processes",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        ncol=1
    )

    fig.suptitle("Gantt Chart Comparison Panel", fontsize=15, weight="bold")
    fig.savefig(filename, dpi=300, bbox_inches="tight")
    plt.close(fig)
