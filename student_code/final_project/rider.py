class Rider:
    def __init__(self, rider_id, starting_location, destination):
        self.id = rider_id
        self.request_time = None
        self.pickup_time = None
        self.dropoff_time = None
        self.start_location = starting_location
        self.destination = destination
        self.status = "waiting" # set for "waiting", "in_car", "completed"

    def __str__(self):
        if self.status == "waiting":
            return f"Rider {self.id} is at {self.start_location} waiting for a ride to {self.destination}"
        elif self.status == "in_car":
            return f"Rider {self.id} is en route to {self.destination}."
        else :
            return f"Rider {self.id} has completed their ride and arrived at {self.destination}."