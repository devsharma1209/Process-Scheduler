import matplotlib.pyplot as plt

def plot_gantt(results, title="Gantt Chart", filename="gantt_chart.png"):
    fig, ax = plt.subplots(figsize=(10, 5))
    for r in results:
        ax.barh(f"P{r['pid']}", r['finish'] - r['start'], left=r['start'],
                height=0.5, edgecolor='black', align='center')
        ax.text((r['start'] + r['finish']) / 2, f"P{r['pid']}",
                f"{r['start']}–{r['finish']}", ha='center', va='center',
                color='white', fontsize=9, fontweight='bold')
    ax.set_xlabel("Time")
    ax.set_ylabel("Process")
    ax.set_title(title)
    ax.grid(True, axis='x', linestyle='--', alpha=0.6)
    plt.tight_layout()
    plt.savefig(filename)
    plt.show()
