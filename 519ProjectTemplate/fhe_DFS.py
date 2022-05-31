import math

vector_size = 2048
numberofnodes = 0
client_response = []

initialnode = 0
stack = []  
firstpass = True
finished = False
result = []
visited = []

# Calculate min required vector size 
def calculateMinVectorSize(inputsize):
    x = math.log(inputsize, 2)
    x = math.ceil(x)
    return 2**(x)


# Shift an element from 'inpos' position to 'outpos' position and mask all others
def accessElement(graph, inpos, outpos):
    dummyList = []
    for i in range(vector_size):
        if i == outpos:
            dummyList.append(1)
        else:
            dummyList.append(0)
        
    numberofshift = inpos - outpos
    reval = (graph<<numberofshift) * dummyList

    #print(str(inpos) + ", " + str(outpos) + ", " + str(numberofshift))
    return reval

# Decide if the node is a potential candidate for the next iteration. 
# If the node is not visited before and not in the stack, then requires checking if there is an edge or not
def isCheckingRequired(node):
    global stack
    global visited

    if not visited[node]: 
        if stack.count(node) == 0: 
            return True

    return False

def visitNode(currentnode):
    global visited
    global result
    global stack

    if not visited[currentnode]:
        visited[currentnode] = True
        result.append(currentnode)
        stack.pop()    


# Find all possible adjacent nodes of the current node to ask client if there is an edge or not
def findNodes2Check(graph, currentnode, numberofnodes):
    nodes2check = []
    for i in range(vector_size):
        nodes2check.append(0) 

    index = 0
    for i in range(numberofnodes):
        if isCheckingRequired(i):   # Add to list
            newlist = accessElement(graph, currentnode * numberofnodes + i, index)
            nodes2check = nodes2check + newlist
            index = index + 1
    
    numberofnodes2check = index
    return nodes2check, numberofnodes2check

    
def graphanalticprogram(graph):

    #print("********************************")
    global firstpass
    global finished
    global numberofnodes
    global client_response
    global stack
    global visited
    global initialnode

    if firstpass:
        firstpass = False
        stack.append(initialnode)
        nodes2check, length = findNodes2Check(graph, initialnode, numberofnodes)
        return nodes2check

    if not firstpass:
        
        currentnode = stack[-1]

        #print("Stack:" + str(stack))
        #print("Client Response:" + str(client_response))
        visitNode(currentnode)

        # add the adjacent vetices of the current vertex according to client answer
        index = 0
        for i in range(numberofnodes):
             if isCheckingRequired(i):
                if client_response[index]:
                    stack.append(i)
                index = index + 1    

        while True:
            # Stack empty. Either all vertices are visited or graph is disconnected. End of the DFS
            if len(stack) == 0:
                finished = True
                print("DFS Result with fhe: " + str(result)) 
                return graph 

            # Create a list to ask client if there is an edge or not
            currentnode = stack[-1]
            nodes2check, length = findNodes2Check(graph, currentnode, numberofnodes)
            
            # if there is no edge to ask, continue to iterate the stack
            if length == 0:
                visitNode(currentnode)
            else:
                break

        return nodes2check

# Refresh variable at the beginning of the each simulation
def refreshVariables():
    global firstpass
    global finished
    global result
    global stack
    global visited

    firstpass = True
    finished = False
    result.clear()
    stack.clear()
    visited.clear()

    for i in range(numberofnodes):
        visited.append(False)