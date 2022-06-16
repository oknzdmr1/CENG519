---
bibliography:
- references.bib
---

Encrypted Vector Arithmetic (EVA) is a general-purpose language which
offers Fully Homomorphic Encryption (FHE) in a less complex manner.
Since the homomorphic encryption is a newly developing area, most of the
algorithms addressing practical problems are still not widely
implemented. This paper presents an implementation of the Depth First
Search (DFS) algorithm using EVA language. The implementation is based
on the iterative version of the Depth First Search algorithm. Since the
comparison operation is not provided in EVA, vertices are discovered
with the help of the client.

Random graphs are created to simulate the implementation using
Watts--Strogatz graph model. As an input of the algorithm, the created
graph is converted to a serialized adjacency matrix. Since Homomorphic
Encryption accepts only power-of-two input size, additional zeros are
added to the end of the input sequence to make its size equal to a power
of two. The implementation is simulated with different graph sizes and a
hundred simulations are conducted for each graph size. At each
simulation, several parameters such as compile time, encryption time,
decryption time, key generation time, execution time, reference
execution time, and mean square error of the output values are measured.

Effects of two different parameters in the implementation are further
analyzed. The first parameter is input size. The measurements are
collected for two different approaches: constant input size and dynamic
input size. In the former, the size of the input is fixed to a constant
value regardless of the graph size, which is the minimum required
power-of-two value for the largest graph size. In the latter, the size
of the input is adapted according to graph size. The results showed that
there is no significant difference in terms of compile time, encryption
time, decryption time, key generation time, and the execution time.
However, mean square error values significantly increase as the input
size decreases if the effect of the graph size is excluded. The second
parameter is the connectivity degree of the graph. As the connectivity
degree increases, all measurement values decrease. This is an expected
result since higher connectivity results in fewer iterations of DFS
algorithm. The performance of the DFS algorithm with EVA language highly
depends on the connectivity degree of the graph. This fact can be
considered as the main parameter of the performance.

Keywords: *Homomorphic encryption, EVA, Depth First Search*

# Introduction

In cloud computation, customers may not want to share all their data
with the cloud service provider. This may force the clients to set a
privacy barrier with the cloud. However, this privacy barrier prevents
any computation on data if the key is not shared with the cloud service
since the data is encrypted. The cloud needs the secret key to decrypt
the data to perform any computation with the traditional approach.

Fully-Homomorphic Encryption (FHE) allows computations on encrypted data
without requiring sharing a key. This allows clients to put a privacy
barrier while allowing certain basic computations on encrypted data.
Microsoft has proposed a software library, SEAL, that allows clients to
use FHE for a particular scheme. However, using SEAL requires extensive
level of experience and knowledge. To overcome this difficulty, a new
language is proposed, namely Encrypted Vector Arithmetic (EVA), which is
a higher-level abstraction of the SEAL. The basic purpose of EVA is to
allow clients to use FHE without requiring too much experience.

Despite the simplicity of EVA, compared to SEAL, it still has a limited
capacity in terms of computations. Implementing some basic algorithms
may require great effort since EVA allows only certain basic
computations. The main purpose of this study is to implement one of the
well-known searching algorithms, Depth First Search (DFS), by using EVA
which can be a guide for other basic implementations.

DFS algorithm requires knowing the vertices which are connected to the
current vertex at each iteration. However, since the EVA does not allow
any comparison operation or accessing a single element in the vector, it
is not possible to find connected vertices using only encrypted data.
This is the main challenge of implementing the algorithm with FHE. To be
able to implement the algorithm, a communication between cloud and the
client is required. This study shows how to implement the algorithm by
establishing a communication between two parties without breaking the
security barrier. Moreover, some basic characteristics of the proposed
method is explained under different circumstances.

# Background and Related Work

## Background

### Depth First Search (DFS)

DFS algorithm is a method to find the vertices reachable from a given
starting vertex. The algorithm can be used in several practical problems
in computer science such as finding a spanning tree, paths, and circuits
in a graph. The main strategy of the algorithm is to explore the nodes
in depth whenever possible. If the algorithm reaches a "dead end", it
backtracks and checks for other nodes to traverse the graph. There are
two well-known approaches to the DFS: iterative and recursive. The
iterative version of the algorithm explores the vertices that are
adjacent to the current vertex and pushes these vertices to a stack in a
while loop. The recursive version of the algorithm does not use a stack,
and at each iteration, the function is recursively called.

### Encrypted Vector Arithmetic (EVA)

EVA is a general-purpose language for FHE computation. It includes an
optimizing compiler that generates correct and secure FHE programs,
while hiding all the complexities of the target FHE scheme. Programmers
can develop efficient general-purpose FHE applications directly in
EVA [@Dathathri2020EVAAE].

Ciphertexts are represented as vectors, which must be power-of-two
vector size, in EVA. In addition, EVA allows limited number of
operations to be performed on vectors, which are Negation, Addition,
Subtraction, Multiplication, RotateLeft, and
RotateRight [@Dathathri2020EVAAE]. Other operations, such as directly
accessing a single element or making comparison between two elements in
the ciphertext, are not allowed.

## Related Work

Since the technology is not fully developed, there are very few
resources on the subject to examine the EVA. Among these, Sobel edge
detection implementation can be reviewed [@Chowdhary2021EVAIC]. In the
same paper, one can also see each step of the usage of EVA.

# Implementation

