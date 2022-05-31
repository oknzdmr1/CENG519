import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings

def plotSingleResult(ylabel, yaxis, xaxis):
    
    warnings.filterwarnings("ignore")

    fig = plt.figure(figsize =(10, 7))
    ax = fig.add_axes([0, 0, 1, 1])
    ax.set_xticklabels(xaxis)
    ax.set_xlabel('Number of Nodes')
    ax.set_ylabel(ylabel)
    ax.boxplot(yaxis)
    plt.show()


def readCsv(path):

    df = pd.read_csv(path)
    #print(df.keys())

    arr_nodecount = np.unique(df.NodeCount)

    # 2d arrays. Each row is a simulation values for a particular node count
    arr_compiletime = np.array_split(df.CompileTime, len(arr_nodecount))
    arr_keygenerationtime = np.array_split(df.KeyGenerationTime, len(arr_nodecount))
    arr_encryptiontime = np.array_split(df.EncryptionTime, len(arr_nodecount))
    arr_executiontime = np.array_split(df.ExecutionTime, len(arr_nodecount))
    arr_decryptiontime = np.array_split(df.DecryptionTime, len(arr_nodecount))
    arr_reference_execution_time = np.array_split(df.ReferenceExecutionTime, len(arr_nodecount))
    arr_mse = np.array_split(df.Mse, len(arr_nodecount))

    return arr_nodecount, arr_compiletime, arr_keygenerationtime, arr_encryptiontime, arr_executiontime, arr_decryptiontime, arr_reference_execution_time, arr_mse


def plotResults():    
    
    arr_nodecount, arr_compiletime, arr_keygenerationtime, arr_encryptiontime, arr_executiontime, arr_decryptiontime, arr_referenceexecutiontime, arr_mse = readCsv('results.csv')
                             
    plotSingleResult("Compile Time (ms)", arr_compiletime, arr_nodecount)
    plotSingleResult("Key Generation Time (ms)", arr_keygenerationtime, arr_nodecount)
    plotSingleResult("Encryption Time (ms)", arr_encryptiontime, arr_nodecount)
    plotSingleResult("Execution Time (ms)", arr_executiontime, arr_nodecount)
    plotSingleResult("Decryption Time (ms)", arr_decryptiontime, arr_nodecount)
    plotSingleResult("Reference Execution Time (ms)", arr_referenceexecutiontime, arr_nodecount)
    plotSingleResult("MSE", arr_mse, arr_nodecount) 


