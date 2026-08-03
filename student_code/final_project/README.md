Project Name : Jordan's RideShare Program

Purpose/Design : To create an app that can complete with Uber/Lyft in utility but provide more ease of use to the users and drivers. This is going to be achieved by a simplistic approach that'll allow users and 
drivers to easily find their next ride and provide clear data to both users on their client/driver.

How to run : Concurrently there is a test.py, test2.py, test3.py or test_quadtree files that contains initially testing, later down the road there will be a proper system that'll allow intuitive control in how to use the app. This will eventually be contained into a main program file, but for now it's testing based. Test 1 is for the overall dictionary testing, Test 2 is for the map layout using Graphs, Test 3 is for testing Dijsktra's algorithm being implented, while test_quadtree is to test quadtrees and how it'll possibly be implented withing my app.

Dependencies : N/A for this iteration

Map Data Format : 
    the map.csv file is where we store our road points. 
    They work with the process of two way street:
    (Intersection A (A), Intersection B (B), with the time to get there or the weight)
    (Intersection B (B), Intersection A (A), time to get there)
    One Way 
    (Intersection A (A), Intersetion C (C), time to get there)

Dijkkstra's Algorithm: 
    Dijkstra's Algoritm is used in this program as a baseline for how we will go about finding the shortest distance, with a few additions to the algoritm to match our needs, we plan on having a live updating map to have changing nodes to make sure we can adjust for construction and flow of traffic.

Quadtree Data Structure : 
    The Quadtree structure will be implemented with the purpose of locating the nearest driver when a rider requests a ride. We chose Quadtrees for it's efficiency for processing compared to other methods to allow our users the fastest response time. The current test script is ran with :
    cd (saved file path)/student_code/final_project then running python3 test_quadtree.py 
    This will showcase a random point getting chosen and how it compares to brute-forcing distance calculations. The reason it's faster is because of the node system it uses with breaking each section down into 4 quadrants and then keep breaking it down until we get our nodes within the shortest range and not having to calculate three other quadrants that would be outside of our scope unless there is no available driver within our immediate vicinity.

## Simulation Engine Prototype

This milestone implements the core **discrete-event simulation engine** that will drive the final ride-sharing simulator. Rather than tracking cars and riders continuously, the simulation jumps from one significant event to the next (a dispatch, a pickup, a dropoff), updating state only when something actually happens.

### How the event loop works

- All upcoming events are stored in a **min-heap** (`heapq`), ordered by timestamp, so the earliest event is alway processed next.
- Each event is an `Event(timestamp, event_type, metadata)` object, where
  `event_type` is either `"RIDE_REQUEST"` or `"ARRIVAL"`.
- The `run()` method contains the main loop: it pops the next event off the heap, advances `self.current_time` to that event's timestamp, and dispatches to the appropriate handler:
  - `"RIDE_REQUEST"` → `handle_rider_request()`
  - `"ARRIVAL"` → `handle_arrival()`
- `handle_rider_request()` finds the nearest available car (via a brute-force distance scan), links the car to the rider (`car.assigned_rider = rider`), and schedules a future `"ARRIVAL"` event for the pickup.
- `handle_arrival()` checks the car's `status` to determine whether the arrival is a **pickup** (`"en_route_to_pickup"`) or a **dropoff** (`"en_route_to_destination"`), updates the car's location and both car/rider statuses accordingly, and — for a pickup — schedules the next `"ARRIVAL"` event for the dropoff.

### Purpose of this prototype

This milestone intentionally uses **placeholder logic** in place of the project's advanced components:

- `find_closest_car_brute_force()` stands in for the Quadtree-based matching that will be added later.
- `calculate_travel_time()` uses simple Manhattan distance instead of the Dijkstra pathfinding built in an earlier milestone.

The goal here is to prove the **event-driven engine** itself — event scheduling, state transitions, and correct time-ordering — works end-to-end before swapping in the high-performance components in the final milestone.

## How to Run

Run the simulation prototype with:

```bash
python simulation.py
```

This will:
1. Load the map from `map.csv`
2. Create a few cars and riders (see the `if __name__ == "__main__":` block in `simulation.py` for the example setup)
3. Run the event loop and print a chronological log of dispatches, pickups, and dropoffs to the console