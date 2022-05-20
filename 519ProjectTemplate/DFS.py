
# To check correctness of fhe_DFS
def iterativeDFS(graph, initialnode, numberofnodes):

    visited = []
    for i in range(numberofnodes):
        visited.append(False)

    stack = []
    stack.append(initialnode)

    result = []

    while len(stack):
        #print(stack)
        currentnode = stack[-1]
        stack.pop()

        if not visited[currentnode]:
            visited[currentnode] = True
            result.append(currentnode)
            #print(currentnode)

        for i in range(numberofnodes):
            if not visited[i]:
                if stack.count(i) == 0:
                    if graph[currentnode * numberofnodes + i] == 1:
                        stack.append(i)
    return result
    