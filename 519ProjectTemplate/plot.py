import matplotlib.pyplot as plt
import numpy as np
import csv

def plotSingleResult(parametername, arrparam, arr_numberofnodes):
    data = np.array_split(arrparam, len(arr_numberofnodes))
    fig = plt.figure(figsize =(10, 7))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xticklabels(arr_numberofnodes)
    ax.set_xlabel('Number of Nodes')
    ax.set_ylabel(parametername)
    ax.boxplot(data)
    plt.show()


def plotResults():    
    arr_nodecount = []
    arr_compiletime = []
    arr_keygenerationtime = []
    arr_encryptiontime = []
    arr_executiontime = []
    arr_decryptiontime = []
    arr_referenceexecutiontime = []
    arr_mse = []
    
    filename = open('results.csv', 'r')
    file = csv.DictReader(filename)
    
    # iterating over each row and append values
    for col in file:
        arr_compiletime.append(float(col['CompileTime']))
        arr_keygenerationtime.append(float(col['KeyGenerationTime']))
        arr_encryptiontime.append(float(col['EncryptionTime']))
        arr_executiontime.append(float(col['ExecutionTime']))
        arr_decryptiontime.append(float(col['DecryptionTime']))
        arr_referenceexecutiontime.append(float(col['ReferenceExecutionTime']))
        arr_mse.append(float(col['Mse']))
        if int(col['SimCnt']) == 0:
            arr_nodecount.append(int(col['NodeCount']))
                             
    plotSingleResult("Compile Time", arr_compiletime,arr_nodecount)
    plotSingleResult("Key Generation Time", arr_keygenerationtime, arr_nodecount)
    plotSingleResult("Encryption Time", arr_encryptiontime, arr_nodecount)
    plotSingleResult("Execution Time", arr_executiontime, arr_nodecount)
    plotSingleResult("Decryption Time", arr_decryptiontime, arr_nodecount)
    plotSingleResult("Reference Execution Time", arr_referenceexecutiontime, arr_nodecount)
    plotSingleResult("MSE", arr_mse, arr_nodecount) 