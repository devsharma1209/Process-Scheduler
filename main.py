from algorithms import (
    fcfs,
    sjf,
    srjf,
    round_robin,
    priority_scheduling
)
from linux_fetch import fetch_linux_processes
from utils import print_table
from gantt import plot_gantt


def run_scheduler(name, func, processes, **kwargs):
    """Helper to run a scheduler, display results, and plot Gantt chart."""
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

    # Run each scheduler
    run_scheduler("FCFS", fcfs, processes)
    run_scheduler("SJF (Non-Preemptive)", sjf, processes)
    run_scheduler("SRJF (Preemptive SJF)", srjf, processes)
    run_scheduler("Round Robin", round_robin, processes, quantum=2)
    run_scheduler("Priority Scheduling", priority_scheduling, processes)


if __name__ == "__main__":
    main()
