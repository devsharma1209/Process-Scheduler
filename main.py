#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main runner for the CPU Scheduling Simulator.

Pipeline:
1) Fetches top-N Linux processes (pid, name, priority, burst, arrival).
2) Runs multiple scheduling algorithms on the same (deep-copied) input set.
3) Prints per-process + global metrics (avg WT/TAT/RT, CPU util, throughput, ctx switches, etc.).
4) Saves high-quality Gantt charts for each algorithm.
5) Saves a comparison panel to visually compare algorithms.
6) (Optional) Detects starvation and demonstrates aging for Priority Scheduling.

Requirements:
    pip install matplotlib tabulate numpy
"""

from copy import deepcopy

# NOTE: module name is 'algorithm.py', so import from 'algorithm'
from algorithm import (
    fcfs, sjf, srtf,
    round_robin, priority_scheduling,
    cfs, mlfq,
    priority_scheduling_with_aging
)
from linux_fetch import fetch_linux_processes
from utils import print_table, detect_starvation
from gantt import plot_gantt, plot_gantt_grid

from tabulate import tabulate


def _deepcopy_processes(processes):
    return [dict(p) for p in processes]


def run_scheduler(name, func, base_processes, gantt_labels=True, **kwargs):
    """
    Run a scheduler on a fresh copy, print metrics, draw & save a Gantt chart,
    and return (timeline, metrics).
    """
    print(f"\n================ {name} ================")
    procs = _deepcopy_processes(base_processes)

    # Execute algorithm
    results = func(procs, **kwargs) if kwargs else func(procs)

    # Print per-process and global performance metrics
    per_proc, metrics = print_table(results, procs)

    # Save a high quality single Gantt chart for this algorithm
    out_file = f"{name.lower().replace(' ', '_').replace('(', '').replace(')', '').replace('-', '')}_gantt.png"
    plot_gantt(
        results,
        title=f"{name} — Gantt Chart",
        filename=out_file,
        processes=procs,
        show_labels=gantt_labels
    )
    print(f"🖼️  Saved Gantt: {out_file}")

    return results, metrics, per_proc


def main():
    print("Fetching Linux processes...")
    processes = fetch_linux_processes(top_n=5)

    if not processes:
        print("No processes fetched. Exiting.")
        return

    # Normalize defaults and print fetched set
    print("\nFetched Processes (normalized):")
    for p in processes:
        p.setdefault("priority", 1)
        print(f"PID: {p['pid']:>5} | "
              f"Name: {p.get('name', 'unknown'):<15} | "
              f"Priority: {p['priority']:<3} | "
              f"Burst: {p['burst']:<3} | "
              f"Arrival: {p['arrival']:<3}")

    # Define scheduler suite
    schedulers = [
        ("FCFS", fcfs, {}),
        ("SJF (Non-Preemptive)", sjf, {}),
        ("SRTF (Preemptive SJF)", srtf, {}),
        ("Round Robin (q=2)", round_robin, {"quantum": 2}),
        ("Priority Scheduling", priority_scheduling, {}),
        ("Completely Fair Scheduler (CFS)", cfs, {}),
        ("Multilevel Feedback Queue (MLFQ)", mlfq, {}),
    ]

    # Run all schedulers, collect results and metrics
    all_results = {}
    summary_rows = []

    for name, func, params in schedulers:
        results, metrics, per_proc = run_scheduler(name, func, processes, **params)
        all_results[name] = results

        summary_rows.append({
            "Scheduler": name,
            "Avg Wait": f"{metrics['Avg Waiting Time']:.2f}",
            "Avg Turnaround": f"{metrics['Avg Turnaround Time']:.2f}",
            "Avg Response": f"{metrics['Avg Response Time']:.2f}",
            "CPU Util (%)": f"{metrics['CPU Utilization (%)']:.2f}",
            "Throughput": f"{metrics['Throughput (proc/unit time)']:.3f}",
            "Ctx Switches": metrics['Context Switches'],
            "Makespan": f"{metrics['Makespan']:.2f}",
        })

        # Optional: detect starvation on *priority* schedule and rerun with aging
        if "Priority" in name:
            starving = detect_starvation(per_proc, threshold=20)  # tweak as you like
            if starving:
                print(f"🚨 Starvation detected for PIDs: {starving}. Re-running with Aging...")
                aged_name = "Priority Scheduling (Aging)"
                aged_results, aged_metrics, _ = run_scheduler(
                    aged_name,
                    priority_scheduling_with_aging,
                    processes,
                    aging_interval=5,
                    aging_delta=1,
                )
                all_results[aged_name] = aged_results
                summary_rows.append({
                    "Scheduler": aged_name,
                    "Avg Wait": f"{aged_metrics['Avg Waiting Time']:.2f}",
                    "Avg Turnaround": f"{aged_metrics['Avg Turnaround Time']:.2f}",
                    "Avg Response": f"{aged_metrics['Avg Response Time']:.2f}",
                    "CPU Util (%)": f"{aged_metrics['CPU Utilization (%)']:.2f}",
                    "Throughput": f"{aged_metrics['Throughput (proc/unit time)']:.3f}",
                    "Ctx Switches": aged_metrics['Context Switches'],
                    "Makespan": f"{aged_metrics['Makespan']:.2f}",
                })

    # Print comparison table
    print("\n=== Scheduler Comparison Summary ===")
    print(tabulate(summary_rows, headers="keys", tablefmt="grid"))

    # Save a comparison panel (side-by-side)
    compare_file = "gantt_comparison_panel.png"
    # Turn off labels here to reduce clutter across many panels
    plot_gantt_grid(all_results, filename=compare_file, show_labels=False)
    print(f"🖼️  Saved comparison panel: {compare_file}")


if __name__ == "__main__":
    main()
