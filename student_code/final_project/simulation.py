import heapq
from itertools import count
from car import Car
from rider import Rider
from graph import Graph, find_nearest_vertex
from quadtree import Quadtree, Point
from pathfinding import find_shortest_path
import argparse
import random
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec


MEAN_ARRIVAL_TIME = 5.0
DEFAULT_CANDIDATE_COUNT = 5
TRAVEL_SPEED_FACTOR = 2


def calculate_travel_time(start_location, end_location):
        x1, y1 = start_location
        x2, y2 = end_location
        distance = abs(x1 - x2) + abs(y1 - y2)
        return distance * TRAVEL_SPEED_FACTOR

class Simulation:

    def __init__(self, map_filename, max_time=None, num_riders=None,
                num_cars=None, candidate_count=DEFAULT_CANDIDATE_COUNT,
                random_seed=None):
        # initialize dictionaries
        self.car_data = {} # car_data {"id" : "Car_Class_Object"}
        self.rider_data = {} # rider_data {"id" : "Rider_Class_Object"}
        self.mapData = Graph()
        self.mapData.load_map_data(map_filename)
        self.map = self.mapData.get_list()
        self.available_cars = {}
        self.available_car_points = {}
        self.available_car_quadtree = self.build_quadtree_for_map()
        self.current_time = 0
        self.events = []
        self.event_sequence = count()
        self.trip_log = []
        self.rider_id_sequence = count(1)
        self.unmatched_riders = []
        self.unsuccessful_trips = []
        self.trip_log =[]

        self.max_time = max_time
        self.num_riders_limit = num_riders
        self.num_cars = num_cars if num_cars is not None else 0
        self.candidate_count = candidate_count
        self.riders_generated = 0

        if random_seed is not None:
            random.seed(random_seed)
        
        
    def build_quadtree_for_map(self):
        xs = [x for x, y in self.mapData.node_coordinates.values()]
        ys = [ y for x, y in self.mapData.node_coordinates.values()]
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(yx), max(ys)

        center_x = (min_x + max_x) / 2
        center_y = (min_y + max_y) / 2
        half_width = (max_x - min_x) / 2
        half_height = (max_y - min_y) / 2

        return Quadtree(center_x, center_y, half_width, half_height)

    def add_available_car(self, car):
        if car.id in self.available_cars or car.id in self.available_car_points:
            raise ValueError(f"add_available_car: Car-{car.id} is already available.")

        point = Point(car.location[0], car.location[1], data=car)
        inserted = self.available_car_quadtree.insert(point)

        if not inserted:
            raise ValueError(
                f"add_available_car: Car-{car.id} at {car.location} is outside the map boundary."
            )

        self.available_cars[car.id] = car
        self.available_car_points[car.id] = point
        car.status = "available"

    def dispatch_car(self, rider, best_car, best_route, best_pickup_time):
        """
        Dispatch the winning candidate, and remove from availability,
        update car/rider state, and schedule the PICKUP_ARRIVAL event.
        """
        self.remove_available_car(best_car)

        best_car.status = "en_route_to_pickup"
        best_car.assigned_rider = rider
        best_car.route = best_route
        best_car.route_time = best_pickup_time
        best_car.busy_start_time = self.current_time

        rider.status = "waiting"

        self.schedule_event(self.current_time + best_pickup_time, "PICKUP_ARRIVAL", best_car)

    def random_point_in_bounds(self):
        b = self.available_car_quadtree.boundary
        x = random.uniform(b.x - b.half_width, b.x + b.half_width)
        y = random.uniform(b.y - b.half_height, b.y + b.half_height)
        return (x, y)

    def generate_rider_request(self, schedule_time):
        """
        Creates a new Rider with random start/destination coords withing 
        the map bounds and schedules a RIDER_REQUEST event
        """
        rider_id = next(self.rider_id_sequence)
        start = self.random_point_in_bounds()
        destination = self.random_point_in_bounds()
        rider = Rider(rider_id, start, destination)
        self.riders_generated += 1
        self.schedule_event(schedule_time, "RIDER_REQUEST", rider)
        return rider

    def select_best_car(self, rider, candidate_points):
        """
        Run Dijkstra's algorithm for every Quadtree candidate, select
        the reachable car with the minimum pickup time. Ties are borken
        by Quadtree result order
        """
        rider_vertex = find_nearest_vertex(rider.start_location, self.mapData.node_coordinates)

        best_car = None
        best_route = None
        best_time = float('inf')

        for point in candidate_points:
            car = point.data
            car_vertex = find_nearest_vertex(car.location, self.mapData.node_coordinates)
            route, travel_time = find_shortest_path(self.mapData.adj_list, car_vertex, rider_vertex)

            if route is None:
                continue

            if travel_time < best_time:
                best_time = travel_time
                best_route = route
                best_car = car

        if best_car is not None:
            best_car.route = best_route
            best_car.route_time = best_time

        return best_car, best_route, best_time

    def remove_available_car(self, car):
        if car.id not in self.available_car_points:
            raise ValueError(f"remove_available_car: Car-{car.id} is not currently available.")

        point = self.available_car_points[car.id]
        removed = self.available_car_quadtree.remove(point)

        if not removed:
            raise RuntimeError(
                f"remove_available_car: Car-{car.id}'s point was not found in the Quadtree "
                "-- availability structures are out of sync."
            )

        del self.available_car_points[car.id]
        del self.available_cars[car.id]

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
        self.add_available_car(car_to_add)        # validate + register first
        self.car_data[f"Car-{id}"] = car_to_add    # only commit after success
        self.num_cars += 1
        print(f"New Car added to our system: {car_to_add.id} at {car_to_add.location}")
        return car_to_add

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
        if rider.request_time is None:
            rider.request_time = self.current_time
        
        query_point = Point(rider.start_location[0], rider.start_location[1])
        candidate_points = self.available_car_quadtree.find_k_nearest(
            query_point, k=self.candidate_count
        )

        if not candidate_points:
            rider.status = "unmatched"
            self.unmatched_riders.append(rider)
            print(f"Rider {rider.id}: no available cars -- marked unmatched.")
        else:
            best_car, best_route, best_time = self.select_best_car(rider, candidate_points)
            if best_car is None:
                rider.status = "unmatched"
                self.unmatched_riders.append(rider)
                print(f"Rider {rider.id}: all {len(candidate_points)} candidates unreachable -- marked unmatched.")
            else:
                self.dispatch_car(rider, best_car, best_route, best_time)

        next_time = self.current_time + random.expovariate(1.0 / MEAN_ARRIVAL_TIME)
        would_exceed_max_time = self.max_time is not None and next_time > self.max_time

        if not self.generation_limit_reached() and not would_exceed_max_time:
            self.generate_rider_request(next_time)

    def generation_limit_reached(self):
        if self.max_time is not None and self.current_time >= self.max_time:
            return True
        if self.num_riders_limit is not None and self.riders_generated >= self.num_riders_limit:
            return True
        return False

    def handle_pickup_arrival(self, car):
        rider = car.assigned_rider
        if rider is None:
            raise ValueError(f"handle_pickup_arrival: Car-{car.id} has no assigned_rider.")

        car.location = rider.start_location
        car.status = "en_route_to_destination"
        rider.status = "in_car"
        rider.pickup_time = self.current_time

        wait_time = rider.pickup_time - rider.request_time
        print(f"TIME {self.current_time}: Car {car.id} picked up Rider {rider.id} (wait_time={wait_time})")

        route, trip_time = car.calculate_route(rider.destination, self.mapData)

        if route is None:
            # Recovery policy: destination unreachable after pickup.
            print(f"TIME {self.current_time}: Rider {rider.id}'s destination is unreachable -- recovering.")
            rider.status = "unsuccessful"
            self.unsuccessful_trips.append(rider)

            car.total_busy_time += (self.current_time - car.busy_start_time)
            car.assigned_rider = None

            self.add_available_car(car)
            return

        self.schedule_event(self.current_time + trip_time, "DROPOFF_ARRIVAL", car)


    def handle_dropoff_arrival(self, car):
        rider = car.assigned_rider
        if rider is None:
            raise ValueError(f"handle_dropoff_arrival: Car-{car.id} has no assigned_rider.")

        car.location = rider.destination
        rider.status = "completed"
        rider.dropoff_time = self.current_time
        car.assigned_rider = None

        self.log_trip_data(rider)

        car.total_busy_time += (self.current_time - car.busy_start_time)
        car.trips_completed += 1

        self.add_available_car(car)

    def create_visualization(self, results, output_path="simulation_summary.png"):
        """ Step 18: single integrated PNG -- car locations + metrics + charts. """
        fig = plt.figure(figsize=(16, 9))
        gs = GridSpec(3, 2, figure=fig, width_ratios=[2, 1], height_ratios=[1, 1, 1])

        # --- Left: large map of final car locations ---
        ax_map = fig.add_subplot(gs[:, 0])

        node_coordinates = self.mapData.node_coordinates
        if node_coordinates:
            xs = [x for x, y in node_coordinates.values()]
            ys = [y for x, y in node_coordinates.values()]
            ax_map.scatter(xs, ys, c="lightgray", s=10, zorder=1, label="Graph nodes")

        available_x = [c.location[0] for c in self.car_data.values() if c.status == "available"]
        available_y = [c.location[1] for c in self.car_data.values() if c.status == "available"]
        busy_x = [c.location[0] for c in self.car_data.values() if c.status != "available"]
        busy_y = [c.location[1] for c in self.car_data.values() if c.status != "available"]

        ax_map.scatter(available_x, available_y, c="tab:green", s=60, zorder=2, label="Available cars")
        ax_map.scatter(busy_x, busy_y, c="tab:red", s=60, zorder=2, marker="^", label="Busy cars")

        ax_map.set_title("Final Car Locations")
        ax_map.set_xlabel("X")
        ax_map.set_ylabel("Y")
        ax_map.legend(loc="upper right", fontsize=8)
        ax_map.set_aspect("equal", adjustable="box")

        # --- Top right: metrics text ---
        ax_text = fig.add_subplot(gs[0, 1])
        ax_text.axis("off")

        metrics_lines = [
            f"Riders generated:   {results['total_riders_generated']}",
            f"Trips completed:    {results['total_completed']}",
            f"Unmatched riders:   {results['total_unmatched']}",
            f"Unsuccessful trips: {results['total_unsuccessful']}",
            f"Avg wait time:      {results['avg_wait_time']:.2f}s",
            f"Avg trip duration:  {results['avg_trip_duration']:.2f}s",
            f"Driver utilization: {results['driver_utilization']:.1%}",
            f"Simulation span:    {results['simulation_span']:.1f}s",
        ]
        y_pos = 0.95
        for line in metrics_lines:
            ax_text.text(0.05, y_pos, line, fontsize=11, family="monospace",
                         verticalalignment="top", transform=ax_text.transAxes)
            y_pos -= 0.12
        ax_text.set_title("Simulation Metrics", fontsize=12, fontweight="bold")

        # --- Middle right: trips completed per car ---
        ax_bar = fig.add_subplot(gs[1, 1])
        car_ids = list(results["trips_per_car"].keys())
        trip_counts = list(results["trips_per_car"].values())
        ax_bar.bar(car_ids, trip_counts, color="tab:blue")
        ax_bar.set_title("Trips Completed per Car", fontsize=10)
        ax_bar.set_xlabel("Car ID", fontsize=8)
        ax_bar.set_ylabel("Trips", fontsize=8)
        ax_bar.tick_params(labelsize=7)

        # --- Bottom right: distribution of rider wait times ---
        ax_hist = fig.add_subplot(gs[2, 1])
        wait_times = [t["wait_time"] for t in self.trip_log]
        if wait_times:
            ax_hist.hist(wait_times, bins=10, color="tab:orange", edgecolor="black")
        ax_hist.set_title("Distribution of Rider Wait Times", fontsize=10)
        ax_hist.set_xlabel("Wait time (s)", fontsize=8)
        ax_hist.set_ylabel("Count", fontsize=8)
        ax_hist.tick_params(labelsize=7)

        fig.suptitle("Ride-Sharing Simulation Summary", fontsize=16, fontweight="bold")
        fig.tight_layout(rect=[0, 0, 1, 0.96])
        fig.savefig(output_path, dpi=150)
        plt.close(fig)

        print(f"Visualization saved to {output_path}")
        return output_path

    def schedule_event(self, timestamp, event_type, data):
        """ Add event to event_queue"""
        heapq.heappush(
            self.events, 
            (timestamp, next(self.event_sequence), event_type, data),
            )

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

    def log_trip_data(self, rider):
        wait_time = rider.pickup_time - rider.request_time
        trip_duration = rider.dropoff_time - rider.pickup_time
        trip_record = {
            'rider_id': rider.id,
            'request_time': rider.request_time,
            'pickup_time': rider.pickup_time,
            'dropoff_time': rider.dropoff_time,
            # run calculations here for convenience
            'wait_time': wait_time,
            'trip_duration': trip_duration,
        }
        self.trip_log.append(trip_record)
        return trip_record

    def analyze_results(self):
        total_generated = self.riders_generated
        total_completed = len(self.trip_log)
        total_unmatched = len(self.unmatched_riders)
        total_unsuccessful = len(self.unsuccessful_trips)

        if total_completed > 0:
            avg_wait_time = sum(t["wait_time"] for t in self.trip_log) / total_completed
            avg_trip_duration = sum(t["trip_duration"] for t in self.trip_log) / total_completed
        else:
            avg_wait_time = 0
            avg_trip_duration = 0

        simulation_span = self.current_time  # final processed event time -- covers trips that finish after generation stops
        total_busy_time = sum(car.total_busy_time for car in self.car_data.values())
        if self.num_cars > 0 and simulation_span > 0:
            driver_utilization = total_busy_time / (self.num_cars * simulation_span)
        else:
            driver_utilization = 0

        trips_per_car = {car.id: car.trips_completed for car in self.car_data.values()}

        results = {
            "total_riders_generated": total_generated,
            "total_completed": total_completed,
            "total_unmatched": total_unmatched,
            "total_unsuccessful": total_unsuccessful,
            "avg_wait_time": avg_wait_time,
            "avg_trip_duration": avg_trip_duration,
            "driver_utilization": driver_utilization,
            "trips_per_car": trips_per_car,
            "simulation_span": simulation_span,
        }

        print("\n--- Simulation Results ---")
        print(f"Riders generated:     {total_generated}")
        print(f"Trips completed:      {total_completed}")
        print(f"Unmatched riders:     {total_unmatched}")
        print(f"Unsuccessful trips:   {total_unsuccessful}")
        print(f"Avg wait time:        {avg_wait_time:.2f}")
        print(f"Avg trip duration:    {avg_trip_duration:.2f}")
        print(f"Driver utilization:   {driver_utilization:.2%}")
        print(f"Trips per car:        {trips_per_car}")
        print(f"Simulation span:      {simulation_span}")

        return results


    def new_rider(self, id, location, destination, request_time=0):
        rider = Rider(id, location, destination)
        self.rider_data[f'Rider-{id}'] = rider
        print(f"New Rider added to our system : {rider.id} at {rider.starting_location}")
        self.schedule_event(Event(request_time, "RIDE_REQUEST", rider))

    def run(self):
        print("--- Running Simulation for Rideshare ---")
        if not self.generation_limit_reached():
            self.generate_rider_request(0)

        # Event System
        while self.events:
            timestamp, sequence_number, event_type, data = heapq.heappop(self.events)
            self.current_time = timestamp

            if event_type == "RIDER_REQUEST":
                self.handle_rider_request(data)
            elif event_type == "PICKUP_ARRIVAL":
                self.handle_pickup_arrival(data)
            elif event_type == "DROPOFF_ARRIVAL":
                self.handle_dropoff_arrival(data)
            else:
                raise ValueError(f"Unknown event type: {event_type}")
        results = self.analyze_results()
        self.create_visualization(results)   
        print(f"{self.trip_log}")
        self.analyze_results()   

def build_parser():
        parser = argparse.ArgumentParser(description="Ride-sharing discrete-event simulator")
        parser.add_argument("--max-time", type=float, default=None)
        parser.add_argument("--num-riders", type=int, default=None)
        parser.add_argument("--num-cars", type=int, default=None)
        parser.add_argument("--candidate-count", type=int, default=DEFAULT_CANDIDATE_COUNT)
        parser.add_argument("--random-seed", type=int, default=None)
        parser.add_argument("--map-file", type=str, default="city_map.csv")
        return parser

if __name__ == "__main__":
    args = build_parser().parse_args()
    sim = Simulation(
        args.map_file,
        max_time=args.max_time,
        num_riders=args.num_riders,
        num_cars=args.num_cars,
        candidate_count=args.candidate_count,
        random_seed=args.random_seed,
    )
    sim.run()

# Other Space for additions (add stuff above this line)