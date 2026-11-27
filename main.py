
import os


# ==================================================
# STEP 1: CHOOSE A CONSTRAINT TABLE
# ==================================================

def choose_table():

    folder = "Test files-20261124"

    while True:

        choice = input(
            "\nEnter table number (1-14) or q to quit: "
        ).strip()

        if choice.lower() in ["q", "quit", "exit"]:
            return None

        if not choice.isdigit():
            print("Invalid input. Enter a number between 1 and 14.")
            continue

        number = int(choice)

        if number < 1 or number > 14:
            print("Please enter a number between 1 and 14.")
            continue

        filename = os.path.join(
            folder, f"table {number}.txt"
        )

        if os.path.isfile(filename):
            return filename

        print("Table file not found:", filename)


# ==================================================
# STEP 2: READ THE CONSTRAINT TABLE AND BUILD GRAPH
# ==================================================

def build_graph(filename):

    tasks = []

    # Read the constraint table

    with open(filename, "r", encoding="utf-8") as file:

        expected_id = 1

        for line_number, line in enumerate(file, start=1):

            if not line.strip():
                continue

            try:
                numbers = list(map(int, line.split()))

            except ValueError:
                raise ValueError(
                    f"Invalid number on line {line_number}."
                )

            # Check that task number and duration exist

            if len(numbers) < 2:
                raise ValueError(
                    f"Missing duration on line {line_number}."
                )

            task_id = numbers[0]
            duration = numbers[1]
            predecessors = numbers[2:]

            # Check task numbering

            if task_id != expected_id:
                raise ValueError(
                    f"Expected task {expected_id}, "
                    f"but found task {task_id}."
                )

            # Check duration

            if duration < 0:
                raise ValueError(
                    f"Negative duration for task {task_id}."
                )

            # Check duplicate predecessors

            if len(predecessors) != len(set(predecessors)):
                raise ValueError(
                    f"Duplicate predecessor for task {task_id}."
                )

            tasks.append([duration, predecessors])

            expected_id += 1

    # Check empty file

    if len(tasks) == 0:
        raise ValueError("The constraint table is empty.")

    n = len(tasks)

    # --------------------------------------------------
    # DISPLAY THE ORIGINAL CONSTRAINT TABLE
    # --------------------------------------------------

    print("\n========== STEP 1: CONSTRAINT TABLE ==========")

    print(
        f"{'Task':<10}"
        f"{'Duration':<12}"
        f"Predecessors"
    )

    for i in range(n):

        task = i + 1
        duration = tasks[i][0]
        predecessors = tasks[i][1]

        print(
            f"{task:<10}"
            f"{duration:<12}"
            f"{predecessors if predecessors else 'None'}"
        )

    # --------------------------------------------------
    # CREATE FICTITIOUS VERTICES
    # --------------------------------------------------

    # Vertex 0 = Beginning of project
    # Vertex N+1 = End of project

    omega = n + 1

    number_of_vertices = n + 2

    # --------------------------------------------------
    # CREATE VALUE MATRIX
    # --------------------------------------------------

    # None means that there is no edge

    graph = [
        [None for j in range(number_of_vertices)]
        for i in range(number_of_vertices)
    ]

    # Track tasks that have successors

    has_successor = [False] * (n + 1)

    print("\n========== BUILDING THE SCHEDULING GRAPH ==========")

    edges = []

    # --------------------------------------------------
    # CREATE EDGES BETWEEN TASKS
    # --------------------------------------------------

    for i in range(n):

        task = i + 1

        duration = tasks[i][0]

        predecessors = tasks[i][1]

        # Check predecessors

        for p in predecessors:

            if p < 1 or p > n:
                raise ValueError(
                    f"Invalid predecessor {p} for task {task}."
                )

            if p == task:
                raise ValueError(
                    f"Task {task} cannot depend on itself."
                )

        # CASE 1: Task without predecessors

        if len(predecessors) == 0:

            graph[0][task] = 0

            edges.append((0, task, 0))

        # CASE 2: Task with predecessors

        else:

            for p in predecessors:

                # Weight = duration of predecessor

                weight = tasks[p - 1][0]

                graph[p][task] = weight

                has_successor[p] = True

                edges.append((p, task, weight))

    # --------------------------------------------------
    # CONNECT FINAL TASKS TO OMEGA
    # --------------------------------------------------

    for task in range(1, n + 1):

        if not has_successor[task]:

            weight = tasks[task - 1][0]

            graph[task][omega] = weight

            edges.append((task, omega, weight))

    # --------------------------------------------------
    # DISPLAY ALL EDGES
    # --------------------------------------------------

    print("\nNumber of vertices:", number_of_vertices)

    print("Number of edges:", len(edges))

    print("\nGraph edges:")

    for u, v, weight in sorted(edges):

        print(u, "->", v, "=", weight)

    return graph


# ==================================================
# STEP 2: DISPLAY THE VALUE MATRIX
# ==================================================

