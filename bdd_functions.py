import sys

## Stores the BDD graph nodes
class BddGraph:
    def __init__(self):
        self.nodes = {}

    def to_str(self):
        string = ""
        for node_name in self.nodes:
            string = string+str("\n"+node_name+': '+str([[x, self.nodes[node_name].get_connections()[x][1]] for x in self.nodes[node_name].get_connections()]))
        return string

    def get_all_nodes(self):
        return self.nodes

    def get_node(self, node_name):
        try:
            return self.nodes[str(node_name)]
        except:
            return False

    def include(self, node_name):
        if (self.get_node(node_name) == False):
            node = BddNode(node_name)
            self.nodes[str(node_name)] = node
            return True
        else:
            return False

    def reset_weights(self, n = 99999):
        for x in self.nodes:
            self.nodes[x].reset_weight(n)

    def calculate_cost(self):
        total_cost = 0
        visited = []
        to_visit = [self.get_all_nodes()[node] for node in self.get_all_nodes()]
        for node_name in self.nodes:
            node = self.nodes[node_name]
            connections = node.get_connections()
            for n in connections:
                if (connections[n][0] in to_visit):
                    total_cost = total_cost + connections[n][1]
            
            to_visit.remove(node)
        return total_cost


## Defines nodes inside the BDD graph
class BddNode:
    def __init__(self, name):
        self.name = name
        self.weight = 99999
        self.parent = None
        self.connections = {"origin" : [self, 0]}

    def connect(self, node, distance):
        self.connections[node.get_name()] = [node, int(distance)]

    def disconnect(self, node_name):
        self.connections.pop(node_name)

    def get_connections(self):
        return self.connections

    def get_name(self):
        return self.name

    def get_weight(self):
        return self.weight
    
    def get_parent(self):
        return self.parent

    def reset_weight(self, n = 99999):
        self.weight = n

    def set_parent(self, node):
        self.parent = node

    def set_weight(self, weight):
        self.weight = weight

## Prim algorithm for the BddGraph class
def prim(bdd_graph, starting_node, ignore = []):

    visited_list = [starting_node]
    visited_list = visited_list + ignore

    #gets nodes remaining to be visited
    graph_nodes = bdd_graph.get_all_nodes()
    visit_list = [graph_nodes[node] for node in graph_nodes]

    for x in visited_list:
        try:
            visit_list.remove(x) 
        except:
            pass

    final_tree = []
    while visit_list != []:
        print("current visited nodes:", [x.get_name() for x in visited_list], "remaining nodes:", [x.get_name() for x in visit_list])
        #gets available connections
        available_connections = [node.get_connections() for node in visited_list]

        #searches for the shortest path
        shortest_dist = 99999
        for connections_dict in available_connections:
            for value in connections_dict:
                if (connections_dict[value][1] < shortest_dist) and (connections_dict[value][1] > 0) and (connections_dict[value][0] not in visited_list):
                    shortest_dist = connections_dict[value][1]
                    #saves closest node, origin and distance
                    shortest_node = connections_dict[value][0]
                    origin = connections_dict["origin"][0]
                    print ("current shortest path:",shortest_dist, " from", origin.get_name(), "to", shortest_node.get_name())
            
        visited_list.append(shortest_node)
        visit_list.remove(shortest_node)
        final_tree.append([origin, shortest_node, shortest_dist])
        print("removing", shortest_node.get_name(), "from visit list")

    #Generate a new BDD, with the shortest paths
    print("\n############## Re-creating structure ##############")
    new_bdd = BddGraph()
    for node in final_tree:
        try:
            node_name1 = node[0].get_name()
            new_bdd.include(node_name1)
            node1 = new_bdd.get_node(node_name1)

            node_name2 = node[1].get_name()            
            new_bdd.include(node_name2)
            node2 = new_bdd.get_node(node_name2)

            distance = node[2]
            node1.connect(node2, distance)
            node2.connect(node1, distance)
        except:
            print('Error creating connection', connection)

    print("### Final structure resulting from Prim: "+new_bdd.to_str())
    return new_bdd

