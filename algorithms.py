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

def srtf(processes):
    """Shortest Remaining Time First (Preemptive SJF)"""
    import heapq
    processes = sorted(processes, key=lambda x: x["arrival"])
    n = len(processes)
    time = 0
    completed = 0
    ready = []
    results = []
    remaining = {p["pid"]: p["burst"] for p in processes}
    start_times = {}
    finish_times = {}
    waiting_times = {}
    turnaround_times = {}

    while completed < n:
        # Add arrived processes to ready queue
        while processes and processes[0]["arrival"] <= time:
            p = processes.pop(0)
            # add tie-breaker (pid) to avoid TypeError
            heapq.heappush(ready, (remaining[p["pid"]], p["pid"], p))

        if ready:
            rem, pid, p = heapq.heappop(ready)
            if p["pid"] not in start_times:
                start_times[p["pid"]] = time
            remaining[p["pid"]] -= 1
            time += 1
            if remaining[p["pid"]] == 0:
                completed += 1
                finish_times[p["pid"]] = time
                turnaround_times[p["pid"]] = finish_times[p["pid"]] - p["arrival"]
                waiting_times[p["pid"]] = turnaround_times[p["pid"]] - p["burst"]
            else:
                heapq.heappush(ready, (remaining[p["pid"]], p["pid"], p))
        else:
            time += 1

    for pid in finish_times:
        results.append({
            "pid": pid,
            "start": start_times[pid],
            "finish": finish_times[pid],
            "waiting": waiting_times[pid],
            "turnaround": turnaround_times[pid]
        })
    return results


def cfs(processes, time_slice=2):
    """Simplified Completely Fair Scheduler (CFS)"""
    import heapq
    # Initialize each process with virtual runtime (vruntime)
    for p in processes:
        p["vruntime"] = 0
    time = 0
    results = []
    ready = []
    processes = sorted(processes, key=lambda x: x["arrival"])
    remaining = {p["pid"]: p["burst"] for p in processes}
    finished = set()

    while len(finished) < len(remaining):
        # Add new arrivals
        while processes and processes[0]["arrival"] <= time:
            p = processes.pop(0)
            # add tie-breaker (pid)
            heapq.heappush(ready, (0, p["pid"], p))

        if ready:
            vr, pid, p = heapq.heappop(ready)
            exec_time = min(time_slice, remaining[p["pid"]])
            start = time
            time += exec_time
            remaining[p["pid"]] -= exec_time
            # Update vruntime — lower priority increases vruntime faster
            p["vruntime"] += exec_time / (p.get("priority", 1))

            if remaining[p["pid"]] <= 0:
                finished.add(p["pid"])
                finish = time
                turnaround = finish - p["arrival"]
                waiting = turnaround - p["burst"]
                results.append({
                    "pid": p["pid"],
                    "start": start,
                    "finish": finish,
                    "waiting": waiting,
                    "turnaround": turnaround
                })
            else:
                heapq.heappush(ready, (p["vruntime"], p["pid"], p))
        else:
            time += 1

    return results


def mlfq(processes, queues=3, base_quantum=2):
    """Multilevel Feedback Queue Scheduling (simplified)"""
    from collections import deque
    processes = sorted(processes, key=lambda x: x["arrival"])
    time = 0
    results = []
    ready_queues = [deque() for _ in range(queues)]
    remaining = {p["pid"]: p["burst"] for p in processes}
    finished = set()

    while len(finished) < len(remaining):
        # Add new arrivals to top queue
        while processes and processes[0]["arrival"] <= time:
            ready_queues[0].append(processes.pop(0))

        executed = False
        for i in range(queues):
            if ready_queues[i]:
                p = ready_queues[i].popleft()
                quantum = base_quantum * (2 ** i)
                exec_time = min(quantum, remaining[p["pid"]])
                start = time
                time += exec_time
                remaining[p["pid"]] -= exec_time
                executed = True

                # Record this execution slice
                results.append({
                    "pid": p["pid"],
                    "start": start,
                    "finish": time,
                    "waiting": time - p["arrival"] - (p["burst"] - remaining[p["pid"]]),
                    "turnaround": time - p["arrival"]
                })

                if remaining[p["pid"]] <= 0:
                    finished.add(p["pid"])
                else:
                    # Demote to next lower queue or stay in last queue
                    if i + 1 < queues:
                        ready_queues[i + 1].append(p)
                    else:
                        ready_queues[i].append(p)
                break

        if not executed:
            time += 1

    return results
