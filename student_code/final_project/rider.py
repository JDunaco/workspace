class Rider:
    def __init__(self, rider_id, start_location, destination):
        self.id = rider_id
        self.starting_location = start_location
        self.destination = destination
        self.status = "waiting" # set for "waiting", "in_car", "completed"

    def __str__(self):
        if self.status == "waiting":
            return f"Rider {self.id} is at {self.starting_location} waiting for a ride to {self.destination}"
        elif self.status == "in_car":
            return f"Rider {self.id} is en route to {self.destination}."
        else :
            return f"Rider {self.id} has completed their ride and arrived at {self.destination}."