import subprocess
import random

def fetch_linux_processes(top_n=5):
    """
    Fetch top N processes from Linux sorted by CPU usage.
    Returns a list of dicts: pid, name, priority, burst, arrival
    """
    cmd = f"ps -eo pid,comm,pri,etimes,%cpu --sort=-%cpu | head -n {top_n+1}"
    output = subprocess.getoutput(cmd).splitlines()[1:]  # skip header
    processes = []
    for i, line in enumerate(output):
        parts = line.split()
        if len(parts) < 5:
            continue
        processes.append({
            "pid": int(parts[0]),
            "name": parts[1][:15].lower(), # Normalize name
            "priority": max(1, 140 - int(parts[2])),  # invert PRI so higher = better
            "burst": max(1, int(parts[3]) // 10),     # rough burst estimate
            "arrival": random.randint(0, 5 * i)       # simulated arrival
        })
    return processes


