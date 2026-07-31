import math
import random

from quadtree import Quadtree

MAP_SIZE = 1000
NUM_POINTS = 5000


def brute_force_nearest(points, query_point):
    """
    Simple O(N) linear scan used as the ground truth to verify the
    Quadtree's find_nearest() result against.
    """
    best_point = None
    best_distance = float("inf")

    for point in points:
        dx = point[0] - query_point[0]
        dy = point[1] - query_point[1]
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < best_distance:
            best_distance = distance
            best_point = point

    return best_point, best_distance


def main():
    # Boundary centered on the map with half-width/half-height of MAP_SIZE / 2
    # so the tree covers the full 1000x1000 area.
    qtree = Quadtree(MAP_SIZE / 2, MAP_SIZE / 2, MAP_SIZE / 2, MAP_SIZE / 2, capacity=4)

    points = []
    for _ in range(NUM_POINTS):
        p = (random.uniform(0, MAP_SIZE), random.uniform(0, MAP_SIZE))
        points.append(p)
        qtree.insert(p)

    query_point = (random.uniform(0, MAP_SIZE), random.uniform(0, MAP_SIZE))

    quadtree_result = qtree.find_nearest(query_point)
    brute_force_result, brute_force_distance = brute_force_nearest(points, query_point)

    print(f"Inserted {NUM_POINTS} random points into a {MAP_SIZE}x{MAP_SIZE} Quadtree.")
    print(f"Query point: {query_point}")
    print(f"Quadtree find_nearest() result: {quadtree_result}")
    print(f"Brute-force nearest result:     {brute_force_result} (distance: {brute_force_distance:.4f})")

    assert quadtree_result == brute_force_result, (
        "MISMATCH: Quadtree result does not match brute-force result."
    )

    print("\nSUCCESS: Quadtree find_nearest() matches brute-force search.")


if __name__ == "__main__":
    main()