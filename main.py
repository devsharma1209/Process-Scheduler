#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Main runner for the CPU Scheduling Simulator.

What this script does:
1) Fetches top-N Linux processes (pid, name, priority, burst, arrival).
2) Runs multiple scheduling algorithms on the same (deep-copied) input set.
3) Prints per-process + global metrics (avg WT/TAT/RT, CPU util, throughput, ctx switches, etc.).
4) Saves high-quality Gantt charts for each algorithm.
5) Saves a side-by-side comparison panel to visually compare algorithms.

Requirements (pip):
    matplotlib
    tabulate
    numpy

Optional (auto-installed elsewhere in your project):
    psutil   # only if you extend the Linux mini task manager later
"""

from copy import deepcopy

from algorithms import (
    fcfs, sjf, srtf,
    round_robin, priority_scheduling,
    cfs, mlfq
)
from linux_fetch import fetch_linux_processes
from utils import print_table
from gantt import plot_gantt, plot_gantt_grid

from tabulate import tabulate


def _deepcopy_processes(processes):
    """
    Return a deep copy of processes so algorithms that mutate lists (e.g., in-place sort)
    do not affect other schedulers.
    """
    return [dict(p) for p in processes]


def run_scheduler(name, func, base_processes, **kwargs):
    """
    Run a scheduler function safely on a fresh copy of the process list,
    print metrics, draw & save a Gantt chart, and return results + metrics.
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
        processes=procs  # used for consistent legend ordering
    )
    print(f"🖼️  Saved Gantt: {out_file}")

    return results, metrics


def main():
    print("Fetching Linux processes...")
    processes = fetch_linux_processes(top_n=5)

    if not processes:
        print("No processes fetched. Exiting.")
        return

    
    print("\nFetched Processes (normalized):")
for p in processes:
    p.setdefault("priority", 1)
    # Nicely formatted output
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
        results, metrics = run_scheduler(name, func, processes, **params)
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

    # Print comparison table
    print("\n=== Scheduler Comparison Summary ===")
    print(tabulate(summary_rows, headers="keys", tablefmt="grid"))

    # Save a comparison panel (side-by-side)
    compare_file = "gantt_comparison_panel.png"
    plot_gantt_grid(all_results, filename=compare_file)
    print(f"🖼️  Saved comparison panel: {compare_file}")


if __name__ == "__main__":
    main()

