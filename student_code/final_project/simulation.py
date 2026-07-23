from car import Car
from rider import Rider
from graph import Graph

class Simulation:

    def __init__(self, map_filename):
        # initialize dictionaries
        self.car_data = {} # car_data {"id" : "Car_Class_Object"}
        self.rider_data = {} # rider_data {"id" : "Rider_Class_Object"}
        self.mapData = Graph()
        self.mapData.load_from_file(map_filename)
        self.map = self.mapData.get_list()
        

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

    # New Rider Info
    def new_rider(self, id, location, destination):
        self.rider_data[f'Rider-{id}'] = Rider(id, location, destination)
        print(f"New Rider added to our system : {self.rider_data[f'Rider-{id}'].id} at {self.rider_data[f'Rider-{id}'].starting_location}")

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