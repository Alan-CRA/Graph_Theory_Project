
import os


# ==========================================
# STEP 1: CHOOSE A CONSTRAINT TABLE
# ==========================================

def choose_table():

    folder = "Test files-20261124"

    while True:

        choice = input(
            "\nEnter table number (1-14) or q to quit: "
        ).strip()

        if choice.lower() in ["q", "quit", "exit"]:
            return None

        if choice.isdigit():

            number = int(choice)

            if 1 <= number <= 14:

                filename = os.path.join(
                    folder, f"table {number}.txt"
                )

                if os.path.isfile(filename):
                    return filename

                else:
                    print("Table file not found.")

            else:
                print("Please enter a number between 1 and 14.")

        else:
            print("Invalid input. Enter a number or q.")


# ==========================================
# STEP 2: READ THE FILE AND BUILD THE GRAPH
# ==========================================

def build_graph(filename):

    tasks = []

    with open(filename, "r", encoding="utf-8") as file:

        expected_id = 1

        for line in file:

            if not line.strip():
                continue

            numbers = list(map(int, line.split()))

            if len(numbers) < 2:
                raise ValueError("A task is missing its duration.")

            task_id = numbers[0]
            duration = numbers[1]
            predecessors = numbers[2:]

            if task_id != expected_id:
                raise ValueError("Task numbers must be consecutive.")

            if duration < 0:
                raise ValueError("Negative duration is not allowed.")

            if len(predecessors) != len(set(predecessors)):
                raise ValueError("Duplicate predecessor.")

            tasks.append([duration, predecessors])

            expected_id += 1

    if len(tasks) == 0:
        raise ValueError("The file is empty.")

    n = len(tasks)

    # Vertex 0 = project beginning
    # Vertex n+1 = project ending

    omega = n + 1
    number_of_vertices = n + 2

    # None means that there is no edge
    graph = [
        [None for j in range(number_of_vertices)]
        for i in range(number_of_vertices)
    ]

    has_successor = [False] * (n + 1)

    print("\n========== STEP 1: BUILDING THE GRAPH ==========")

    edges = []

    for i in range(n):

        task = i + 1
        duration = tasks[i][0]
        predecessors = tasks[i][1]

        # Check predecessors
        for p in predecessors:

            if p < 1 or p > n:
                raise ValueError("Invalid predecessor.")

            if p == task:
                raise ValueError("A task cannot depend on itself.")

        # Task without predecessors
        if len(predecessors) == 0:

            graph[0][task] = 0
            edges.append((0, task, 0))

        # Task with predecessors
        else:

            for p in predecessors:

                weight = tasks[p - 1][0]

                graph[p][task] = weight

                has_successor[p] = True

                edges.append((p, task, weight))

    # Connect tasks without successors to omega

    for task in range(1, n + 1):

        if not has_successor[task]:

            weight = tasks[task - 1][0]

            graph[task][omega] = weight

            edges.append((task, omega, weight))

    print("Number of vertices:", number_of_vertices)
    print("Number of edges:", len(edges))

    for u, v, weight in sorted(edges):

        print(u, "->", v, "=", weight)

    return graph


# ==========================================
# STEP 3: DISPLAY THE VALUE MATRIX
# ==========================================

def display_matrix(graph):

    print("\n========== STEP 2: VALUE MATRIX ==========")

    n = len(graph)

    print("     ", end="")

    for j in range(n):
        print(f"{j:>5}", end="")

    print()

    for i in range(n):

        print(f"{i:>3} |", end="")

        for j in range(n):

            if graph[i][j] is None:
                print(f"{'*':>5}", end="")

            else:
                print(f"{graph[i][j]:>5}", end="")

        print()


# ==========================================
# STEP 4: CHECK GRAPH PROPERTIES
# ==========================================

