# -*- coding: utf-8 -*-
"""
Scheduling algorithms for the simulator.

Notes
-----
- FCFS / SJF / SRTF / RR / Priority / CFS / MLFQ
- Added: Priority with Aging (non-preemptive), to mitigate starvation.
- All algorithms return a *timeline* of execution slices:
    {"pid": <int>, "start": <int>, "finish": <int>, ...optional metrics...}
  The plotter and metric functions only require pid/start/finish.
"""

from typing import List, Dict


def fcfs(processes: List[Dict]) -> List[Dict]:
    """First Come First Serve Scheduling"""
    processes = sorted(processes, key=lambda x: x["arrival"])
    time = 0
    timeline = []
    for p in processes:
        start = max(time, p["arrival"])
        finish = start + p["burst"]
        timeline.append({
            "pid": p["pid"], "start": start, "finish": finish
        })
        time = finish
    return timeline


def sjf(processes: List[Dict]) -> List[Dict]:
    """Shortest Job First (Non-Preemptive)"""
    procs = sorted(processes, key=lambda x: x["arrival"])
    ready = []
    time = 0
    timeline = []
    while procs or ready:
        while procs and procs[0]["arrival"] <= time:
            ready.append(procs.pop(0))
        if ready:
            ready.sort(key=lambda x: x["burst"])
            p = ready.pop(0)
            start = max(time, p["arrival"])
            finish = start + p["burst"]
            timeline.append({"pid": p["pid"], "start": start, "finish": finish})
            time = finish
        else:
            # jump to next arrival instead of time += 1
            if procs:
                time = max(time + 1, procs[0]["arrival"])
            else:
                time += 1
    return timeline


def round_robin(processes: List[Dict], quantum: int = 2) -> List[Dict]:
    """Round Robin (preemptive, arrival-aware)."""
    from collections import deque
    procs = sorted(processes, key=lambda x: x["arrival"])
    q = deque()
    time = 0
    remaining = {p["pid"]: p["burst"] for p in procs}
    timeline = []

    # seed time to first arrival if idle
    if procs:
        time = max(0, procs[0]["arrival"])

    # enqueue arrivals that have come by 'time'
    while procs and procs[0]["arrival"] <= time:
        q.append(procs.pop(0))

    while q or procs:
        if not q:
            # idle gap → jump to next arrival
            time = max(time, procs[0]["arrival"])
            while procs and procs[0]["arrival"] <= time:
                q.append(procs.pop(0))

        p = q.popleft()
        exec_time = min(quantum, remaining[p["pid"]])
        start = time
        finish = start + exec_time
        time = finish
        remaining[p["pid"]] -= exec_time

        timeline.append({"pid": p["pid"], "start": start, "finish": finish})

        # pull in new arrivals that came during this slice
        while procs and procs[0]["arrival"] <= time:
            q.append(procs.pop(0))

        if remaining[p["pid"]] > 0:
            q.append(p)  # rotate back

    return timeline


def priority_scheduling(processes: List[Dict]) -> List[Dict]:
    """Non-preemptive Priority (smaller number = higher priority)."""
    procs = sorted(processes, key=lambda x: x["arrival"])
    ready = []
    time = 0
    timeline = []
    while procs or ready:
        while procs and procs[0]["arrival"] <= time:
            ready.append(procs.pop(0))
        if ready:
            ready.sort(key=lambda x: (x["priority"], x["arrival"]))
            p = ready.pop(0)
            start = max(time, p["arrival"])
            finish = start + p["burst"]
            timeline.append({"pid": p["pid"], "start": start, "finish": finish})
            time = finish
        else:
            if procs:
                time = max(time + 1, procs[0]["arrival"])
            else:
                time += 1
    return timeline


