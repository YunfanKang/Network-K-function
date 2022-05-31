def pedal(p1, p2, p3):
    if p2[0] != p1[0]:
        k, b = np.linalg.solve([[p1[0], 1], [p2[0], 1]], [p1[1], p2[1]])
        x = np.divide(((p2[0] - p1[0]) * p3[0] + (p2[1] - p1[1]) * p3[1] - b * (p2[1] - p1[1])),
                      (p2[0] - p1[0] + k * (p2[1] - p1[1])))
        y = k * x + b

    else:
        x = p1[0]
        y = p3[1]
    d1 = (x - p1[0])**2 + (y - p1[1])**2
    d2 = (x - p2[0])**2 + (y - p2[1])**2
    d = (p1[0] - p2[0])**2 + (p1[1] - p2[1])**2
    if d1 > d:
        return p2[0], p2[1]
    elif d2 > d:
        return p1[0], p1[1]
    else:
        return x, y
def fix_oneway(G):
    #edge_oneway = nx.get_edge_attributes(G, "oneway")
    for e in G.edges:
        if G.edges[e]['oneway']:
            G.add_edge(e[1], e[0], 0)
            attrs = {(e[1], e[0], 0):{"length": G.edges[e]['length'], "oneway": False}, e:{"length": G.edges[e]['length'], "oneway": False}}
            nx.set_edge_attributes(G, attrs)
def match_event_to_edges(events, G, show_mod = False): #May need to create a function for reverting the ops
    max_index = max(G.nodes) + 1
    matched_points = []
    for i in range(len(events)):
        event_index = -1 * (max_index + i)
        if (show_mod):
            print("Finding nearest edge for ", event_index, ", ", events.iloc[i])
        nearest_edge = ox.nearest_edges(G, events.iloc[i]['x'], events.iloc[i]['y'])
        if (show_mod):
            print("Nearest edge is ", nearest_edge)
        p1 = nearest_edge[0]
        p2 = nearest_edge[1]
        match_x, match_y = pedal((G.nodes[p1]['x'], G.nodes[p1]['y']), (G.nodes[p2]['x'], G.nodes[p2]['y']), (events.iloc[i]['x'], events.iloc[i]['y']))
        if(show_mod):
            print("Match ", match_x, match_y)
        
        #event_index = -1 * (max_index + i)
        edge_lengths = nx.get_edge_attributes(G, "length")
        originalLength = edge_lengths[(p1, p2, 0)]
        length_1e = (match_x - G.nodes[p1]['x'])/ (G.nodes[p2]['x'] - G.nodes[p1]['x']) * originalLength
        length_2e = originalLength - length_1e
        G.add_node(event_index)
        G.nodes[event_index]['x'] = match_x
        G.nodes[event_index]['y'] = match_y
        G.nodes[event_index]['street_count'] = 2
        G.remove_edges_from(((p1, p2, 0), (p2, p1, 0)))
        if(show_mod):
            print("Remove ", p1, "-" , p2)
            print("Add ", p1, "-", event_index, "-", p2)
        G.add_edges_from(((p1, event_index, 0), (event_index, p1, 0), (p2, event_index, 0), (event_index, p2, 0)))
        attrs = {(p1, event_index, 0):{"length": length_1e, "oneway": False}, (event_index, p1, 0):{"length": length_1e, "oneway": False}, (p2, event_index, 0):{"length": length_2e, "oneway": False}, (event_index, p2, 0):{"length": length_2e, "oneway": False}}
        nx.set_edge_attributes(G, attrs)
        matched_points.append(event_index)
    return matched_points
def extended_shortest_path_tree(root_node, G):
    root = Node(root_node, d = 0, l = 0) 
    edge_lengths = nx.get_edge_attributes(G, "length")
    distances, paths = nx.single_source_dijkstra(G,root_node,weight = 'length') #No need to start 
    for pkey in paths.keys():
        if not pkey == root:
            path = paths[pkey]
            for i in range(1, len(path)):
                if not find(root, lambda node: node.name == path[i]):
                    node = Node(path[i], parent = find(root, lambda node: node.name == path[i-1]), l = edge_lengths[( path[i-1], path[i], 0)], d = distances[path[i]])
    for l in PreOrderIter(root):#Need to further confirm the correcteness
        lname = l.name
        neighborEdges = list(G.edges(lname))
        for e in neighborEdges:
            v2 = find(root, lambda node: node.name == e[1])
            if v2 and not (v2 == l.parent or l == v2.parent) :
                ledge = edge_lengths[(lname, e[1], 0)]
                #print('Leave: ', lname)
                #print('d: ', l.d)
                #print('neighbor d: ', v2.d)
                #print('Edge length: ', ledge)
                dbreak = (v2.d + ledge - l.d)/2
                node = Node(str(lname)+"break"+str(v2.name), parent = l, l = dbreak, d = l.d + dbreak)
                node = Node(str(v2.name)+"break"+str(lname), parent =v2, l = ledge- dbreak, d = v2.d + ledge- dbreak)
            if not v2:
                print("Error: Neighbor node not in tree: ",e, edge_lengths[(lname, e[1], 0)])
    return root
def shortest_path_tree(root_node, G):
    root = Node(root_node, d = 0, l = 0)
    edge_lengths = nx.get_edge_attributes(G, "length")
    distances, paths = nx.single_source_dijkstra(G,root_node,weight = 'length') #No need to start 
    for pkey in paths.keys():
        if not pkey == root:
            path = paths[pkey]
            for i in range(1, len(path)):
                if not find(root, lambda node: node.name == path[i]):
                    node = Node(path[i], parent = find(root, lambda node: node.name == path[i-1]), l = edge_lengths[( path[i-1], path[i], 0)], d = distances[path[i]])
    return root