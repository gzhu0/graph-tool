'''
Collection of graph algorithms
'''

from collections import defaultdict
import itertools
import networkx as nx
import itertools
import igraph as ig
import random
import math
import numpy as np

# K-Cut Algorithm 

def k_cut(data, k: int):
    '''
    Returns all k-cuts in the graph.
    A k-cut is a partition of vertices into two non-empty sets (A, B)
    such that the sum of edge weights between A and B is exactly k.
    '''
    # 1. Filter out self-loops and standardize edges
    edges = [(u, v, w) for u, v, w in data if u != v]

    # 2. Extract all unique vertices
    vertices = list(set(v for u, v, w in edges for v in (u, v)))
    
    # A cut requires at least 2 vertices
    if len(vertices) < 2:
        return []

    cuts_return = []
    
    # We lock the first vertex into Set A. 
    # This prevents counting (A, B) and (B, A) as two separate cuts.
    v0 = vertices[0]
    remaining_vertices = vertices[1:]

    # 3. Iterate through all possible partitions of the remaining vertices
    for r in range(len(remaining_vertices) + 1):
        for a_subset in itertools.combinations(remaining_vertices, r):
            
            # Construct Set A and Set B
            set_A = set(a_subset)
            set_A.add(v0)
            set_B = set(vertices) - set_A

            # A valid cut requires both sets to be non-empty
            if not set_B:
                continue

            # 4. Calculate the weight of the edges crossing the cut
            cut_weight = 0
            for u, v, w in edges:
                if (u in set_A and v in set_B) or (v in set_A and u in set_B):
                    cut_weight += w

            # 5. If the cut weight matches k, format and save it
            if cut_weight == k:
                cuts_return.append([sorted(list(set_A)), sorted(list(set_B))])

    return cuts_return

# def k_cut(data: list[list], k: int):
#     '''
#     Returns all k cuts in the graph
#     '''
#     all_edges = [tuple(x) for x in data if x[0] != x[1]]
    

#     vertices = set(itertools.chain.from_iterable(data))
#     n = len(vertices)
#     cut_count = 0
#     cuts_return = []

#     for cut in itertools.combinations(data, k):
#         cut_set = set(tuple(x) for x in cut)
#         edges = [x for x in all_edges if tuple(x) not in cut_set]

#         g = nx.Graph()
#         g.add_nodes_from(range(n))
#         g.add_edges_from(edges)

#         mappings = defaultdict(int)

#         contracted = g.copy()
#         for component in nx.connected_components(g):
#             component = list(component)
#             for v in component:
#                 mappings[v] = component[0]
#             for v in component[1:]: # We merge everything to first node
#                 contracted = nx.contracted_nodes(contracted, component[0], v, self_loops=False)

#         # Remapping each vertex
#         for u,v in cut:
#             new_u = mappings[u]
#             new_v = mappings[v]
#             contracted.add_edge(new_u,new_v)        
#         # Checking bipartite
#         is_bip = nx.is_bipartite(contracted)
#         if (is_bip): 
#             cut_count += 1
#             coloring = nx.bipartite.color(contracted)
#             set_A = []
#             set_B = []
#             for v in vertices:
#                 if coloring[mappings[v]] == 1:
#                     set_A.append(v)
#                 else:
#                     set_B.append(v)
#             print(set_A,set_B)
#             cuts_return.append([set_A, set_B])

#     print(cut_count, "cuts found.")
#     return cuts_return

# K-Edge-Connected Components ###

def k_edge_connected_components(data: list[list], k: int):
    '''
    Returns each k edge connected components in the graph.
    Supports unweighted [u, v] and weighted [u, v, weight] lists.
    '''
    g = nx.Graph()

    # Dynamically handle normal vs weighted edges
    for x in data:
        if x[0] != x[1]:  # Ignore self-loops
            if len(x) >= 3:
                g.add_edge(x[0], x[1], weight=x[2])
            else:
                g.add_edge(x[0], x[1])

    # Get Components
    components = [sorted(x) for x in nx.k_edge_components(g, k=k) if len(x) > 1]

    return [components]