def check_graph(graph):

    print("\n========== STEP 3: GRAPH VALIDATION ==========")

    n = len(graph)

    valid = True

    # Calculate incoming and outgoing degrees

    incoming = [0] * n
    outgoing = [0] * n

    for i in range(n):

        for j in range(n):

            if graph[i][j] is not None:

                outgoing[i] += 1
                incoming[j] += 1

    # Check entry point

    entries = []

    for i in range(n):

        if incoming[i] == 0:
            entries.append(i)

    if entries == [0]:

        print("There is one entry point: 0")

    else:

        print("ERROR: Entry points:", entries)
        valid = False

    # Check exit point

    exits = []

    for i in range(n):

        if outgoing[i] == 0:
            exits.append(i)

    if exits == [n - 1]:

        print("There is one exit point:", n - 1)

    else:

        print("ERROR: Exit points:", exits)
        valid = False

    # --------------------------------------
    # CYCLE DETECTION
    # Method of eliminating entry points
    # --------------------------------------

    print("\nDetecting cycles...")

    remaining = set(range(n))

    degree = incoming.copy()

    ranks = {}

    rank = 0

    while remaining:

        # Find vertices with zero incoming degree

        entry_points = []

        for v in sorted(remaining):

            if degree[v] == 0:
                entry_points.append(v)

        # If no entry point exists, there is a cycle

        if len(entry_points) == 0:

            print("No entry points available.")
            print("Remaining vertices:", sorted(remaining))
            print("A cycle has been detected.")

            valid = False
            break

        print("Entry points:", entry_points)

        # Assign the same rank to these vertices

        for u in entry_points:

            ranks[u] = rank

        # Eliminate these vertices

        for u in entry_points:

            remaining.remove(u)

            for v in range(n):

                if graph[u][v] is not None:
                    degree[v] -= 1

        print("Remaining vertices:", sorted(remaining))

        rank += 1

    if len(remaining) == 0:

        print("There is no cycle.")

    # --------------------------------------
    # CHECK OUTGOING EDGE WEIGHTS
    # --------------------------------------

    same_weights = True

    for u in range(n):

        weights = []

        for v in range(n):

            if graph[u][v] is not None:
                weights.append(graph[u][v])

        if len(weights) > 1:

            if len(set(weights)) > 1:

                print("ERROR: Different outgoing weights at", u)
                same_weights = False

    if same_weights:

        print("Outgoing weights are the same for each vertex.")

    else:

        valid = False

    # --------------------------------------
    # CHECK WEIGHTS FROM VERTEX 0
    # --------------------------------------

    entry_weights = []

    for v in range(n):

        if graph[0][v] is not None:
            entry_weights.append(graph[0][v])

    if all(weight == 0 for weight in entry_weights):

        print("Outgoing edges of vertex 0 have weight 0.")

    else:

        print("ERROR: Outgoing weights from vertex 0 are not zero.")
        valid = False

    # --------------------------------------
    # CHECK NEGATIVE EDGES
    # --------------------------------------

    negative = False

    for i in range(n):

        for j in range(n):

            if graph[i][j] is not None:

                if graph[i][j] < 0:
                    negative = True

    if not negative:

        print("There are no negative edges.")

    else:

        print("ERROR: Negative edges detected.")
        valid = False

    # Final result

    if valid:

        print("\nThis is a valid scheduling graph.")

    else:

        print("\nThis is NOT a valid scheduling graph.")

    return valid, ranks


# ==========================================
# STEP 5: CALCULATE EARLIEST AND LATEST DATES
# ==========================================