def display_matrix(graph):

    print("\n========== STEP 2: VALUE MATRIX ==========")

    n = len(graph)

    # Display column headings

    print("     ", end="")

    for j in range(n):

        print(f"{j:>5}", end="")

    print()

    print("-" * (5 * n + 5))

    # Display matrix rows

    for i in range(n):

        print(f"{i:>3} |", end="")

        for j in range(n):

            if graph[i][j] is None:

                print(f"{'*':>5}", end="")

            else:

                print(f"{graph[i][j]:>5}", end="")

        print()


# ==================================================
# STEP 3: CHECK SCHEDULING GRAPH PROPERTIES
# ==================================================

def check_graph(graph):

    print("\n========== STEP 3: GRAPH VALIDATION ==========")

    n = len(graph)

    valid = True

    # --------------------------------------------------
    # CALCULATE INCOMING AND OUTGOING DEGREES
    # --------------------------------------------------

    incoming = [0] * n

    outgoing = [0] * n

    for i in range(n):

        for j in range(n):

            if graph[i][j] is not None:

                outgoing[i] += 1

                incoming[j] += 1

    # --------------------------------------------------
    # CHECK SINGLE ENTRY POINT
    # --------------------------------------------------

    entries = []

    for i in range(n):

        if incoming[i] == 0:

            entries.append(i)

    if entries == [0]:

        print("There is one entry point: 0")

    else:

        print("ERROR: Entry points:", entries)

        valid = False

    # --------------------------------------------------
    # CHECK SINGLE EXIT POINT
    # --------------------------------------------------

    exits = []

    for i in range(n):

        if outgoing[i] == 0:

            exits.append(i)

    if exits == [n - 1]:

        print("There is one exit point:", n - 1)

    else:

        print("ERROR: Exit points:", exits)

        valid = False

    # --------------------------------------------------
    # DETECT CYCLES AND CALCULATE RANKS
    # METHOD OF ELIMINATING ENTRY POINTS
    # --------------------------------------------------

    print("\nDetecting cycles using elimination of entry points...")

    remaining = set(range(n))

    degree = incoming.copy()

    ranks = {}

    rank = 0

    while remaining:

        entry_points = []

        # Find vertices with zero incoming degree

        for v in sorted(remaining):

            if degree[v] == 0:

                entry_points.append(v)

        # No entry point means a cycle exists

        if len(entry_points) == 0:

            print("Entry points: None")

            print(
                "Remaining vertices:",
                sorted(remaining)
            )

            print("A cycle has been detected.")

            valid = False

            break

        print("Entry points:", entry_points)

        # Assign ranks

        for u in entry_points:

            ranks[u] = rank

        # Eliminate entry points

        for u in entry_points:

            remaining.remove(u)

            # Remove their outgoing edges

            for v in range(n):

                if graph[u][v] is not None:

                    degree[v] -= 1

        if remaining:

            print("Remaining vertices:", sorted(remaining))

        else:

            print("Remaining vertices: None")

        rank += 1

    if len(remaining) == 0:

        print("There is no cycle.")

    # --------------------------------------------------
    # CHECK SAME OUTGOING EDGE WEIGHTS
    # --------------------------------------------------

    print("\nChecking outgoing edge weights...")

    same_weights = True

    for u in range(n):

        weights = []

        for v in range(n):

            if graph[u][v] is not None:

                weights.append(graph[u][v])

        if len(weights) > 1:

            if len(set(weights)) > 1:

                print(
                    "ERROR: Vertex",
                    u,
                    "has different outgoing weights:",
                    weights
                )

                same_weights = False

    if same_weights:

        print("All outgoing edges of each vertex have the same weight.")

    else:

        valid = False

    # --------------------------------------------------
    # CHECK OUTGOING EDGES OF VERTEX 0
    # --------------------------------------------------

    print("\nChecking outgoing edges of vertex 0...")

    entry_weights = []

    for v in range(n):

        if graph[0][v] is not None:

            entry_weights.append(graph[0][v])

    if all(weight == 0 for weight in entry_weights):

        print("All outgoing edges of vertex 0 have weight 0.")

    else:

        print("ERROR: Outgoing edges of vertex 0 are not all zero.")

        valid = False

    # --------------------------------------------------
    # CHECK NEGATIVE EDGES
    # --------------------------------------------------

    print("\nChecking negative edge weights...")

    negative = False

    for i in range(n):

        for j in range(n):

            if graph[i][j] is not None:

                if graph[i][j] < 0:

                    negative = True

    if not negative:

        print("There are no negative-weight edges.")

    else:

        print("ERROR: Negative-weight edges detected.")

        valid = False

    # --------------------------------------------------
    # FINAL VALIDATION RESULT
    # --------------------------------------------------

    if valid:

        print("\nThis is a valid scheduling graph.")

    else:

        print("\nThis is NOT a valid scheduling graph.")

    return valid, ranks


# ==================================================
# STEP 4 AND 5: RANKS AND CALENDARS
# ==================================================

