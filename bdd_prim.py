
## Stores the BDD graph nodes

class BddGraph:
    def __init__(self):
        self.nodes = {}

    def print_nodes(self):
        print(self.nodes)
        for node_name in self.nodes:
            print (node_name, ':' , [[x, self.nodes[node_name].get_connections()[x][1]] for x in self.nodes[node_name].get_connections()])

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

## Defines nodes and properties inside the BDD graph

class BddNode:
    def __init__(self, name):
        self.name = name
        self.connections = {name : [self, 0]}

    def connect(self, node, distance):
        self.connections[node.get_name()] = [node, distance]

    def disconnect(self, node, distance):
        self.connections.remove(node)

    def get_connections(self):
        return self.connections

    def get_name(self):
        return self.name


##############################

if __name__ == "__main__":

    bdd_structure = []

    with open("bdd.txt", "r") as file:
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
            node2.connect(node1, connection[2])
        except:
            print('Error creating connection', connection)


    bdd_graph.print_nodes()