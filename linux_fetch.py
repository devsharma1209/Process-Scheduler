import subprocess

def fetch_linux_processes(top_n=5):
    """
    Fetch top N processes by CPU priority.
    Returns a list of dicts: pid, priority, elapsed_time
    """
    cmd = f"ps -eo pid,comm,pri,etimes --sort=-pri | head -n {top_n+1}"
    output = subprocess.getoutput(cmd).splitlines()[1:]  # skip header
    processes = []
    for line in output:
        parts = line.split()
        processes.append({
            "pid": int(parts[0]),
            "name": parts[1],
            "priority": int(parts[2]),
            "burst": int(parts[3]),  # approximate using elapsed time
            "arrival": 0
        })
    return processes




