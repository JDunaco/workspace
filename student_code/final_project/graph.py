import csv
import collections

def find_nearest_vertex(point, node_coordinates):
        if not node_coordinates:
            raise ValueError("find_nearest_vertex: no graph vertices have been loaded.")

        px, py = point
        best_id, best_dist_sq = None, float('inf')
        for node_id, (nx, ny) in node_coordinates.items():
            dist_sq = (nx - px) ** 2 + (ny - py) ** 2
            if dist_sq < best_dist_sq:
                best_dist_sq = dist_sq
                best_id = node_id
        return best_id

class Graph:
    """
    Graph class to control the map layout
    """
    def __init__(self):
        self.adj_list = collections.defaultdict(list)
        self.node_coordinates = {}
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

    def load_map_data(self, filename):
        print(f"Loading map from {filename}...")
        try:
            with open(filename, 'r') as f:
                for line in f:
                    if line.startswith('#') or not line.strip():
                        continue

                    parts = line.strip().split(',')
                    start_id, start_x, start_y, end_id, end_x, end_y, weight = parts

                    #Store the coordinates for both nodes
                    self.node_coordinates[start_id] = (float(start_x), float(start_y))
                    self.node_coordinates[end_id] = (float(end_x), float(end_y))

                    # Store the edge for the undirected graph
                    self.adj_list[start_id].append((end_id, float(weight)))
                    self.adj_list[end_id].append((start_id, float(weight)))
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