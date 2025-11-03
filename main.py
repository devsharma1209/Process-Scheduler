from algorithms import fcfs, sjf, round_robin, priority_scheduling
from linux_fetch import fetch_linux_processes
from utils import print_table
from gantt import plot_gantt


def main():
    print("Fetching Linux processes...")
    processes = fetch_linux_processes(top_n=5)
    for p in processes:
        print(p)
    
    print("\nRunning FCFS Scheduler...")
    fcfs_results = fcfs(processes)
    print_table(fcfs_results)
    plot_gantt(fcfs_results, "FCFS Gantt Chart")

    print("\nRunning SJF Scheduler...")
    sjf_results = sjf(processes)
    print_table(sjf_results)
    plot_gantt(sjf_results, "SJF Gantt Chart")

    print("\nRunning Round Robin Scheduler...")
    rr_results = round_robin(processes, quantum=2)
    print_table(rr_results)
    plot_gantt(rr_results, "Round Robin Gantt Chart")

    print("\nRunning Priority Scheduling...")
    prio_results = priority_scheduling(processes)
    print_table(prio_results)
    plot_gantt(prio_results, "Priority Scheduling Gantt Chart")

if __name__ == "__main__":
    main()