The implementation of the algorithm is based on the iterative version of
the DFS. A serialized adjacency matrix is used as an input, a list is
used as a stack for backtracking, and a list is used as an array for
tracking the visited vertices. At each iteration, a vertex is popped
from the stack while adjacent vertices of the current vertex are pushed
to the stack. However, since the encrypted values do not show the
adjacency information, this information is obtained from the client
side.

At each iteration of the algorithm, a vector of the encrypted values is
created, and the function is terminated by returning the prepared
encrypted vector. This vector is created using encrypted values of the
adjacency information between the current vertex and the possible
vertices to visit. These possible vertices are the vertices which are
neither visited before nor in the stack.

After the termination of the function, the client side gets the
encrypted output values of the function. These values are first
decrypted, then processed by checking if an edge exists or not. The
client side prepares a list of Boolean values according to the existence
of edges and sends it to the server side again. Once this procedure is
completed, the next iteration begins.

The key point in this approach is the order of the elements in the
vector, which is sent to the client, and the processing order of the
client answer. The order should be preserved while creating the vector
and processing the client answer.

The main drawback of this approach, on the other hand, is that it may
reveal certain information about the degree of the vertices in the
graph. The number of the true values in the client answer at any
iteration shows the minimum value of the degree of a vertex in graph. To
eliminate this drawback, the communication between the client and the
server can be conducted per iteration per node instead of per iteration
only.

# Results and Discussion

## Methodology

Input graphs are created using "connected_watts_strogatz_graph" method
in networkx library for testing the implementation. Connected graphs are
preferred for simulations to perform a better comparison between
measurements since the algorithm will be terminated without traversing
all edges with the unconnected graphs. The graphs are converted to a
serialized adjacency matrix and appended with zeros, if necessary, since
EVA only accepts power-of-two size vectors. Therefore, input size and
graph size should be treated as two different parameters for the
algorithm.

The algorithm is simulated with the graphs of various sizes. The
simulation is conducted 100 times for each graph size. In each
simulation, compile time, encryption time, decryption time, key
generation time, execution time, reference execution time, and mean
square error of the output values are measured. This method is used to
analyze the effects of different parameters on the implementation.

Firstly, the effect of the input size on the implementation is analyzed.
Two different approaches are used. In the first approach, input vector
size is defined as a constant value, which is the minimum possible value
regarding to the maximum graph size. In the second approach, input
vector size is the dynamically changed according to the graph size.

Further tests are conducted to observe the effect of the connectivity
degree of the graph. To achieve different connectivity degrees, the k
parameter of the watts_strogatz_graph method is manipulated. This
parameter shows the number of the connected nearest neighbors in the
ring topology for each node. The measurements are gathered for three
different k values:

-   k = 3

-   k = N/4, (N: number of nodes in the graph)

-   k = N/2, (N: number of nodes in the graph)

## Results

As mentioned in the previous section, the implemented DFS algorithm is
simulated for different graph sizes, and for each graph size, simulation
is repeated 100 times. Mean values of the measurements are calculated
and plotted to observe the effect of the certain parameters.
Figure [1](#fig:Const_vs_Dynamic_Vector_Size){reference-type="ref"
reference="fig:Const_vs_Dynamic_Vector_Size"} shows the effect of the
input size for two different approaches mentioned in the previous
section.

![Constant vs Dynamic Input Size
](figures/Const_vs_Dynamic_Vector_Size.png){#fig:Const_vs_Dynamic_Vector_Size}

As can be seen from Figure 1, there is no significant difference in
terms of encryption time, decryption time, compile time, and execution
time except that the reference execution is slightly slower in the
constant vector size approach. However, the biggest difference is
observed in mean square error (MSE) values which are highly dependent on
the ratio between the input size and the graph size. The effect of the
connectivity degree of the graph is also studied.
Figure [2](#fig:k=3_vs_nover4){reference-type="ref"
reference="fig:k=3_vs_nover4"} and
Figure [3](#fig:k=nover4_vs_nover2){reference-type="ref"
reference="fig:k=nover4_vs_nover2"} present the mean values of the
measurements for k = 3 & k = N/4 and k = N/4 & k = N/2, respectively.

![k=3 vs k=n/4](figures/k=3_vs_nover4.png){#fig:k=3_vs_nover4}

![k=n/4 vs
k=n/2](figures/k=nover4_vs_nover2.png){#fig:k=nover4_vs_nover2}

The result is compatible with the expectations. As the connectivity
increases, the time required for the algorithm decreases since many
vertices are discovered at each iteration.

## Discussion

The results of the test show that the connectivity degree of a graph is
one of the major parameters for the implementation. Higher connectivity
degree results in a smaller number of iterations, which reduces all time
parameters significantly. This is mainly because all connected vertices
to the current vertex are discovered in a single iteration.

# Conclusion

This paper explains the implementation of the DFS algorithm using EVA
language and analyzes the implementation for different aspects. The most
challenging part of the implementation is making a comparison on
encrypted data. Since EVA does not support comparison on encrypted data,
the existence of an edge in the graph is discovered with the help of the
unencrypted region. This is a general issue many users may encounter
while implementing an algorithm in EVA. Moreover, since an encryption
and decryption process are required for each iteration, the connectivity
degree of a graph has a huge effect on the time spent.

As mentioned in the Result and Discussion section of the report,
implementation reveals some information about the connectivity of the
graph. To overcome this exposure, the communication between encrypted
and unencrypted region can be changed per iteration per node instead of
per iteration only. However, this new approach may drastically increase
the time complexity of the algorithm and may reduce the effect of the
connectivity degree on time complexity. In addition, the implementation
can be improved by eliminating new key generation for each iteration.
This could be achieved by saving and reusing the keys and encrypted
inputs at each iteration.