def priority_scheduling_with_aging(
    processes: List[Dict],
    aging_interval: int = 5,
    aging_delta: int = 1,
) -> List[Dict]:
    """
    Non-preemptive Priority with Aging:
    Every `aging_interval` units of waiting, reduce (improve) priority by `aging_delta`.
    """
    import heapq

    # copy and track waiting start
    procs = [dict(p) for p in processes]
    procs.sort(key=lambda x: x["arrival"])
    time = procs[0]["arrival"] if procs else 0

    ready = []
    timeline = []
    waiting_since = {}

    def effective_priority(p, now):
        waited = now - waiting_since.get(p["pid"], now)
        bonus = (waited // aging_interval) * aging_delta
        return max(1, p["priority"] - bonus)  # lower is better

    while procs or ready:
        # enqueue new arrivals
        while procs and procs[0]["arrival"] <= time:
            p = procs.pop(0)
            waiting_since[p["pid"]] = time
            heapq.heappush(ready, (p["priority"], p["arrival"], p["pid"], p))

        if not ready:
            if procs:
                time = max(time + 1, procs[0]["arrival"])
                continue
            else:
                break

        # rebuild heap with aged priorities
        tmp = []
        while ready:
            _, arr, pid, p = heapq.heappop(ready)
            heapq.heappush(tmp, (effective_priority(p, time), arr, pid, p))
        ready = tmp

        _, _, _, p = heapq.heappop(ready)
        start = max(time, p["arrival"])
        finish = start + p["burst"]
        timeline.append({"pid": p["pid"], "start": start, "finish": finish})
        time = finish

        # update waiting_since for everyone still waiting
        tmp = []
        while ready:
            pr, arr, pid, rp = ready.pop(0)
            waiting_since[pid] = time
            tmp.append((pr, arr, pid, rp))
        ready = tmp

    return timeline


def srtf(processes: List[Dict]) -> List[Dict]:
    """Shortest Remaining Time First (preemptive SJF)."""
    import heapq
    procs = sorted(processes, key=lambda x: x["arrival"])
    n = len(procs)
    time = procs[0]["arrival"] if procs else 0
    completed = 0
    ready = []
    timeline = []
    remaining = {p["pid"]: p["burst"] for p in procs}
    current_pid = None
    last_time = time

    while completed < n:
        while procs and procs[0]["arrival"] <= time:
            p = procs.pop(0)
            heapq.heappush(ready, (remaining[p["pid"]], p["pid"], p))

        if ready:
            rem, pid, p = heapq.heappop(ready)
            # if CPU switched, record a boundary (preemption)
            if current_pid is None:
                last_time = time
                current_pid = pid
            elif current_pid != pid:
                if last_time < time:
                    timeline.append({"pid": current_pid, "start": last_time, "finish": time})
                last_time = time
                current_pid = pid

            # run 1 time unit
            time += 1
            remaining[pid] -= 1

            if remaining[pid] == 0:
                # close the running slice
                timeline.append({"pid": pid, "start": last_time, "finish": time})
                current_pid = None
                completed += 1
            else:
                heapq.heappush(ready, (remaining[pid], pid, p))
        else:
            time += 1

    return timeline


def cfs(processes: List[Dict], time_slice: int = 2) -> List[Dict]:
    """Simplified Completely Fair Scheduler (CFS)"""
    import heapq
    procs = [dict(p, vruntime=0.0) for p in processes]
    procs = sorted(procs, key=lambda x: x["arrival"])
    time = procs[0]["arrival"] if procs else 0
    timeline = []
    ready = []
    remaining = {p["pid"]: p["burst"] for p in procs}
    finished = set()

    while len(finished) < len(remaining):
        while procs and procs[0]["arrival"] <= time:
            p = procs.pop(0)
            heapq.heappush(ready, (p["vruntime"], p["pid"], p))

        if ready:
            vr, pid, p = heapq.heappop(ready)
            exec_time = min(time_slice, remaining[pid])
            start = time
            time += exec_time
            remaining[pid] -= exec_time
            timeline.append({"pid": pid, "start": start, "finish": start + exec_time})

            # Update vruntime — lower (better) priority increases vruntime more slowly if provided
            weight = max(1.0, float(p.get("priority", 1)))
            p["vruntime"] = vr + (exec_time / weight)

            if remaining[pid] <= 0:
                finished.add(pid)
            else:
                heapq.heappush(ready, (p["vruntime"], pid, p))
        else:
            # jump to next arrival to avoid 1-by-1 stepping
            if procs:
                time = max(time + 1, procs[0]["arrival"])
            else:
                time += 1

    return timeline


def mlfq(processes: List[Dict], queues: int = 3, base_quantum: int = 2) -> List[Dict]:
    """Multilevel Feedback Queue Scheduling (simplified)"""
    from collections import deque
    procs = sorted(processes, key=lambda x: x["arrival"])
    time = procs[0]["arrival"] if procs else 0
    timeline = []
    ready_queues = [deque() for _ in range(queues)]
    remaining = {p["pid"]: p["burst"] for p in procs}
    finished = set()

    while len(finished) < len(remaining):
        # Add new arrivals to top queue
        while procs and procs[0]["arrival"] <= time:
            ready_queues[0].append(procs.pop(0))

        executed = False
        for i in range(queues):
            if ready_queues[i]:
                p = ready_queues[i].popleft()
                quantum = base_quantum * (2 ** i)
                exec_time = min(quantum, remaining[p["pid"]])
                start = time
                time += exec_time
                remaining[p["pid"]] -= exec_time
                timeline.append({"pid": p["pid"], "start": start, "finish": time})
                executed = True

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
            # jump to next arrival if idle
            if procs:
                time = max(time + 1, procs[0]["arrival"])
            else:
                time += 1

    return timeline
