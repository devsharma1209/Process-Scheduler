from tabulate import tabulate

def print_table(results):
    print(tabulate(results, headers="keys", tablefmt="fancy_grid"))
    avg_wait = sum(r["waiting"] for r in results)/len(results)
    avg_turnaround = sum(r["turnaround"] for r in results)/len(results)
    print(f"\nAverage Waiting Time: {avg_wait:.2f}")
    print(f"Average Turnaround Time: {avg_turnaround:.2f}\n")

