def ntpi(t, pi):
    found = []
    distances, paths = nx.single_source_dijkstra(G,pi,cutoff=t, weight = 'length') #No need to start from scratch every time
    for p in paths.keys():
        if p in matched_index and (p not in found):
            #print(p)
            #print(p in found)
            found.append(p)
    return len(found)
def Ltp (root, tj):
    D = 0
    #root = extended_shortest_path_tree(pi, G)
    for child in root.children:
        if  child.d <= tj:
            D = D + child.l + Ltp(child, tj)
        else:
            D = D + child.l + tj - child.d #if a node is further than tj, the subtree rooted at the node will not be computed
    return D
def L(G):
    edge_lengths = nx.get_edge_attributes(G, "length")
    edge_oneway = nx.get_edge_attributes(G, "oneway")
    L = 0
    for edge in G.edges:
        if edge_oneway[edge]:
            L = L + edge_lengths[edge]
        else:
            L = L + edge_lengths[edge]/2
    return L
def Var(G, t, pi, n):
    l = L(G)
    Ltpi = Ltp(extended_shortest_path_tree(pi, G), t)
    var = 1/(n-1) * l * Ltpi * (1-Ltpi/l)
    return var
def Ktp(G, t, pi, n):
    return L(G)/(n-1)*ntpi(t, pi)