# Spanning Tree Congestion Approximation###

def algorithm_stc(edge_list, temp=10.0, cooling=0.9995):

# Simmulated Annealing Algorithm to approximate spanning tree congestion  
    
    # Get steps based on density of the graph
    m = len(edge_list)
    steps = (m ** 2) * 100  

    vertices = set()
    for u, v in edge_list:
        vertices.add(u)
        vertices.add(v)
    
    # remap to 0-indexed
    sorted_verts = sorted(vertices)
    idx = {v: i for i, v in enumerate(sorted_verts)}
    reverse_idx = {i: v for v, i in idx.items()}
    
    remapped = [(idx[u], idx[v]) for u, v in edge_list]
    n = len(sorted_verts)
    
    G = ig.Graph(n=n, edges=remapped)
    
    best_edge_ids, best_cost = sa(G, steps=steps, temp=temp, cooling=cooling)
    
    best_edge_list = [
        [reverse_idx[G.es[eid].source], reverse_idx[G.es[eid].target]]
        for eid in best_edge_ids
    ]
    print("Tree:", best_edge_list)
    print("Congestion:", best_cost)
    return best_edge_list, best_cost

def congestion(G, tree_edges):
    max_cong = 0
    
    for i, eid in enumerate(tree_edges):
        sub_edges = [e for j, e in enumerate(tree_edges) if j != i]
        T_sub = G.subgraph_edges(sub_edges, delete_vertices=False)
        comps = T_sub.connected_components()
        membership = comps.membership
        
        A = {v for v, m in enumerate(membership) if m == 0}
        B = {v for v, m in enumerate(membership) if m == 1}
        
        cong = sum(1 for e in G.es
                   if (e.source in A and e.target in B)
                   or (e.source in B and e.target in A))
        max_cong = max(max_cong, cong)
    
    return max_cong

def random_spanning_tree(G):
    weights = [random.random() for _ in G.es]
    T = G.spanning_tree(weights=weights)
    # return as edge indices in G
    tree_edge_ids = []
    for te in T.es:
        u, v = te.source, te.target
        eid = G.get_eid(u, v)
        tree_edge_ids.append(eid)
    return tree_edge_ids

def sa(G, steps=1000_000, temp=10.0, cooling=0.9995):
    tree_edges = random_spanning_tree(G)
    best_edges = tree_edges[:]
    best_cost = congestion(G, tree_edges)
    cost = best_cost
    
    tree_set = set(tree_edges)
    non_tree = [e.index for e in G.es if e.index not in tree_set]

    for i in range(steps):
        idx = random.randrange(len(tree_edges))
        removed = tree_edges[idx]
        trial = [e for j, e in enumerate(tree_edges) if j != idx]
        
        T_sub = G.subgraph_edges(trial, delete_vertices=False)  # fix here
        comps = T_sub.connected_components()
        membership = comps.membership
        A = {v for v, m in enumerate(membership) if m == 0}
        B = {v for v, m in enumerate(membership) if m == 1}
        
        crossing = [e for e in non_tree
                    if (G.es[e].source in A and G.es[e].target in B)
                    or (G.es[e].source in B and G.es[e].target in A)]
        
        if not crossing:
            continue
        
        added = random.choice(crossing)
        new_tree = trial + [added]
        new_cost = congestion(G, new_tree)
        
        delta = new_cost - cost
        if delta < 0 or random.random() < math.exp(-delta / temp):
            tree_edges = new_tree
            tree_set = set(tree_edges)
            non_tree = [e.index for e in G.es if e.index not in tree_set]
            cost = new_cost
            if cost < best_cost:
                best_cost = cost
                best_edges = tree_edges[:]
        
        temp *= cooling
    
    return best_edges, best_cost

