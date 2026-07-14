import csv
class Graph:
    """
    Graph class to control the map layout
    """
    def __init__(self):
        self.adj_list = {}
        print("Created Graph class")

    def add_vertex(self, vertex):
        if vertex not in self.adj_list:
            self.adj_list[vertex] = []
    
    def add_edge(self, v1, v2, weight):
        self.add_vertex(v1)
        self.add_vertex(v2)
        self.adj_list[v1].append((v2, float(weight)))

    def get_list(self):
        return self.adj_list

    def load_from_file(self, filename):
        print(f"Loading map from {filename}...")
        try:
            with open(filename, 'r') as f:
                reader = csv.reader(f)
                for row in reader:
                    if len(row) == 3: 
                        start, end, weight = row
                        self.add_edge(start.strip(), end.strip(), weight.strip())
            print("Map loaded successfully.")
        except FileNotFoundError:
            print(f"ERROR: file '{filename}' not found.")
        except Exception as e:
            print(f"An error occured: {e}")

    def __str__(self):
        print("\n--- Map node List ---")
        for vertex, neighbors in self.adj_list.items():
            neighbor_str = ", ".join([f"({n}, {w})" for n, w in neighbors])
            print(f"{vertex} -> [{neighbor_str}]")
        print("--- Finished Printing Locations ---")