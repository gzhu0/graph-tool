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

# K-Cut Algorithm ###

def k_cut(data: list[list], k: int):
    '''
    Returns all k cuts in the graph
    '''
    all_edges = [tuple(x) for x in data if x[0] != x[1]]
    

    vertices = set(itertools.chain.from_iterable(data))
    n = len(vertices)
    cut_count = 0
    cuts_return = []


    for cut in itertools.combinations(data, k):
        cut_set = set(tuple(x) for x in cut)
        edges = [x for x in all_edges if tuple(x) not in cut_set]

        g = nx.Graph()
        g.add_nodes_from(range(n))
        g.add_edges_from(edges)

        mappings = defaultdict(int)

        contracted = g.copy()
        for component in nx.connected_components(g):
            component = list(component)
            for v in component:
                mappings[v] = component[0]
            for v in component[1:]: # We merge everything to first node
                contracted = nx.contracted_nodes(contracted, component[0], v, self_loops=False)

        # Remapping each vertex
        for u,v in cut:
            new_u = mappings[u]
            new_v = mappings[v]
            contracted.add_edge(new_u,new_v)        
        # Checking bipartite
        is_bip = nx.is_bipartite(contracted)
        if (is_bip): 
            cut_count += 1
            coloring = nx.bipartite.color(contracted)
            set_A = []
            set_B = []
            for v in vertices:
                if coloring[mappings[v]] == 1:
                    set_A.append(v)
                else:
                    set_B.append(v)
            print(set_A,set_B)
            cuts_return.append([set_A, set_B])

    print(cut_count, "cuts found.")
    return cuts_return

# K-Edge-Connected Components ###

def k_edge_connected_components(data: list[list], k: int):
    '''
    Returns each k edge connected compoennts in the graph
    '''

    edges = [tuple(x) for x in data if x[0] != x[1]]
    vertices = set(itertools.chain.from_iterable(data))
    # Create Graph
    g = nx.Graph()
    n = len(vertices)
    g.add_nodes_from(range(n))
    g.add_edges_from(edges)
    # Get Components
    components = [sorted(x) for x in nx.k_edge_components(g, k=k) if len(x) > 1]

    # Filter Out Components
    print(f"components {components}")
    return([components])

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

def sa(G, steps=100_000, temp=10.0, cooling=0.9995):
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