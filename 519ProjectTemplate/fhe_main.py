from eva import EvaProgram, Input, Output
import networkx as nx
from random import random
import matplotlib.pyplot as plt
import numpy as np
from plot import plotResults
from DFS import iterativeDFS
from common import evaCommon
import math


ERROR_MARGIN = 0.1
vector_size = 4096
initialnode = 0
numberofnodes = 0
stack = []  
client_response = []
firstpass = True
finished = False
result = []
visited = []

# Using networkx, generate a random graph
# You can change the way you generate the graph
def generateGraph(n, k, p):
    #ws = nx.cycle_graph(n)
    ws = nx.watts_strogatz_graph(n,k,p)
    return ws

# If there is an edge between two vertices its weight is 1 otherwise it is zero
# You can change the weight assignment as required
# Two dimensional adjacency matrix is represented as a vector
# Assume there are n vertices
# (i,j)th element of the adjacency matrix corresponds to (i*n + j)th element in the vector representations
def serializeGraphZeroOne(GG,vec_size):
    n = GG.size()
    graphdict = {}
    g = []
    for row in range(n):
        for column in range(n):
            if GG.has_edge(row, column) or row==column: # I assumed the vertices are connected to themselves
                weight = 1
            else:
                weight = 0 
            g.append( weight  )  
            key = str(row)+'-'+str(column)
            graphdict[key] = [weight] # EVA requires str:listoffloat
    # EVA vector size has to be large, if the vector representation of the graph is smaller, fill the eva vector with zeros
    for i in range(vec_size - n*n): 
        g.append(0.0)
    return g, graphdict

# To display the generated graph
def printGraph(graph,n):
    for row in range(n):
        for column in range(n):
            print("{:.2f}".format(graph[row*n+column]), end = '\t')
        print() 

# Eva requires special input, this function prepares the eva input
# Eva will then encrypt them
def prepareInput(n, m):
    input = {}
    GG = generateGraph(n,3,0.6)
    graph, graphdict = serializeGraphZeroOne(GG,m)
    #printGraph(graph,n)
    input['Graph'] = graph
    return input, graph


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

# Decide if the node is a potential candidate for the next iterations
def isCheckingRequired(node):
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


# Find all possible adjacent nodes of the current node to ask client if there is an edge
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

# Calculate required vector size
def calculateVectorSize(inputsize):
    x = math.log(inputsize, 2)
    x = math.ceil(x)
    return 2**(x+1)
  
# Do not change this 
# the parameter n can be passed in the call from simulate function
class EvaProgramDriver(EvaProgram):
    def __init__(self, name, vec_size=4096, n=4):
        self.n = n
        super().__init__(name, vec_size)

    def __enter__(self):
        super().__enter__()

    def __exit__(self, exc_type, exc_value, traceback):
        super().__exit__(exc_type, exc_value, traceback)


# Repeat the experiments and show averages with confidence intervals
# You can modify the input parameters
# n is the number of nodes in your graph
# If you require additional parameters, add them
def simulate(n):
    
    global vector_size
    global initialnode

    # vector size is adapted according to input/output size
    m = vector_size = calculateVectorSize(n*n)
    #print("vector size: " + str(vector_size))

    print("Will start simulation for ", n)
    inputs, g= prepareInput(n, m)

    initialnode = 1 # select node to start

    result_nofhe = iterativeDFS(g, initialnode, n)
    print("DFS Result no fhe: " + str(result_nofhe)) 

    t_compiletime = t_keygenerationtime = t_encryptiontime = t_executiontime = t_decryptiontime = t_referenceexecutiontime = t_mse = 0

    #
    global finished
    global visited
    global numberofnodes
    global result
    global firstpass
    global client_response

    #prepare variables for fhe algorithm
    numberofnodes = n
    firstpass = True
    finished = False
    result.clear()
    stack.clear()
    visited.clear()

    for i in range(numberofnodes):
        visited.append(False)

    numberofiteration = 0 # for debug purpose

    # Run until DFS is finished. At every iteration server prepares a list to ask client if an edge exist or not. After the client response a new iteration begins
    while not finished:

        numberofiteration += 1

        graphanaltic = EvaProgramDriver("graphanaltic", vec_size=m,n=n)
        with graphanaltic:
            graph = Input('Graph')
            reval = graphanalticprogram(graph)
            Output('ReturnedValue', reval)
    
        prog = graphanaltic
        prog.set_output_ranges(25)
        prog.set_input_scales(25)

        outputs, compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse = evaCommon(prog, inputs)
        
        # Add the measurements of each iteration to find a total time or error value
        t_compiletime += compiletime
        t_keygenerationtime += keygenerationtime
        t_encryptiontime += encryptiontime
        t_executiontime += executiontime
        t_decryptiontime += decryptiontime
        t_referenceexecutiontime += referenceexecutiontime
        t_mse += mse

        client_response.clear()

        # Error Margin can be adopted according to eva parameters. Change in the Eva parameters may require yto change this error margin
        for key in outputs:
            for i in range(numberofnodes):
                if (outputs[key][i] < 1+ERROR_MARGIN) and (outputs[key][i] > 1-ERROR_MARGIN):
                    client_response.append(True)
                    #print(outputs[key][i])
                else:
                    client_response.append(False)

    #print(numberofiteration)
    if result_nofhe != result:
        print("FHE WRONG RESULT")

    return t_compiletime, t_keygenerationtime, t_encryptiontime, t_executiontime, t_decryptiontime, t_referenceexecutiontime, t_mse
 


if __name__ == "__main__":
    simcnt = 50 #The number of simulation runs, set it to 3 during development otherwise you will wait for a long time
    # For benchmarking you must set it to a large number, e.g., 100
    #Note that file is opened in append mode, previous results will be kept in the file
    resultfile = open("results.csv", "w")  
    resultfile.write("NodeCount,SimCnt,CompileTime,KeyGenerationTime,EncryptionTime,ExecutionTime,DecryptionTime,ReferenceExecutionTime,Mse\n")
    resultfile.close()
    
    print("Simulation campaing started:")

    for nc in range(12,60,4): # Node counts for experimenting various graph sizes
        n = nc

        resultfile = open("results.csv", "a") 
        for i in range(simcnt):
            #Call the simulator
            compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse = simulate(n)
            #res = str(n) + "," + str(i) + "," + str(compiletime) + "," + str(keygenerationtime) + "," +  str(encryptiontime) + "," +  str(executiontime) + "," +  str(decryptiontime) + "," +  str(referenceexecutiontime) + "," +  str(mse) + "\n"
            res = str(n) + "," + str(i) + "," + "{:.5f}".format(compiletime) + "," + "{:.5f}".format(keygenerationtime) + "," +  "{:.5f}".format(encryptiontime) + "," +  "{:.5f}".format(executiontime) + "," +  "{:.5f}".format(decryptiontime) + "," +  "{:.5f}".format(referenceexecutiontime) + "," +  "{:.9f}".format(mse) + "\n"
            print(res)
            resultfile.write(res)
            
        resultfile.close()

    plotResults()

    