def calculate_calendars(graph, ranks):

    n = len(graph)

    print("\n========== STEP 4: VERTEX RANKS ==========")

    # Sort vertices according to their ranks

    order = sorted(
        ranks,
        key=lambda v: (ranks[v], v)
    )

    print(f"{'Vertex':<12}{'Rank':<10}")

    print("-" * 22)

    for v in order:

        print(f"{v:<12}{ranks[v]:<10}")

    # --------------------------------------------------
    # EARLIEST DATES: FORWARD PASS
    # --------------------------------------------------

    print("\n========== STEP 5: EARLIEST DATES ==========")

    earliest = [0] * n

    for u in order:

        for v in range(n):

            if graph[u][v] is not None:

                weight = graph[u][v]

                new_date = earliest[u] + weight

                if new_date > earliest[v]:

                    earliest[v] = new_date

                    print(
                        f"Updating vertex {v}: "
                        f"{earliest[v]}"
                    )

    print("Earliest dates:", earliest)

    # --------------------------------------------------
    # LATEST DATES: BACKWARD PASS
    # --------------------------------------------------

    print("\n========== LATEST DATES ==========")

    omega = n - 1

    # Project end latest date = earliest project end date

    project_duration = earliest[omega]

    latest = [project_duration] * n

    for u in reversed(order):

        for v in range(n):

            if graph[u][v] is not None:

                weight = graph[u][v]

                new_date = latest[v] - weight

                if new_date < latest[u]:

                    latest[u] = new_date

                    print(
                        f"Updating vertex {u}: "
                        f"{latest[u]}"
                    )

    print("Latest dates:", latest)

    # --------------------------------------------------
    # CALCULATE TOTAL FLOAT
    # --------------------------------------------------

    print("\n========== TOTAL FLOAT ==========")

    total_float = [0] * n

    for i in range(n):

        total_float[i] = latest[i] - earliest[i]

    print("Total floats:", total_float)

    # --------------------------------------------------
    # CALCULATE FREE FLOAT
    # --------------------------------------------------

    print("\n========== FREE FLOAT ==========")

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

    print("Free floats:", free_float)

    # --------------------------------------------------
    # DISPLAY COMPLETE CALENDAR
    # --------------------------------------------------

    print("\n========== CALENDAR RESULTS ==========")

    print(
        f"{'Vertex':<10}"
        f"{'Rank':<10}"
        f"{'Earliest':<12}"
        f"{'Latest':<12}"
        f"{'Total Float':<14}"
        f"{'Free Float':<12}"
    )

    print("-" * 70)

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


# ==================================================
# STEP 6: FIND ALL CRITICAL PATHS
# ==================================================

def find_critical_paths(graph, earliest, total_float):

    print("\n========== STEP 6: CRITICAL PATHS ==========")

    n = len(graph)

    omega = n - 1

    paths = []

    # --------------------------------------------------
    # DEPTH FIRST SEARCH
    # --------------------------------------------------

    def dfs(current, path):

        # Stop when the final vertex is reached

        if current == omega:

            paths.append(path.copy())

            return

        # Explore all successors

        for next_vertex in range(n):

            weight = graph[current][next_vertex]

            if weight is not None:

                # Check whether the edge belongs
                # to a critical path

                if (
                    total_float[current] == 0
                    and total_float[next_vertex] == 0
                    and earliest[current] + weight
                    == earliest[next_vertex]
                ):

                    path.append(next_vertex)

                    print(
                        "Following critical edge:",
                        current,
                        "->",
                        next_vertex
                    )

                    dfs(next_vertex, path)

                    # Backtracking

                    path.pop()

    # Start searching from vertex 0

    dfs(0, [0])

    print(
        "\nMinimum project duration:",
        earliest[omega]
    )

    if len(paths) == 0:

        print("No critical path found.")

    else:

        for i, path in enumerate(paths, start=1):

            print(
                "Critical Path",
                i,
                ":",
                " -> ".join(map(str, path))
            )


# ==================================================
# MAIN PROGRAM
# ==================================================

def main():

    print("======================================")

    print("         PROJECT SCHEDULING")

    print("======================================")

    while True:

        # Choose a constraint table

        filename = choose_table()

        if filename is None:

            print("Exiting program.")

            break

        try:

            # STEP 1: BUILD GRAPH

            graph = build_graph(filename)

            # STEP 2: DISPLAY VALUE MATRIX

            display_matrix(graph)

            # STEP 3: CHECK GRAPH PROPERTIES

            valid, ranks = check_graph(graph)

            # Continue only if the graph is valid

            if valid:

                # STEP 4 AND 5: RANKS AND CALENDARS

                earliest, latest, total_float = (
                    calculate_calendars(graph, ranks)
                )

                # STEP 6: CRITICAL PATHS

                find_critical_paths(
                    graph,
                    earliest,
                    total_float
                )

        except (ValueError, OSError) as error:

            print("\nERROR:", error)

        # Ask user to test another table

        answer = input(
            "\nDo you want to test another table? (y/n): "
        ).strip().lower()

        if answer not in ["y", "yes"]:

            print("Exiting program.")

            break


# ==================================================
# START THE PROGRAM
# ==================================================

if __name__ == "__main__":

    main()
