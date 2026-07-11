class Car:
    def __init__(self, car_id, location):
        self.id = car_id
        self.location = (location)
        self.status = "available" # Set to available, other states are going to be "unavailable", "going_to_pickup", "going_to_destination"
        self.destination = "None" # Going to be (x,y) coords

    def __str__(self):
        if self.destination == "None":
            return f"Car {self.id} is no where. - Status: {self.status}"
        else:
            return f"Car {self.id} is at {self.destination} - Status: {self.status}"