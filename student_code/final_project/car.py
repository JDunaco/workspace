from pathfinding import find_shortest_path
from graph import find_nearest_vertex

class Car:
    def __init__(self, car_id, location):
        self.id = car_id
        self.location = (location)
        self.assigned_rider = None
        self.status = "available"  # "available" | "en_route_to_pickup" | "en_route_to_destination"
        self.route = None          # NEW: stores the planned path (list of nodes)
        self.route_time = None     # NEW: stores the total travel time for that path
        self.busy_start_time = None
        self.total_busy_time = 0
        self.trips_completed = 0

    def calculate_route(self, destination, graph):
        start_vertex = find_nearest_vertex(self.location, graph.node_coordinates)
        end_vertex = find_nearest_vertex(destination, graph.node_coordinates)

        path, distance = find_shortest_path(graph.adj_list, start_vertex, end_vertex)

        self.route = path
        self.route_time = distance

        if path is None:
            print(f"Car {self.id}: No route found from {self.location} to {destination}.")
        else:
            print(f"Car {self.id}: Route calculated - {path} (time: {distance})")

        return self.route, self.route_time

    def __str__(self):       
        return f"Car {self.id} is no where. - Status: {self.status}"