## Dijkstra algorithm for the BddGraph class
def dijkstra(bdd_graph, starting_node, direction = "one"):

    starting_node.set_weight(0)

    graph_nodes = [bdd_graph.get_all_nodes()[node] for node in bdd_graph.get_all_nodes()]

    visit_list = [starting_node]
    visited_list = [starting_node]

    while visit_list != [] or (len(visited_list) < len(graph_nodes)):
        #gets available connections
        available_connections = [node.get_connections() for node in visit_list]
        visit_list = []

        #sets weights
        for connections_dict in available_connections:
            print("Current node:", connections_dict["origin"][0].get_name())
            for value in connections_dict:
                if (value != "origin"):
                    new_weight = connections_dict["origin"][0].get_weight() + connections_dict[value][1]
                    if (new_weight < connections_dict[value][0].get_weight()) or ((new_weight == connections_dict[value][0].get_weight()) and (connections_dict["origin"][0].get_weight() < connections_dict[value][0].get_parent().get_weight())):
                        connections_dict[value][0].set_weight(new_weight)
                        connections_dict[value][0].set_parent(connections_dict["origin"][0])

                        print("updated weight:", connections_dict[value][0].get_name(), connections_dict[value][0].get_weight())
                        if (connections_dict[value][0] not in visited_list):
                            visit_list.append(connections_dict[value][0])
            
        visited_list.append(connections_dict["origin"][0])

    #Finds path according to minimum weights
    bdd_structure = []
    for node in graph_nodes:
        current_node = node
        path = [int(node.get_name())]
        while current_node.get_parent() != None:
            dest = current_node
            current_node = current_node.get_parent()
            path.append(int(current_node.get_name()))
            struct = [current_node.get_name(), dest.get_name(), dest.get_weight() - current_node.get_weight()]
            if struct not in bdd_structure:
                bdd_structure.append(struct)
        path.reverse()
        print("Shortest path to node " + node.get_name() + ": "+str(path))
    print (bdd_structure)

    #Generates a new BDD, with the shortest paths
    print("\n############## Re-creating structure ##############")
    new_bdd = BddGraph()
    for connection in bdd_structure:
        try:
            node_name1 = connection[0]
            new_bdd.include(node_name1)
            node1 = new_bdd.get_node(node_name1)

            node_name2 = connection[1]        
            new_bdd.include(node_name2)
            node2 = new_bdd.get_node(node_name2)

            distance = connection[2]
            node1.connect(node2, distance)
            if direction == "both":
                node2.connect(node1, distance)
        except:
            print('Error creating connection', connection)

    print("### Final structure resulting from Dijkstra: "+new_bdd.to_str())
    return new_bdd

def tsm(bdd_graph, starting_node):

    #gets a node
    #gets available connections
    #starts a branch for each connection
        #runs prim for the connection
        #collects total tree cost
    #compare costs
    #decide which one to branch next based on cost

    print("Starting node: ", starting_node.get_name())

    bdd_graph.reset_weights(0)

    visited_list = [starting_node]

    print(len(bdd_graph.get_all_nodes()))
    while(len(visited_list) < len(bdd_graph.get_all_nodes())):

        available_connections = [node.get_connections() for node in visited_list]
        
        for connections_dict in available_connections:
            smallest = 99999
            for n in connections_dict:
                if n != "origin":
                    if (connections_dict[n][0].get_weight() < smallest):
                        smallest = connections_dict[n][0].get_weight()
                        candidate = connections_dict[n][0]

        #print(visited_list)

        new_weight = prim(bdd_graph, candidate, ignore = visited_list).calculate_cost()
        if (new_weight > 0) and ((candidate.get_weight() > new_weight) or (candidate.get_weight() == 0)):
            candidate.set_weight(new_weight)

        print(candidate.get_name(), new_weight)
        visited_list.append(candidate)

    dijkstra(bdd_graph, starting_node, direction="both")
    
    exit(0)

    ##Should continue here but i didn't get it to work properly


## Loads a .txt file containing a BDD graph for prim/dijkstra algorithm
def load_file(filename, algorithm, starting_node_name):
    bdd_structure = []

    with open(filename, "r") as file:
        for line in file.readlines():
            bdd_structure.append(line.split())

    print (bdd_structure)

    bdd_graph = BddGraph()

    # Iterates over the structure and creates the first nodes
    for connection in bdd_structure:
        try:
            if not bdd_graph.include(connection[0]):
                print('Node', connection[0], 'already exists!')
            node1 = bdd_graph.get_node(connection[0])

            if (connection[1] in node1.get_connections()):
                print ('Connection', connection, 'already exists!')
                pass
            
            if not bdd_graph.include(connection[1]):
                print('Node', connection[1], 'already exists!')
            node2 = bdd_graph.get_node(connection[1])

            node1.connect(node2, connection[2])
            if (algorithm == "prim") or (algorithm == "tsm"):
                node2.connect(node1, connection[2])
        except:
            print('Error creating connection', connection)


    print("\n############## Loaded structure ##############:", bdd_graph.to_str(), "\n")
    starting_node = bdd_graph.get_node(starting_node_name)
    final_node = node2
    if algorithm == "prim":
        prim(bdd_graph, starting_node)
    elif algorithm == "dijkstra":
        dijkstra(bdd_graph, starting_node)
    elif algorithm == "tsm":
        tsm(bdd_graph, starting_node)
##############################

## Main function
if __name__ == "__main__":

    try:
        filename = sys.argv[1]
        algorithm = sys.argv[2]
        starting_node_name = sys.argv[3]
        load_file(filename, algorithm, starting_node_name)
    except:
        filename = "dijkstra_test.txt"
        algorithm = "dijkstra"
        starting_node_name = 7
        print ('Testing with main arguments: \nFile: {}\nAlgorithm: {}\nStarting Node: {}\n'.format(filename, algorithm, starting_node_name))
        load_file(filename, algorithm, starting_node_name)