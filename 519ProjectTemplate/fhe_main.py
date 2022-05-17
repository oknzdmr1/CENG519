from eva import EvaProgram, Input, Output, evaluate
from eva.ckks import CKKSCompiler
from eva.seal import generate_keys
from eva.metric import valuation_mse
import timeit
import networkx as nx
from random import random
import matplotlib.pyplot as plt
import numpy as np
from plot import plotResults
from DFS import iterativeDFS


vector_size = 4096
numberofnodes = 0
stack = []
responded = []
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
    GG = generateGraph(n,3,0.5)
    graph, graphdict = serializeGraphZeroOne(GG,m)
    printGraph(graph,n)
    input['Graph'] = graph
    return input, graph

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

def FindNodes2Check(graph, currentnode, numberofnodes):
    nodes2check = []
    for i in range(vector_size):
        nodes2check.append(0) 

    index = 0
    for i in range(numberofnodes):
        if not visited[i]:
            if stack.count(i) == 0:
                #print("Nodes to check: " + str(currentnode * numberofnodes + i))
                newlist = accessElement(graph, currentnode * numberofnodes + i, index)
                nodes2check = nodes2check + newlist
                index = index + 1

    return nodes2check

# This is the dummy analytic service
# You will implement this service based on your selected algorithm
# you can other parameters using global variables !!! do not change the signature of this function
# 
# Note that you cannot compute everything using EVA/CKKS
# For instance, comparison is not possible
# You can add, subtract, multiply, negate, shift right/left
# You will have to implement an interface with the trusted entity for comparison (send back the encrypted values, push the trusted entity to compare and get the comparison output)
def graphanalticprogram(graph):

    print("********************************")
    global firstpass
    global finished
    global numberofnodes
    global responded
    global stack
    global visited

    if firstpass:
        #print("First Pass")
        firstpass = False
        stack.append(0)
        nodes2check = FindNodes2Check(graph, 0, numberofnodes)
        return nodes2check

    if not firstpass:
        currentnode = stack[-1]
        
        print("Stack:" + str(stack))
        if not visited[currentnode]:
            visited[currentnode] = True
            #print("Visited:" + str(currentnode))
            result.append(currentnode)
            stack.pop()
        
        
        #print("Response" + str(responded))
        #print("visited: " + str(visited)) 

        index = 0
        for i in range(numberofnodes):
            #print("***Checking Node: " + str(i))
            if not visited[i]:
                #print("not visited: ")
                if stack.count(i) == 0:
                    #print("not in the stack: ")
                    index = index + 1
                    if responded[index-1]:
                        #print("Adding to stack: "+ str(i))
                        stack.append(i)

        if len(stack):
            finished = True
            print(result)
            return result                  

        nodes2check = FindNodes2Check(graph, currentnode, numberofnodes)
        return nodes2check

        

    
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
    m = vector_size
    print("Will start simulation for ", n)
    config = {}
    config['warn_vec_size'] = 'false'
    config['lazy_relinearize'] = 'true'
    config['rescaler'] = 'always'
    config['balance_reductions'] = 'true'
    inputs, g= prepareInput(n, m)

    iterativeDFS(g, 0, n)

    compiletime = 0
    keygenerationtime  = 0
    encryptiontime = 0
    executiontime = 0
    decryptiontime = 0
    referenceexecutiontime = 0
    mse = 0

    global finished
    global visited
    global numberofnodes
    global result
    global firstpass
    global responded

    numberofnodes = n
    firstpass = True
    finished = False
    result.clear()
    stack.clear()
    visited.clear()
    for i in range(numberofnodes):
        visited.append(False)

    counter = 0
    while not finished:

        graphanaltic = EvaProgramDriver("graphanaltic", vec_size=m,n=n)
        with graphanaltic:
            graph = Input('Graph')
            reval = graphanalticprogram(graph)
            Output('ReturnedValue', reval)
    
        prog = graphanaltic
        prog.set_output_ranges(30)
        prog.set_input_scales(30)

        start = timeit.default_timer()
        compiler = CKKSCompiler(config=config)
        compiled_multfunc, params, signature = compiler.compile(prog)
        compiletime += (timeit.default_timer() - start) * 1000.0 #ms

        start = timeit.default_timer()
        public_ctx, secret_ctx = generate_keys(params)
        keygenerationtime = (timeit.default_timer() - start) * 1000.0 #ms
    
        start = timeit.default_timer()
        encInputs = public_ctx.encrypt(inputs, signature)
        encryptiontime += (timeit.default_timer() - start) * 1000.0 #ms

        start = timeit.default_timer()
        encOutputs = public_ctx.execute(compiled_multfunc, encInputs)
        executiontime += (timeit.default_timer() - start) * 1000.0 #ms

        start = timeit.default_timer()
        outputs = secret_ctx.decrypt(encOutputs, signature)
        decryptiontime += (timeit.default_timer() - start) * 1000.0 #ms

        responded.clear()

        for key in outputs:
            for i in range(numberofnodes):
                #print(outputs[key][i])
                if (outputs[key][i] < 1.02) and (outputs[key][i] > 0.98):
                    responded.append(True)
                else:
                    responded.append(False)


        start = timeit.default_timer()
        reference = evaluate(compiled_multfunc, inputs)
        referenceexecutiontime += (timeit.default_timer() - start) * 1000.0 #ms

    # Change this if you want to output something or comment out the two lines below
    #for key in outputs:
    #    print(key, float(outputs[key][0]), float(reference[key][0]))

    #     for key in outputs:
    #         print(key+":")
    #         for i in range(len(outputs[key])):
    #             if i<10:
    #                 print(float(outputs[key][i]))    
 
        mse += valuation_mse(outputs, reference) # since CKKS does approximate computations, this is an important measure that depicts the amount of error

    return compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse
 


if __name__ == "__main__":
    simcnt = 10 #The number of simulation runs, set it to 3 during development otherwise you will wait for a long time
    # For benchmarking you must set it to a large number, e.g., 100
    #Note that file is opened in append mode, previous results will be kept in the file
    resultfile = open("results.csv", "w")  # Measurement results are collated in this file for you to plot later on
    resultfile.write("NodeCount,SimCnt,CompileTime,KeyGenerationTime,EncryptionTime,ExecutionTime,DecryptionTime,ReferenceExecutionTime,Mse\n")
    resultfile.close()
    
    print("Simulation campaing started:")

    for nc in range(8,40,4): # Node counts for experimenting various graph sizes
        n = nc

        resultfile = open("results.csv", "a") 
        for i in range(simcnt):
            #Call the simulator
            compiletime, keygenerationtime, encryptiontime, executiontime, decryptiontime, referenceexecutiontime, mse = simulate(n)
            res = str(n) + "," + str(i) + "," + str(compiletime) + "," + str(keygenerationtime) + "," +  str(encryptiontime) + "," +  str(executiontime) + "," +  str(decryptiontime) + "," +  str(referenceexecutiontime) + "," +  str(mse) + "\n"
            #res = str(n) + "," + str(i) + "," + "{:.5f}".format(compiletime) + "," + "{:.5f}".format(keygenerationtime) + "," +  "{:.5f}".format(encryptiontime) + "," +  "{:.5f}".format(executiontime) + "," +  "{:.5f}".format(decryptiontime) + "," +  "{:.5f}".format(referenceexecutiontime) + "," +  "{:.9f}".format(mse) + "\n"
            #print(res)
            resultfile.write(res)
            
        resultfile.close()

    plotResults()

    