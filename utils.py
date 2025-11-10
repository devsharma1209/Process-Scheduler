# -*- coding: utf-8 -*-
"""
Utility functions for metric aggregation, tabular display, and performance reporting.
This version integrates perfectly with the new `main.py`.
"""

from tabulate import tabulate
from collections import defaultdict
import statistics


def aggregate_metrics(timeline, processes):
    """
    Compute per-process and global metrics from execution slices.

    Args:
        timeline (list of dict): {"pid", "start", "finish"}
        processes (list of dict): {"pid", "arrival", "burst", ...}

    Returns:
        (per_proc_metrics, global_metrics)
    """
    if not timeline or not processes:
        return [], {
            "Avg Waiting Time": 0,
            "Avg Turnaround Time": 0,
            "Avg Response Time": 0,
            "Min Waiting Time": 0,
            "Max Waiting Time": 0,
            "Std Dev Waiting Time": 0,
            "CPU Utilization (%)": 0,
            "Throughput (proc/unit time)": 0,
            "Context Switches": 0,
            "Makespan": 0,
        }

    # Group slices by PID (for preemptive schedulers)
    by_pid = defaultdict(list)
    for sl in sorted(timeline, key=lambda x: (x["start"], x["finish"])):
        by_pid[int(sl["pid"])].append(sl)

    # Process info lookup
    info = {int(p["pid"]): p for p in processes}

    # Per-process metrics
    per_proc = []
    for pid, slices in by_pid.items():
        arrival = info.get(pid, {}).get("arrival", 0)
        burst = info.get(pid, {}).get("burst", 0)
        first_start = min(s["start"] for s in slices)
        last_finish = max(s["finish"] for s in slices)

        turnaround = last_finish - arrival
        waiting = turnaround - burst
        response = first_start - arrival
        active = sum(s["finish"] - s["start"] for s in slices)

        per_proc.append({
            "pid": pid,
            "arrival": arrival,
            "burst": burst,
            "start": first_start,
            "finish": last_finish,
            "response": response,
            "waiting": waiting,
            "turnaround": turnaround,
            "active": active,
        })

    per_proc.sort(key=lambda x: x["pid"])

    # Global system metrics
    makespan = max(s["finish"] for s in timeline) - min(s["start"] for s in timeline)
    cpu_busy = sum(s["finish"] - s["start"] for s in timeline)
    cpu_util = (cpu_busy / makespan * 100) if makespan > 0 else 0
    throughput = (len(per_proc) / makespan) if makespan > 0 else 0

    # Context switches = count PID changes between consecutive slices
    ordered = sorted(timeline, key=lambda s: (s["start"], s["finish"]))
    ctx_switches = sum(ordered[i - 1]["pid"] != ordered[i]["pid"]
                       for i in range(1, len(ordered)))

    # Statistical metrics
    waiting_times = [p["waiting"] for p in per_proc]
    avg_wait = statistics.mean(waiting_times)
    avg_tat = statistics.mean(p["turnaround"] for p in per_proc)
    avg_resp = statistics.mean(p["response"] for p in per_proc)
    min_wait = min(waiting_times)
    max_wait = max(waiting_times)
    std_wait = statistics.stdev(waiting_times) if len(waiting_times) > 1 else 0

    global_metrics = {
        "Avg Waiting Time": avg_wait,
        "Avg Turnaround Time": avg_tat,
        "Avg Response Time": avg_resp,
        "Min Waiting Time": min_wait,
        "Max Waiting Time": max_wait,
        "Std Dev Waiting Time": std_wait,
        "CPU Utilization (%)": cpu_util,
        "Throughput (proc/unit time)": throughput,
        "Context Switches": ctx_switches,
        "Makespan": makespan,
    }

    return per_proc, global_metrics


def print_table(timeline, processes):
    """
    Pretty-print metrics for a scheduler run.
    Returns: (per-process list, global_metrics dict)
    """
    per_proc, globals_ = aggregate_metrics(timeline, processes)

    if not per_proc:
        print("⚠️  No process data to display.")
        return per_proc, globals_

    # Per-process table
    headers = ["pid", "arrival", "burst", "start", "finish", "response", "waiting", "turnaround"]
    print(tabulate(per_proc, headers=headers, tablefmt="fancy_grid", floatfmt=".2f"))

    # Global metrics
    print("\n" + "=" * 60)
    print("📊 PERFORMANCE METRICS")
    print("=" * 60)

    print("\n⏱️  Time Metrics:")
    print(f"  • Avg Waiting Time.............. {globals_['Avg Waiting Time']:.2f}")
    print(f"  • Avg Turnaround Time........... {globals_['Avg Turnaround Time']:.2f}")
    print(f"  • Avg Response Time............. {globals_['Avg Response Time']:.2f}")

    print("\n📈 Distribution Metrics:")
    print(f"  • Min Waiting Time.............. {globals_['Min Waiting Time']:.2f}")
    print(f"  • Max Waiting Time.............. {globals_['Max Waiting Time']:.2f}")
    print(f"  • Std Dev Waiting Time.......... {globals_['Std Dev Waiting Time']:.2f}")

    print("\n⚙️  System Metrics:")
    print(f"  • CPU Utilization (%)........... {globals_['CPU Utilization (%)']:.2f}")
    print(f"  • Throughput (proc/unit time)... {globals_['Throughput (proc/unit time)']:.3f}")
    print(f"  • Context Switches.............. {globals_['Context Switches']}")
    print(f"  • Makespan...................... {globals_['Makespan']:.2f}")

    print("=" * 60 + "\n")

    return per_proc, globals_
