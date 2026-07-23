from pathfinding import find_shortest_path

class Car:
    def __init__(self, car_id, location):
        self.id = car_id
        self.location = (location)
        self.status = "available"  # other states: "unavailable", "going_to_pickup", "going_to_destination"
        self.destination = "None"  # Going to be (x,y) coords
        self.route = None          # NEW: stores the planned path (list of nodes)
        self.route_time = None     # NEW: stores the total travel time for that path

    def calculate_route(self, destination, graph):
        path, distance = find_shortest_path(graph, self.location, destination)

        self.route = path
        self.route_time = distance

        if path is None:
            print(f"Car {self.id}: No route found from {self.location} to {destination}.")
        else:
            print(f"Car {self.id}: Route calculated - {path} (time: {distance})")

    def __str__(self):
        if self.destination == "None":
            return f"Car {self.id} is no where. - Status: {self.status}"
        else:
            return f"Car {self.id} is at {self.destination} - Status: {self.status}"