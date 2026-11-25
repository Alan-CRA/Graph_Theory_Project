import os
import numpy as np


def choose_table(folder):
    while True:
        choice = input(
            "\nEnter table number (1-14) or custom filename [or 'q' to quit]: "
        ).strip()
        if choice.lower() in ("q", "quit", "exit"):
            return None
        if choice.isdigit() and 1 <= int(choice) <= 14:
            path = f"{folder}/table {int(choice)}.txt"
            if os.path.isfile(path):
                return path
            print(f"[ERROR] File '{path}' not found.")
        elif os.path.isfile(choice):
            return choice
        elif os.path.isfile(f"{folder}/{choice}"):
            return f"{folder}/{choice}"
        else:
            print("[ERROR] Invalid input or file not found. Try again.")


def build_graph(filepath):
    m = []
    with open(filepath, "r", encoding="utf-8") as f:
        for line in f:
            parts = list(map(int, line.split()))
            if parts:  # Ignore empty lines
                m.append(parts[1:])  # [duration, pred1, pred2, ...]

    n_tasks = len(m)
    n_nodes = n_tasks + 2
    omega = n_nodes - 1

    graph = np.full((n_nodes, n_nodes), np.inf)
    has_successor = [False] * (n_tasks + 1)

    print("\n--- STEP 1: Creating the scheduling graph ---")
    edges = []

    for task_idx, values in enumerate(m):
        u = task_idx + 1
        if len(values) == 1:
            # No predecessors -> connect from 0 with weight 0
            graph[0][u] = 0
            edges.append((0, u, 0))
        else:
            predecessors = values[1:]
            for p in predecessors:
                if 1 <= p <= n_tasks:
                    w = m[p - 1][0]
                    graph[p][u] = w
                    has_successor[p] = True
                    edges.append((p, u, w))

    # Connect tasks with no successors to omega (N + 1)
    for u in range(1, n_tasks + 1):
        if not has_successor[u]:
            w = m[u - 1][0]
            graph[u][omega] = w
            edges.append((u, omega, w))

    # Sort edges for clean trace output
    edges.sort()
    print(f"{n_nodes} vertices")
    print(f"{len(edges)} edges")
    for u, v, w in edges:
        print(f"{u} -> {v} = {int(w)}")

    return graph


def display_matrix(graph):
    print("\n--- STEP 2: Value Matrix ---")
    n_nodes = graph.shape[0]
    col_w = 4

    header = " " * col_w + "".join(f"{j:>{col_w}}" for j in range(n_nodes))
    print(header)
    print("-" * len(header))

    for i in range(n_nodes):
        row_str = f"{i:<{col_w - 1}}|"
        for j in range(n_nodes):
            val = "*" if np.isinf(graph[i][j]) else str(int(graph[i][j]))
            row_str += f"{val:>{col_w}}"
        print(row_str)


def check_scheduling_graph(graph):
    print("\n--- STEP 3: Checking Scheduling Graph Properties ---")
    n_nodes = graph.shape[0]
    is_valid = True

    # 1. Single entry point & single exit point
    in_degrees = np.sum(~np.isinf(graph), axis=0)
    out_degrees = np.sum(~np.isinf(graph), axis=1)

    entries = np.where(in_degrees == 0)[0].tolist()
    exits = np.where(out_degrees == 0)[0].tolist()

    if len(entries) == 1:
        print(f"There is one entry point: {entries[0]}")
    else:
        print(f"[ERROR] Expected 1 entry point, found: {entries}")
        is_valid = False

    if len(exits) == 1:
        print(f"There is one exit point: {exits[0]}")
    else:
        print(f"[ERROR] Expected 1 exit point, found: {exits}")
        is_valid = False

    # 2. Cycle detection (Method of eliminating entry points)
    print("\nDetecting cycles (Method of eliminating entry points):")
    remaining = set(range(n_nodes))
    work_in_deg = in_degrees.copy()

    while remaining:
        current_entries = sorted([v for v in remaining if work_in_deg[v] == 0])
        if not current_entries:
            print("Entry points: None")
            print(f"Remaining vertices: {' '.join(map(str, sorted(remaining)))}")
            print("-> Cycle detected!")
            is_valid = False
            break

        print(f"Entry points: {' '.join(map(str, current_entries))}")
        print("Eliminating entry points...")
        for u in current_entries:
            remaining.remove(u)
            for v in range(n_nodes):
                if not np.isinf(graph[u][v]):
                    work_in_deg[v] -= 1

        rem_str = " ".join(map(str, sorted(remaining))) if remaining else "None"
        print(f"Remaining vertices: {rem_str}")

    if not remaining and is_valid:
        print("-> There is no cycle")

    # 3. Same weights for all outgoing edges of each vertex
    same_weights = True
    for u in range(n_nodes):
        weights = graph[u][~np.isinf(graph[u])]
        if len(np.unique(weights)) > 1:
            same_weights = False
            print(f"[ERROR] Vertex {u} has different outgoing weights: {weights}")
    if same_weights:
        print("The values of outgoing edges for each vertex are the same.")
    else:
        is_valid = False

    # 4. Outgoing edges of entry vertex 0 have weight 0
    entry_weights = graph[0][~np.isinf(graph[0])]
    if np.all(entry_weights == 0):
        print("Outgoing edges of entry vertex 0 have a weight of 0.")
    else:
        print("[ERROR] Outgoing edges of entry vertex 0 are not all 0.")
        is_valid = False

    # 5. No negative edges
    finite_weights = graph[~np.isinf(graph)]
    if np.all(finite_weights >= 0):
        print("There are no negative-weight edges.")
    else:
        print("[ERROR] Graph contains negative-weight edges.")
        is_valid = False

    print("-> Valid scheduling graph!" if is_valid else "-> NOT a valid scheduling graph.")
    return is_valid


