# Jordan's RideShare Simulator

A discrete-event ride-sharing simulation that dynamically generates riders,
dispatches the best available car using a Quadtree + Dijkstra matching
pipeline, and produces an integrated analytical visualization of the run.

## Installation

Requires Python 3.10+ and `matplotlib`.

```bash
pip install matplotlib
```

No other third-party dependencies. All other modules (`heapq`, `argparse`,
`random`, `itertools`, `collections`, `dataclasses`) are part of the
Python standard library.

## How to Run

```bash
python3 simulation.py --map-file city_map.csv --num-cars 5 --num-riders 50
```

### Command-line options

| Flag | Type | Default | Description |
|---|---|---|---|
| `--map-file` | str | `city_map.csv` | Path to the unified 7-column map CSV. |
| `--max-time` | float | `None` | Stop generating new riders once `current_time` reaches this value. |
| `--num-riders` | int | `None` | Stop generating new riders once this many have been created. |
| `--num-cars` | int | `5` | Number of cars to initialize (5 for the debugging map, 100 for the production map, per the assignment spec). |
| `--candidate-count` | int | `5` | How many nearest available cars the Quadtree returns per rider request (`DEFAULT_CANDIDATE_COUNT`). |
| `--random-seed` | int | `None` | Seed for reproducible runs (car placement, rider generation, arrival timing). |

If both `--max-time` and `--num-riders` are supplied, rider **generation**
stops as soon as either limit is reached. This does **not** cut off
in-progress trips — any car already en route to a pickup or dropoff
finishes normally, and the simulation's reported time span reflects the
last event actually processed, not the generation cutoff.

### Examples

```bash
# Debugging map, default 5 cars, run until 50 riders have been generated
python3 simulation.py --map-file city_map.csv --num-riders 50

# Production map, 100 cars, run for 3600 simulated seconds, reproducible
python3 simulation.py --map-file city_map.csv --num-cars 100 --max-time 3600 --random-seed 42

# Wider candidate pool per match
python3 simulation.py
python3 simulation.py --map-file city_map.csv --candidate-count 8
```

## Map File Format

A single unified `city_map.csv`. Each row represents one road and has
seven comma-separated values:

start_node_id,start_x,start_y,end_node_id,end_x,end_y,weight


`weight` is the travel time along that road. Roads are treated as
undirected — loading a row automatically creates edges in both
directions. `Graph.load_map_data()` populates two structures from this
single file:

- `adjacency_list` — the road network Dijkstra runs on
- `node_coordinates` — the `(x, y)` position of every node, which is what
  lets the Quadtree's raw coordinates get "snapped" onto the graph

## Architecture

| Component | Responsibility |
|---|---|
| `Graph` (`graph.py`) | Road network topology + node coordinates. Loads the unified map, and exposes `find_nearest_vertex(point, node_coordinates)` to snap any `(x, y)` point to its closest graph node. |
| `Quadtree` (`quadtree.py`) | Spatial index of currently *available* cars. Returns up to `k` geographically nearest candidates; does not know about roads or travel time. |
| Dijkstra (`pathfinding.py`) | Computes actual road-network travel time between two graph nodes. |
| `Simulation` (`simulation.py`) | Owns simulated time, the event queue, and all car/rider state. Ties the above together: Quadtree narrows candidates, Dijkstra picks the winner. |

The Quadtree identifies *promising* candidates by straight-line distance;
Dijkstra makes the *final* decision by actual road travel time. The two
are not the same thing — the geographically closest car is not always the
fastest to reach the rider.

## Event System

Every event is a plain 4-tuple, not an object:

```python
(timestamp, sequence_number, event_type, data)
```

`sequence_number` comes from `itertools.count()` and is strictly
increasing across every event ever scheduled. It exists purely as a
tie-breaker: since Python's `heapq` compares tuples element-by-element,
two events at the *exact same* `timestamp` will never fall through to
comparing `data` directly (which could be a `Car` or `Rider` object with
no defined ordering, and would raise a `TypeError`). All events are
pushed through one helper:

```python
def schedule_event(self, timestamp, event_type, data):
    heapq.heappush(self.events, (timestamp, next(self.event_sequence), event_type, data))
```

### Event types

