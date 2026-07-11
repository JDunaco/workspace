from car import Car
from rider import Rider

class Simulation:

    def __init__(self):
        # initialize dictionaries
        self.car_data = {} # car_data {"id" : "Car_Class_Object"}
        self.rider_data = {} # rider_data {"id" : "Rider_Class_Object"}

    # New Driver info
    def new_car(self, id, location):
        car_to_add = Car(id, location)
        self.car_data[f"Car-{id}"] = car_to_add
        print(f"New Car added to our system : {self.car_data[f'Car-{id}'].id} at {self.car_data[f'Car-{id}'].location}")

    # New Rider Info
    def new_rider(self, id, location, destination):
        self.rider_data[f'Rider-{id}'] = Rider(id, location, destination)
        print(f"New Rider added to our system : {self.rider_data[f'Rider-{id}'].id} at {self.rider_data[f'Rider-{id}'].starting_location}")

    def display_info(self):
        print("\nDrivers in Service")
        for car, details in self.car_data.items():
            print(f"ID: {car}, Details: {details.__str__()}")
        print("\n\nRiders in System")
        for rider, details in self.rider_data.items():
            print(f"ID: {rider}, Details: {details.__str__()}")
        print("\n\n All users in system found")