from tabulate import tabulate

def print_table(results):
    print(tabulate(results, headers="keys", tablefmt="fancy_grid"))
    
    n = len(results)
    avg_wait = sum(r["waiting"] for r in results) / n
    avg_turnaround = sum(r["turnaround"] for r in results) / n

    # Optional extra metrics if available
    total_time = max(r["finish"] for r in results) - min(r["start"] for r in results)
    cpu_busy = sum(r["turnaround"] - r["waiting"] for r in results)
    cpu_util = (cpu_busy / total_time) * 100 if total_time > 0 else 0
    throughput = n / total_time if total_time > 0 else 0

    print(f"\nAverage Waiting Time: {avg_wait:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround:.2f}")
    print(f"CPU Utilization: {cpu_util:.2f}%")
    print(f"Throughput: {throughput:.2f} processes/unit time\n")
