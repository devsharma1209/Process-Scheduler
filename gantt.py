import matplotlib.pyplot as plt

def plot_gantt(results, title="Gantt Chart"):
    for r in results:
        plt.barh(f"P{r['pid']}", r['finish'] - r['start'], left=r['start'])
    plt.xlabel("Time")
    plt.ylabel("Process")
    plt.title(title)
    plt.show()
    plt.savefig("fcfs_gantt.png")