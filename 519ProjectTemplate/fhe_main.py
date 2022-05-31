from eva import EvaProgram, Input, Output
import networkx as nx
from plot import plotResults
from evaCommon import evaCommon
import fhe_DFS

ERROR_MARGIN = 0.1


# Using networkx, generate a random graph
# You can change the way you generate the graph
def generateGraph(n, k, p):
    #ws = nx.cycle_graph(n)
    ws = nx.connected_watts_strogatz_graph(n,k,p)
    return ws

# If there is an edge between two vertices its weight is 1 otherwise it is zero
# You can change the weight assignment as required
# Two dimensional adjacency matrix is represented as a vector
# Assume there are n vertices
# (i,j)th element of the adjacency matrix corresponds to (i*n + j)th element in the vector representations
def serializeGraphZeroOne(GG,n,vec_size):
    #n = GG.size()
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
    #k = int(n/2)
    k = 3
    GG = generateGraph(n,k,0.5)
    graph, graphdict = serializeGraphZeroOne(GG,n,m)
    #printGraph(graph,n)
    input['Graph'] = graph
    return input, graph
  
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
    
    # vector size is adapted according to input/output size
    #m = fhe_DFS.vector_size = fhe_DFS.calculateMinVectorSize(n*n)

    m = fhe_DFS.vector_size
    fhe_DFS.numberofnodes = n

    print("Will start simulation for ", n)
    inputs, g= prepareInput(n, m)

    t_compiletime = t_keygenerationtime = t_encryptiontime = t_executiontime = t_decryptiontime = t_referenceexecutiontime = t_mse = 0

    numberofiteration = 0 # for debug purpose

    fhe_DFS.refreshVariables()

    # Run until fhe_DFS is finished. At every iteration server prepares a list to ask client if an edge exist or not. After the client response a new iteration begins
    while not fhe_DFS.finished:

        numberofiteration += 1

        graphanaltic = EvaProgramDriver("graphanaltic", vec_size=m, n=n)
        with graphanaltic:
            graph = Input('Graph')
            reval = fhe_DFS.graphanalticprogram(graph)
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

        fhe_DFS.client_response.clear()

        # Error Margin can be adopted according to eva parameters. Change in the Eva parameters may require yto change this error margin
        for key in outputs:
            for i in range(fhe_DFS.numberofnodes):
                if (outputs[key][i] < 1+ERROR_MARGIN) and (outputs[key][i] > 1-ERROR_MARGIN):
                    fhe_DFS.client_response.append(True)
                    #print(outputs[key][i])
                else:
                    fhe_DFS.client_response.append(False)

    #print(numberofiteration)

    print("Number of Iteration: " + str(numberofiteration))

    return t_compiletime, t_keygenerationtime, t_encryptiontime, t_executiontime, t_decryptiontime, t_referenceexecutiontime, t_mse
 

if __name__ == "__main__":
    simcnt = 100 #The number of simulation runs, set it to 3 during development otherwise you will wait for a long time
    # For benchmarking you must set it to a large number, e.g., 100
    #Note that file is opened in append mode, previous results will be kept in the file
    resultfile = open("results.csv", "w")  
    resultfile.write("NodeCount,SimCnt,CompileTime,KeyGenerationTime,EncryptionTime,ExecutionTime,DecryptionTime,ReferenceExecutionTime,Mse\n")
    resultfile.close()
    
    print("Simulation campaing started:")

    for nc in range(12,44,4): # Node counts for experimenting various graph sizes
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

    