'''
Script to convert a 3-edge connected graph into a cactus graph
'''

import igraph
import graph_algorithms as g

class graph:
    def __init__(self, verticies, edges):
        self.verticies = verticies
        self.edges = edges

def setup(edges):
    # Get vertex balh
    vertices = set()
    for u, v, w in edges:
        vertices.add(u)
        vertices.add(v)
    n = len(vertices)

    # Check for 3ec
    cc = g.k_edge_connected_components(edges,3)
    if cc == [[]] or len(cc[0][0]) != n:
        print("WARNING: Graph is not 3 edge connected")
    
    return vertices

# Crossign cuts
def isCrossing(cut1, cut2):
    '''
    Given 2 cuts as list(set), returns whether they are crossing and a list of intersections
    '''
    A,B = cut1
    C,D = cut2
    intersections = [A & C, A & D, B & C, B & D]
    flag = True
    for i in intersections:
        if len(i) == 0:
            flag = False
    return flag, intersections

def get_f_cuts(vertices, edges):
    '''
    Given (V,E) return all F-cuts
    Returns basic F-cuts
    '''
    # Get all 3 cuts, 4 cuts 
    cuts_3 = g.k_cut(edges, 3)
    cuts_4 = g.k_cut(edges, 4)
    shores_3 = [shore for cut in cuts_3 for shore in cut]
    cuts_3 = [list(map(set, cut)) for cut in g.k_cut(edges, 3)]
    cuts_4 = [list(map(set, cut)) for cut in g.k_cut(edges, 4)]
    shores_3 = [shore for cut in cuts_3 for shore in cut]

    # Get all bridge cuts
    bridge_cuts = []
    for cut in cuts_4:
        for X in cut: # for every shore
            for Y in shores_3: # for every 3-cut shore
                if Y < X: # if Y \in X
                    Y2 = X - Y
                    if Y2 in shores_3:
                        bridge_cuts.append(cut)
    bridge_cuts = list({frozenset(map(frozenset, cut)) for cut in bridge_cuts}) # remove dupes
    bridge_cuts = [list(map(set, cut)) for cut in {frozenset(map(frozenset, cut)) for cut in bridge_cuts}]

    # Get bridge free cuts
    cuts_4_static = {frozenset(map(frozenset, cut)) for cut in cuts_4}
    bridge_cuts_static = {frozenset(map(frozenset, cut)) for cut in bridge_cuts}

    bridgefree_cuts = [list(map(set, cut)) for cut in cuts_4_static - bridge_cuts_static]

    # Get corner cuts
    corner_cuts = []
    for i in range(len(bridgefree_cuts)):
        for j in range(i, len(bridgefree_cuts)):
            crossing, intersections = isCrossing(bridgefree_cuts[i], bridgefree_cuts[j])
            if (crossing):
                for shore in intersections:
                    corner_cuts.append([shore, vertices - shore]) # This is a bit janky but should work

    # Family of F cuts
    F_cuts = []
    F_cuts.extend(cuts_3)
    F_cuts.extend(bridgefree_cuts)
    F_cuts.extend(corner_cuts)
    F_cuts = [list(map(set, cut)) for cut in {frozenset(map(frozenset, cut)) for cut in F_cuts}]

    # Get basic F-cuts
    # Basic_F_cuts = []
    # for cut1 in F_cuts:
    #     flag = True
    #     for cut2 in F_cuts:
    #         if cut1 != cut2 and isCrossing(cut1, cut2)[0]:
    #             flag = False
    #     if flag:
    #         Basic_F_cuts.append(cut1)

    return F_cuts

def edit_cuts(v, cuts, dummy, dummyset):
    '''
    Given current vertices, nontrivial basic f cuts, filter them so shores with the dummy node's set are replaced with just the dummy node
    '''
    new_cuts = []
    for s1,s2 in cuts:
        s1 = s1 & v
        s2 = s2 & v
        if dummyset <= s1: 
            s1.add(dummy)
        elif dummyset <= s2:
            s2.add(dummy)
        if len(s1) > 0 and len(s2) > 0:
            new_cuts.append((s1,s2))
    return new_cuts

def cactus(v, cuts):
    '''
    Recursive cactus function that returns a graph struct
    Takes in verticies, basic f-cuts
    '''
    global currn
    n = len(v)
# Base Case: Either a vertex, cycle, or cube
    # Vertex / Edge
    if len(v) == 1:
        return graph(verticies = v, edges = [])
    if len(v) == 2:
        vl = list(v)
        v1, v2 = vl[0], vl[1] 
        return graph(verticies = {v1,v2}, edges = [(v1,v2)])

    # Find a nontrivial basic cut
    for cut in cuts:
        # Check if the cut is basic (not crossing)
        if any(isCrossing(cut, other)[0] for other in cuts if other != cut):
            continue

        shore1, shore2 = cut
        p1 = shore1 & v# p - partitions
        p2 = shore2 & v
        if len(p1) >= 2 and len(p2) >= 2: # The cut is partitioning the subgraph, also checks triviality
            # Recursive Case

            # Add dummy nodes
            a = currn + 1
            b = currn + 2
            currn += 2

            v1 = p1 | {a}
            v2 = p2 | {b}

            c1 = edit_cuts(v1,cuts,a,p2)
            c2 = edit_cuts(v2,cuts,b,p1)

            cactus1 = cactus(v1, c1)
            cactus2 = cactus(v2,c2)

            verticies = cactus1.verticies | cactus2.verticies #union
            edges = cactus1.edges + cactus2.edges + [(a,b)]

            return graph(verticies = verticies, edges = edges)
    # Slop for now ggs
    # Create a cube or cycle graph

    if len(v) == 8: # Cube Reconstruction
            active = [c for c in cuts if 0 < len(c[0] & v) < 8][:3]
            coords = {u: "".join("1" if u in s1 else "0" for s1, s2 in active) for u in v}
            edges = [(u, w) for i, u in enumerate(list(v)) for w in list(v)[i+1:] if sum(b1 != b2 for b1, b2 in zip(coords[u], coords[w])) == 1]
            return graph(v, edges)
    # Otherwise, form a cycle 
    ordered, remaining = [list(v)[0]], set(v) - {list(v)[0]}
    while remaining:
        # Find the next neighbor by choosing the node with the minimum cut separation
        nxt = min(remaining, key=lambda cand: sum((ordered[-1] in s1 and cand in s2) or (ordered[-1] in s2 and cand in s1) for s1, s2 in cuts))
        ordered.append(nxt)
        remaining.remove(nxt) 
    return graph(v, [(ordered[i], ordered[(i + 1) % len(ordered)]) for i in range(len(ordered))])   
    
def create_cactus(edges):
    '''
    Creates a cactus given edges
    Oh my balls this better work
    '''
    vertices = setup(edges)
    curnn = len(vertices) # Global counter
    basic_f_cuts = get_f_cuts(vertices, edges)
    cactus_graph = cactus(vertices, basic_f_cuts)
    return cactus_graph.edges

