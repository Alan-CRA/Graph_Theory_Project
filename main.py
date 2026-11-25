import numpy as np


def choose_table():
    table = 0
    while(table < 1 or table > 14):
        table = int(input("In wich table do you wanna work on? (choose a number between 1 and 14)   "))
    return table

files = "Test files-20261124"
while(True):
    table = choose_table()
    m = []
    with open(f"{files}/table {table}.txt") as f:
        for line in f:
            m.append(list(map(int,line.split()[1:])))
    n_nodes = len(m)+2
    graph = np.zeros((n_nodes,n_nodes))
    graph[:] = np.inf
    print(m)

    for task,values in enumerate(m):
        if len(values) == 1:
            graph[0][task+1] = 0
        else:
            predecessors = values[1:]
            for i in predecessors:
                graph[i][task+1] = m[i-1][0]
                
    print(graph)