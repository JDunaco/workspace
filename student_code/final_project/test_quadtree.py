import math
import random

from quadtree import Quadtree, Point   # import Point too

MAP_SIZE = 1000
NUM_POINTS = 5000


def brute_force_nearest(points, query_point):
    best_point = None
    best_distance = float("inf")

    for point in points:
        dx = point.x - query_point.x    # .x / .y instead of [0] / [1]
        dy = point.y - query_point.y
        distance = math.sqrt(dx * dx + dy * dy)
        if distance < best_distance:
            best_distance = distance
            best_point = point

    return best_point, best_distance


def main():
    qtree = Quadtree(MAP_SIZE / 2, MAP_SIZE / 2, MAP_SIZE / 2, MAP_SIZE / 2, capacity=4)

    points = []
    for _ in range(NUM_POINTS):
        p = Point(random.uniform(0, MAP_SIZE), random.uniform(0, MAP_SIZE))   # wrap in Point
        points.append(p)
        qtree.insert(p)

    query_point = Point(random.uniform(0, MAP_SIZE), random.uniform(0, MAP_SIZE))

    quadtree_result = qtree.find_nearest(query_point)
    brute_force_result, brute_force_distance = brute_force_nearest(points, query_point)

    print(f"Inserted {NUM_POINTS} random points into a {MAP_SIZE}x{MAP_SIZE} Quadtree.")
    print(f"Query point: ({query_point.x:.2f}, {query_point.y:.2f})")
    print(f"Quadtree find_nearest() result: ({quadtree_result.x:.2f}, {quadtree_result.y:.2f})")
    print(f"Brute-force nearest result:     ({brute_force_result.x:.2f}, {brute_force_result.y:.2f}) (distance: {brute_force_distance:.4f})")

    assert quadtree_result is brute_force_result, (   # 'is' not '==' since Point has auto-generated __eq__
        "MISMATCH: Quadtree result does not match brute-force result."
    )

    print("\nSUCCESS: Quadtree find_nearest() matches brute-force search.")


if __name__ == "__main__":
    main()