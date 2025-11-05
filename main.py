from algorithms import (
    fcfs, sjf, srtf,
    round_robin, priority_scheduling,
    cfs, mlfq
)
from linux_fetch import fetch_linux_processes
from utils import print_table
from gantt import plot_gantt


def run_scheduler(name, func, processes, **kwargs):
    print(f"\nRunning {name} Scheduler...")
    results = func(processes, **kwargs) if kwargs else func(processes)
    print_table(results)
    plot_gantt(results, f"{name} Gantt Chart", filename=f"{name.lower().replace(' ', '_')}_gantt.png")
    return results


def main():
    print("Fetching Linux processes...")
    processes = fetch_linux_processes(top_n=5)
    print("\nFetched Processes:")
    for p in processes:
        print(p)

    schedulers = [
        ("FCFS", fcfs, {}),
        ("SJF (Non-Preemptive)", sjf, {}),
        ("SRTF (Preemptive SJF)", srtf, {}),
        ("Round Robin", round_robin, {"quantum": 2}),
        ("Priority Scheduling", priority_scheduling, {}),
        ("Completely Fair Scheduler (CFS)", cfs, {}),
        ("Multilevel Feedback Queue (MLFQ)", mlfq, {})
    ]

    summary = []
    for name, func, params in schedulers:
        results = run_scheduler(name, func, processes, **params)
        avg_wait = sum(r["waiting"] for r in results) / len(results)
        avg_turnaround = sum(r["turnaround"] for r in results) / len(results)
        summary.append({"Scheduler": name, "Avg Wait": avg_wait, "Avg Turnaround": avg_turnaround})

    print("\n=== Scheduler Comparison Summary ===")
    from tabulate import tabulate
    print(tabulate(summary, headers="keys", tablefmt="grid"))


if __name__ == "__main__":
    main()
