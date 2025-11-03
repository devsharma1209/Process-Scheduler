def fcfs(processes):
    """First Come First Serve Scheduling"""
    processes.sort(key=lambda x: x["arrival"])
    time = 0
    results = []
    for p in processes:
        start = max(time, p["arrival"])
        finish = start + p["burst"]
        waiting = start - p["arrival"]
        turnaround = finish - p["arrival"]
        results.append({
            "pid": p["pid"], "start": start, "finish": finish,
            "waiting": waiting, "turnaround": turnaround
        })
        time = finish
    return results


def sjf(processes):
    """Shortest Job First (Non-Preemptive)"""
    processes = sorted(processes, key=lambda x: x["arrival"])
    ready = []
    time = 0
    results = []
    while processes or ready:
        # Add arrived processes to ready queue
        while processes and processes[0]["arrival"] <= time:
            ready.append(processes.pop(0))
        if ready:
            ready.sort(key=lambda x: x["burst"])
            p = ready.pop(0)
            start = time
            finish = start + p["burst"]
            waiting = start - p["arrival"]
            turnaround = finish - p["arrival"]
            results.append({
                "pid": p["pid"], "start": start, "finish": finish,
                "waiting": waiting, "turnaround": turnaround
            })
            time = finish
        else:
            time += 1
    return results


def round_robin(processes, quantum=2):
    """Round Robin Scheduling"""
    from collections import deque
    queue = deque(processes)
    time = 0
    remaining = {p["pid"]: p["burst"] for p in processes}
    results = []
    last_finish = {p["pid"]: 0 for p in processes}
    
    while queue:
        p = queue.popleft()
        exec_time = min(quantum, remaining[p["pid"]])
        start = max(time, p["arrival"])
        finish = start + exec_time
        time = finish
        remaining[p["pid"]] -= exec_time
        last_finish[p["pid"]] = finish
        if remaining[p["pid"]] > 0:
            queue.append(p)
        else:
            turnaround = finish - p["arrival"]
            waiting = turnaround - p["burst"]
            results.append({
                "pid": p["pid"], "start": start, "finish": finish,
                "waiting": waiting, "turnaround": turnaround
            })
    return results


def priority_scheduling(processes):
    """Non-preemptive Priority Scheduling (smaller number = higher priority)"""
    processes = sorted(processes, key=lambda x: x["arrival"])
    ready = []
    time = 0
    results = []
    while processes or ready:
        while processes and processes[0]["arrival"] <= time:
            ready.append(processes.pop(0))
        if ready:
            ready.sort(key=lambda x: x["priority"])
            p = ready.pop(0)
            start = time
            finish = start + p["burst"]
            waiting = start - p["arrival"]
            turnaround = finish - p["arrival"]
            results.append({
                "pid": p["pid"], "start": start, "finish": finish,
                "waiting": waiting, "turnaround": turnaround
            })
            time = finish
        else:
            time += 1
    return results