#via igraph, brute force the STC of a given spanning tree given the original graph and the spanning tree
def spanningTreeCongestion(graph, spanningTree) -> int:
    #the spanning tree MUST be valid, little error checking is done to ensure it is valid
    #graph is the undirected base igraph object of the graph in question
    #st edge is a list of tuples (or whatever the parentheses are) representing the edges in the spanning tree
    #corresponding vertices must be named the same on both graphs, 0 to n-1

    maxCongestion = 1
    STedges = spanningTree.get_edgelist()

    #these are needed beacuse all_st_cuts does not work with an undirected graph, and was the easiest way for me to create a partition given the spanning tree (i don't need to personally figure out which edge is where)
    directedSpanningTree = spanningTree.as_directed()

    for edge in STedges:
        treeCuts = directedSpanningTree.all_st_cuts(edge[0], edge[1])

        if (len(treeCuts) != 1):
            print("WEEWOO")
            raise Exception("given cut of spanning tree does not have one edge")
        
        leftpart = treeCuts[0].partition[0]
        rightpart = treeCuts[0].partition[1]
        edgeCongestion = 0

        #for every combination of left part-right part, check if there is an edge in the original graph, if so that adds 1 to the congestion
        #the spanning tree edge will be counted as well with this method
        for leftvertex in leftpart:
            for rightvertex in rightpart:
                #the matrix form of the graph that igraph gives has numbers represent the weights as well, allowing us to account for multigraphs
                edgeCongestion += graph[leftvertex, rightvertex]
        
        if (edgeCongestion > maxCongestion):
            maxCongestion = edgeCongestion

    return maxCongestion

#gives a list of tuples of edges, each tuple is a spanning tree and containes edges represented by tuples
def getAllSpanningTrees(graph) -> list:
    'gives a list of tuples of edges, each tuple is a spanning tree and containes edges represented by tuples'
    spanningtrees = []
    adjmatrix = np.array(graph.get_adjacency())
    currTree = ()
    currVertices = (0,)
    getSpanningTreeRecursive(adjmatrix, currTree, currVertices, spanningtrees)

    return spanningtrees


def getSpanningTreeRecursive(adjacency, currTreeEdges, currTreeVertices, spanningTreeList):
    n = adjacency.shape[1]
    if (len(currTreeEdges) == n-1):
        currTreeEdges = tuple(sorted(currTreeEdges))
        if currTreeEdges not in spanningTreeList:
            spanningTreeList.append(currTreeEdges)
        return
    for vertex in currTreeVertices:
        for i in range(n):
            if i in currTreeVertices:
                continue
            if (adjacency[vertex][i]):
                getSpanningTreeRecursive(adjacency, currTreeEdges + ((vertex, i),), currTreeVertices + (i,), spanningTreeList) 
    return

#sanity check, use kirchoff's theorem to figure out how many spanning trees there should be
def getNumSpanningTrees(graph) -> int:
    'use kirchoffs theorem to figure out how many spanning trees there should be'
    adjmatrix = np.array(graph.get_adjacency())
    adjmatrix = -1 * adjmatrix

    for i in range(adjmatrix.shape[1]):
        adjmatrix[i][i] = 0
        for j in range(adjmatrix.shape[1]):
            if adjmatrix[i][j] == -1:
                adjmatrix[i][i]  += 1
    adjmatrix = np.delete(adjmatrix, 0, axis=0)
    adjmatrix = np.delete(adjmatrix, 0, axis=1)

    return round(np.linalg.det(adjmatrix))


def getMinimumSpanningTrees(graph) -> tuple:
    'tuple is ([list of min span trees in edges], congestion)'
    minSpanTrees = []
    allSpanTrees = getAllSpanningTrees(graph)
    if (len(allSpanTrees) != getNumSpanningTrees(graph)):
        raise Exception("Number of spanning trees does not match how many should exist", len(allSpanTrees), "(found) vs ", getNumSpanningTrees(graph), " (kirchoff)")
    congestions = []
    for spanningtreeedgeset in allSpanTrees:
        congestions.append(spanningTreeCongestion(graph, ig.Graph(edges=spanningtreeedgeset)))
    minCongestion = min(congestions)
    for i in range(len(allSpanTrees)):
        if (congestions[i] == minCongestion):
            minSpanTrees.append(allSpanTrees[i])
    return minSpanTrees, minCongestion