def calculate_calendars(graph, ranks):

    print("\n========== STEP 4: CALCULATING RANKS ==========")

    n = len(graph)

    # Sort vertices by rank

    order = sorted(ranks, key=lambda v: (ranks[v], v))

    for v in order:

        print("Vertex:", v, " Rank:", ranks[v])

    # --------------------------------------
    # EARLIEST DATES: FORWARD PASS
    # --------------------------------------

    print("\n========== EARLIEST DATES ==========")

    earliest = [0] * n

    for u in order:

        for v in range(n):

            if graph[u][v] is not None:

                weight = graph[u][v]

                new_date = earliest[u] + weight

                if new_date > earliest[v]:

                    earliest[v] = new_date

    # --------------------------------------
    # LATEST DATES: BACKWARD PASS
    # --------------------------------------

    print("\n========== LATEST DATES ==========")

    omega = n - 1

    project_duration = earliest[omega]

    latest = [project_duration] * n

    for u in reversed(order):

        for v in range(n):

            if graph[u][v] is not None:

                weight = graph[u][v]

                new_date = latest[v] - weight

                if new_date < latest[u]:

                    latest[u] = new_date

    # --------------------------------------
    # CALCULATE TOTAL FLOAT
    # --------------------------------------

    total_float = [0] * n

    for i in range(n):

        total_float[i] = latest[i] - earliest[i]

    # --------------------------------------
    # CALCULATE FREE FLOAT
    # --------------------------------------

    free_float = [0] * n

    for u in range(n):

        successors = []

        for v in range(n):

            if graph[u][v] is not None:
                successors.append(v)

        if len(successors) > 0:

            values = []

            for v in successors:

                value = (
                    earliest[v]
                    - earliest[u]
                    - graph[u][v]
                )

                values.append(value)

            free_float[u] = min(values)

    # --------------------------------------
    # DISPLAY RESULTS
    # --------------------------------------

    print("\n========== CALENDAR RESULTS ==========")

    print(
        f"{'Vertex':<10}"
        f"{'Rank':<10}"
        f"{'Earliest':<12}"
        f"{'Latest':<12}"
        f"{'Total Float':<14}"
        f"{'Free Float':<12}"
    )

    for v in order:

        print(
            f"{v:<10}"
            f"{ranks[v]:<10}"
            f"{earliest[v]:<12}"
            f"{latest[v]:<12}"
            f"{total_float[v]:<14}"
            f"{free_float[v]:<12}"
        )

    return earliest, latest, total_float


# ==========================================
# STEP 6: FIND CRITICAL PATHS
# ==========================================

def find_critical_paths(graph, earliest, total_float):

    print("\n========== STEP 5: CRITICAL PATHS ==========")

    n = len(graph)

    omega = n - 1

    paths = []

    # Depth First Search

    def dfs(current, path):

        # If we reach the final vertex,
        # we have found a complete critical path

        if current == omega:

            paths.append(path.copy())
            return

        # Explore all successors

        for next_vertex in range(n):

            weight = graph[current][next_vertex]

            if weight is not None:

                # Check whether the edge is critical

                if (
                    total_float[current] == 0
                    and total_float[next_vertex] == 0
                    and earliest[current] + weight
                    == earliest[next_vertex]
                ):

                    path.append(next_vertex)

                    dfs(next_vertex, path)

                    # Backtracking

                    path.pop()

    # Start from vertex 0

    dfs(0, [0])

    print("Minimum project duration:", earliest[omega])

    if len(paths) == 0:

        print("No critical path found.")

    else:

        for i, path in enumerate(paths, start=1):

            print("Critical path", i, ":", " -> ".join(
                map(str, path)
            ))


# ==========================================
# MAIN PROGRAM
# ==========================================

def main():

    print("===================================")
    print("       PROJECT SCHEDULING")
    print("===================================")

    while True:

        filename = choose_table()

        if filename is None:

            print("Program finished.")
            break

        try:

            # Step 1: Build graph

            graph = build_graph(filename)

            # Step 2: Display matrix

            display_matrix(graph)

            # Step 3: Validate graph

            valid, ranks = check_graph(graph)

            # Continue only if graph is valid

            if valid:

                # Step 4 and 5: Calculate calendars

                earliest, latest, total_float = (
                    calculate_calendars(graph, ranks)
                )

                # Step 6: Find critical paths

                find_critical_paths(
                    graph,
                    earliest,
                    total_float
                )

        except (ValueError, OSError) as error:

            print("\nERROR:", error)

        # Ask whether the user wants another table

        answer = input(
            "\nDo you want to test another table? (y/n): "
        ).strip().lower()

        if answer not in ["y", "yes"]:

            print("Program finished.")
            break


# Start the program

if __name__ == "__main__":

    main()