- `"RIDER_REQUEST"` — a new or re-triggered rider request; also
  responsible for scheduling the *next* `RIDER_REQUEST` (see "Dynamic
  Rider Generation" below).
- `"PICKUP_ARRIVAL"` — a dispatched car has reached the rider.
- `"DROPOFF_ARRIVAL"` — a car has reached the rider's destination.

`run()` drains the heap until it's empty — it does **not** stop early at
`--max-time`. That check lives entirely in rider *generation*
(`generation_limit_reached()`), so any trip already dispatched is allowed
to finish even if it completes after the nominal cutoff.

## Car and Rider State Model

All physical locations — `car.location`, `rider.start_location`,
`rider.destination` — are `(x, y)` coordinate tuples, never graph node
IDs. Node IDs only exist transiently, inside Dijkstra calls, via
`find_nearest_vertex()`.

**Car** state progression:

available -> en_route_to_pickup -> en_route_to_destination -> available


**Rider** state progression:

waiting -> in_car -> completed

A rider may also end in `unmatched` (no car was ever dispatched — see
below) or `unsuccessful` (a car was dispatched and pickup happened, but
the destination turned out unreachable).

## Dynamic Rider Generation

The simulation does not seed a static list of riders. It starts with a
single `RIDER_REQUEST` at `t=0`, and every time that event is processed,
it schedules the *next* one at `current_time + random.expovariate(1.0 /
MEAN_ARRIVAL_TIME)` — a daisy chain, not a queue. This happens
**regardless** of whether the current rider was successfully matched, so
a temporary shortage of cars never stalls the whole simulation. The next
request is only scheduled if doing so wouldn't exceed `--max-time` and the
overall generation limit hasn't already been reached.

## Matching Workflow

For every `RIDER_REQUEST`:

1. **Quadtree** — `available_car_quadtree.find_k_nearest(rider_point,
   k=candidate_count)` returns up to `k` (default **5**, set via
   `--candidate-count`) geographically nearest available cars.
2. **Dijkstra** — for *every* candidate returned (not just the first
   reachable one), the car's location and the rider's start location are
   each snapped to their nearest graph vertex via `find_nearest_vertex()`,
   and Dijkstra computes the real travel time between them.
3. **Selection** — the reachable candidate with the lowest travel time
   wins. Ties are broken deterministically by Quadtree result order
   (first-seen candidate wins) rather than left to chance.
4. **Dispatch** — the winning car is removed from availability, both car
   and rider state update, and a `PICKUP_ARRIVAL` is scheduled using the
   real Dijkstra pickup time (never a placeholder distance calculation).

## Availability Synchronization

Three structures track which cars are currently available, and must
always agree on membership:

- `available_cars` — `{car_id: Car}`, for direct lookup
- `available_car_points` — `{car_id: Point}`, retaining the *exact* Point
  object inserted into the Quadtree (needed for identity-based removal)
- `available_car_quadtree` — the spatial index itself

All changes go through two methods, never touched directly elsewhere:

- **`add_available_car(car)`** — creates a fresh, immutable `Point` from
  the car's current location, inserts it into the Quadtree, and only then
  updates both dictionaries. If insertion fails (car is outside the map
  boundary) or the car ID is already present, nothing is written —
  no partial state.
- **`remove_available_car(car)`** — looks up the car's exact `Point` by
  ID, removes it from the Quadtree by object identity (`is`, not
  coordinate equality — two different cars can share coordinates), and
  only then deletes both dictionary entries.

A car is never reinserted at a stale location: its old `Point` is
discarded at dispatch, and `add_available_car()` always builds a brand
new one from `car.location` at the moment of reinsertion (i.e. at the
dropoff location, not the pickup location).

## Policy: Unavailable Cars and Unreachable Routes

- **No available cars at request time** → the rider is marked
  `"unmatched"` and recorded in `self.unmatched_riders`.
- **All Quadtree candidates unreachable via Dijkstra** → same outcome,
  same list. (Geographically near ≠ reachable, if the graph is
  disconnected.)
- **Destination becomes unreachable after pickup** → the rider is marked
  `"unsuccessful"` (tracked separately, in `self.unsuccessful_trips`,
  since it's a distinct failure mode — the rider *was* picked up). No
  event is ever scheduled at `float('inf')`. The car's elapsed busy time
  is still recorded, `assigned_rider` is cleared, and the car is returned
  to availability at its current (pickup) location via
  `add_available_car()`.

## Metrics

Computed once, at the end of `run()`, via `analyze_results()`:

- **Riders generated** — total `RIDER_REQUEST`s created.
- **Trips completed** — length of `trip_log` (successful dropoffs).
- **Unmatched riders** — never got a car.
- **Unsuccessful trips** — got a car, but the destination was unreachable.
- **Avg wait time** — mean of `pickup_time - request_time` across
  completed trips.
- **Avg trip duration** — mean of `dropoff_time - pickup_time` across
  completed trips.
- **Driver utilization** —
  `total busy time across all cars / (number of cars × simulation span)`,
  where *simulation span* is the timestamp of the last event actually
  processed (not the generation cutoff), so utilization correctly
  accounts for trips that finish after rider generation stops.
- **Trips completed per car** — `{car_id: trips_completed}`, drawn from
  every car ever created (`car_data`), not just currently-idle ones.

## Visualization

`create_visualization()` produces a single `simulation_summary.png`:

- **Left, large panel** — scatter plot of every graph node (faint gray)
  plus every car's final location, color-coded green (available) or red
  (busy).
- **Top right** — the metrics listed above, rendered as text.
- **Middle right** — bar chart of trips completed per car.
- **Bottom right** — histogram of rider wait times.

## Running Tests / Demonstration

```bash
# Quadtree correctness: brute-force cross-check on 5,000 random points
python3 test_quadtree.py

# Full simulation, small scale (debugging map)
python3 simulation.py --map-file city_map.csv --num-cars 5 --num-riders 30 --random-seed 1

# Full simulation, production scale
python3 simulation.py --map-file production_map.csv --num-cars 100 --max-time 3600
```

`test1.py`, `test2.py`, and `test3.py` are retained from earlier
milestones (early dictionary/graph/Dijkstra checks) but predate the final
architecture — they use the old 3-column `map.csv` and an outdated
`Simulation()` signature, so they are not expected to run against the
current codebase. They're kept for historical reference only; the
authoritative tests are `test_quadtree.py` and a real `simulation.py` run.