def compute_ranks(graph):
    print("\n--- STEP 4: Computing Ranks ---")
    n_nodes = graph.shape[0]
    in_deg = np.sum(~np.isinf(graph), axis=0)
    remaining = set(range(n_nodes))
    ranks = {}
    current_rank = 0

    while remaining:
        sources = sorted([v for v in remaining if in_deg[v] == 0])
        for u in sources:
            ranks[u] = current_rank
            remaining.remove(u)
        for u in sources:
            for v in range(n_nodes):
                if not np.isinf(graph[u][v]):
                    in_deg[v] -= 1
        current_rank += 1

    print(f"{'Vertex':<8} | {'Rank':<6}")
    print("-" * 17)
    for v, r in sorted(ranks.items(), key=lambda x: (x[1], x[0])):
        print(f"{v:<8} | {r:<6}")

    return ranks


def compute_calendars_and_critical_paths(graph, ranks):
    print("\n--- STEP 5: Calendars and Floats ---")
    n_nodes = graph.shape[0]
    omega = n_nodes - 1
    topo_order = [v for v, _ in sorted(ranks.items(), key=lambda x: (x[1], x[0]))]

    # Earliest dates (Forward pass)
    earliest = np.zeros(n_nodes, dtype=int)
    for u in topo_order:
        for v in range(n_nodes):
            if not np.isinf(graph[u][v]):
                w = int(graph[u][v])
                if earliest[u] + w > earliest[v]:
                    earliest[v] = earliest[u] + w

    # Latest dates (Backward pass)
    latest = np.full(n_nodes, earliest[omega], dtype=int)
    for u in reversed(topo_order):
        for v in range(n_nodes):
            if not np.isinf(graph[u][v]):
                w = int(graph[u][v])
                if latest[v] - w < latest[u]:
                    latest[u] = latest[v] - w

    # Total float & Free float
    total_float = latest - earliest
    free_float = np.zeros(n_nodes, dtype=int)
    for u in range(n_nodes):
        succs = [v for v in range(n_nodes) if not np.isinf(graph[u][v])]
        if succs:
            free_float[u] = min(
                earliest[v] - earliest[u] - int(graph[u][v]) for v in succs
            )

    header = (
        f"{'Vertex':<8} | {'Rank':<6} | {'Earliest':<10} | "
        f"{'Latest':<10} | {'Total Float':<12} | {'Free Float':<10}"
    )
    print(header)
    print("-" * len(header))
    for v in topo_order:
        print(
            f"{v:<8} | {ranks[v]:<6} | {earliest[v]:<10} | "
            f"{latest[v]:<10} | {total_float[v]:<12} | {free_float[v]:<10}"
        )

    # Step 6: Critical Path(s)
    print("\n--- STEP 6: Critical Path(s) ---")
    paths = []

    def dfs(u, path):
        if u == omega:
            paths.append(list(path))
            return
        for v in range(n_nodes):
            if not np.isinf(graph[u][v]):
                w = int(graph[u][v])
                if (
                    total_float[u] == 0
                    and total_float[v] == 0
                    and earliest[u] + w == earliest[v]
                ):
                    path.append(v)
                    dfs(v, path)
                    path.pop()

    dfs(0, [0])
    print(f"Minimum Project Duration: {earliest[omega]}")
    for idx, p in enumerate(paths, 1):
        print(f"Critical Path {idx}: {' -> '.join(map(str, p))}")


# --- MAIN LOOP ---
files_folder = "Test files-20261124"

while True:
    filepath = choose_table(files_folder)
    if filepath is None:
        print("Exiting program.")
        break

    graph = build_graph(filepath)
    display_matrix(graph)

    if check_scheduling_graph(graph):
        ranks = compute_ranks(graph)
        compute_calendars_and_critical_paths(graph, ranks)

    again = input("\nTest another constraint table? (y/n): ").strip().lower()
    if again not in ("y", "yes"):
        print("Exiting program.")
        break