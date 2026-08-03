import heapq
from dataclasses import dataclass, field
from typing import Any
from car import Car
from rider import Rider
from graph import Graph

TRAVEL_SPEED_FACTOR = 2

@dataclass(order=True)
class Event:
    """ Event Class for the simulation """
    timestamp: int
    event_type: str
    metadata: Any = field(compare=False)

def calculate_travel_time(start_location, end_location):
        x1, y1 = start_location
        x2, y2 = end_location
        distance = abs(x1 - x2) + abs(y1 - y2)
        return distance * TRAVEL_SPEED_FACTOR

class Simulation:

    def __init__(self, map_filename):
        # initialize dictionaries
        self.car_data = {} # car_data {"id" : "Car_Class_Object"}
        self.rider_data = {} # rider_data {"id" : "Rider_Class_Object"}
        self.mapData = Graph()
        self.mapData.load_from_file(map_filename)
        self.map = self.mapData.get_list()
        self.current_time = 0
        self.event_queue = []
        
        

    def calculate_route(self, car_id, destination):
        car_key = f"Car-{car_id}"
        if car_key not in self.car_data:
            print(f"ERROR: {car_key} not found in system.")
            return
        
        car = self.car_data[car_key]
        car.calculate_route(destination, self.map)

        print(f"Route calculated for {car_key}: {car.route} (time: {car.route_time})")

    # New Driver info
    def new_car(self, id, location):
        car_to_add = Car(id, location)
        self.car_data[f"Car-{id}"] = car_to_add
        print(f"New Car added to our system : {self.car_data[f'Car-{id}'].id} at {self.car_data[f'Car-{id}'].location}")


    # Add nodes to map
    def add_map_paths(self, start, end, travel_time):
        self.mapData.add_edge(start, end, travel_time)
        self.map = self.mapData.get_list()

    def display_info(self, test_value):

        if test_value == 1:
            print("\nDrivers in Service")
            for car, details in self.car_data.items():
                print(f"ID: {car}, Details: {details.__str__()}")
            print("\n\nRiders in System")
            for rider, details in self.rider_data.items():
                print(f"ID: {rider}, Details: {details.__str__()}")
            print("\n\n All users in system found")
        elif test_value == 2:
            self.mapData.__str__()

    def handle_rider_request(self, rider):
        car = self.find_closest_car_brute_force(rider.starting_location)
        if car is None:
            print(f"TIME {self.current_time}: No available car for RIDER {rider.id}")
            return

        car.assigned_rider = rider
        car.status = "en_route_to_pickup"

        pickup_duration = calculate_travel_time(car.location, rider.starting_location)
        self.schedule_event(Event(self.current_time + pickup_duration, "ARRIVAL", car))

        print(f"TIME {self.current_time}: CAR {car.id} dispatched to RIDER {rider.id}")


    def handle_arrival(self, car):
        rider = car.assigned_rider

        if car.status == "en_route_to_pickup":
            print(f"TIME {self.current_time}: CAR {car.id} picked up RIDER {rider.id}")
            car.location = rider.starting_location
            car.status = "en_route_to_destination"
            rider.status = "in_car"

            dropoff_duration = calculate_travel_time(car.location, rider.destination)
            self.schedule_event(Event(self.current_time + dropoff_duration, "ARRIVAL", car))

        elif car.status == "en_route_to_destination":
            print(f"TIME {self.current_time}: CAR {car.id} dropped off RIDER {rider.id}")
            car.location = rider.destination
            car.status = "available"
            rider.status = "completed"
            car.assigned_rider = None

    def schedule_event(self, event):
        """ Add event to event_queue"""
        heapq.heappush(self.event_queue, event)

    def find_closest_car_brute_force(self, rider_location):
        rx, ry = rider_location
        best_car = None
        min_dist_sq = float('inf')
        for car in self.car_data.values():
            if car.status != "available":
                continue
            cx, cy = car.location
            dist_sq = (cx - rx)**2 + (cy - ry)**2
            if dist_sq < min_dist_sq:
                min_dist_sq = dist_sq
                best_car = car
        return best_car


    def new_rider(self, id, location, destination, request_time=0):
        rider = Rider(id, location, destination)
        self.rider_data[f'Rider-{id}'] = rider
        print(f"New Rider added to our system : {rider.id} at {rider.starting_location}")
        self.schedule_event(Event(request_time, "RIDE_REQUEST", rider))

    def run(self):
        print("--- Running Simulation for Rideshare ---")
        # Event System
        while self.event_queue:
            event = heapq.heappop(self.event_queue)
            self.current_time = event.timestamp

            if event.event_type == "RIDE_REQUEST":
                self.handle_rider_request(event.metadata)
            elif event.event_type == "ARRIVAL":
                self.handle_arrival(event.metadata)


if __name__ == "__main__":
    sim = Simulation("map.csv")
    sim.new_car(1, (0, 0))
    sim.new_car(2, (20, 20))
    sim.new_rider(1, (2, 3), (10, 10), request_time=0)
    sim.new_rider(2, (15, 18), (5, 5), request_time=3)
    sim.run()

# Other Space for additions (add stuff above this line)