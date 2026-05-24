import igraph as ig
import matplotlib.pyplot as plt
import graph_algorithms

data = [[0, 1], [1, 2], [2, 3], [3, 4], [4, 5], [5, 6], [6, 7], [7, 0], [0, 4], [1, 5], [2, 6], [3, 7]]

graph_algorithms.k_cut(data,4)


edges = [(0,1),(1,2),(2,3),(3,0)]
edgeweights = [1,1,1,1]
g = ig.Graph(n=4, edges=edges)
g.es["weight"] = 1.0
g[0,1] = 3

print(g)

fig, ax = plt.subplots()
ig.plot(g, target=ax, 
        vertex_label=['0', '1', '2', '3', '4', '5', '6', '7','8','9','10','11'],)
ax.invert_yaxis()
#plotting doesnt seem to work in terminal... wonder why xd
#works best on a jupiter notebook or something of the sort

exspanningtreeedge = [(1,0),(1,2),(2,3)]
exspanningtree = ig.Graph(n=4, edges=exspanningtreeedge)
print(graph_algorithms.spanningTreeCongestion(g, exspanningtree))