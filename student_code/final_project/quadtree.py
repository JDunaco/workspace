import math
import heapq
from itertools import count
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Point:
    """
    Immutable point stored in the Quadtree. Carries an optional payload
    (e.g. the Car object) so the tree can return more than just coordinates.
    """
    x: float
    y: float
    data: Any = None


class Boundary:
    def __init__(self, x, y, half_width, half_height):
        self.x = x
        self.y = y
        self.half_width = half_width
        self.half_height = half_height

    def contains(self, point):
        return (self.x - self.half_width <= point.x < self.x + self.half_width and
                self.y - self.half_height <= point.y < self.y + self.half_height)

    def distance_to_point(self, point):
        closest_x = max(self.x - self.half_width, min(point.x, self.x + self.half_width))
        closest_y = max(self.y - self.half_height, min(point.y, self.y + self.half_height))
        dx = point.x - closest_x
        dy = point.y - closest_y
        return math.sqrt(dx * dx + dy * dy)


class QuadtreeNode:
    MAX_DEPTH = 20

    def __init__(self, boundary, capacity=4, depth=0):
        self.boundary = boundary
        self.capacity = capacity
        self.depth = depth
        self.points = []
        self.divided = False
        self.northwest = None
        self.northeast = None
        self.southwest = None
        self.southeast = None

    def subdivide(self):
        x, y = self.boundary.x, self.boundary.y
        hw, hh = self.boundary.half_width / 2, self.boundary.half_height / 2
        child_depth = self.depth + 1
        self.northwest = QuadtreeNode(Boundary(x - hw, y - hh, hw, hh), self.capacity, child_depth)
        self.northeast = QuadtreeNode(Boundary(x + hw, y - hh, hw, hh), self.capacity, child_depth)
        self.southwest = QuadtreeNode(Boundary(x - hw, y + hh, hw, hh), self.capacity, child_depth)
        self.southeast = QuadtreeNode(Boundary(x + hw, y + hh, hw, hh), self.capacity, child_depth)
        self.divided = True

    def insert(self, point):
        if not self.boundary.contains(point):
            return False
        if self.depth >= self.MAX_DEPTH:
            self.points.append(point)
            return True
        if len(self.points) < self.capacity and not self.divided:
            self.points.append(point)
            return True
        if not self.divided:
            self.subdivide()
            existing = self.points
            self.points = []
            for p in existing:
                self._insert_into_children(p)
        return self._insert_into_children(point)

    def _insert_into_children(self, point):
        for child in (self.northwest, self.northeast, self.southwest, self.southeast):
            if child.insert(point):
                return True
        return False

    def remove(self, point):
        """
        Removes the exact Point object (by identity) from this subtree.
        Follows point.x/point.y down the correct branch(es).
        """
        if not self.boundary.contains(point):
            return False

        for i, stored in enumerate(self.points):
            if stored is point:
                del self.points[i]
                return True

        if not self.divided:
            return False

        for child in (self.northwest, self.northeast, self.southwest, self.southeast):
            if child.boundary.contains(point):
                if child.remove(point):
                    return True
        return False


class Quadtree:
    def __init__(self, x, y, half_width, half_height, capacity=4):
        self.boundary = Boundary(x, y, half_width, half_height)
        self.root = QuadtreeNode(self.boundary, capacity)

    def insert(self, point):
        return self.root.insert(point)

    def remove(self, point):
        return self.root.remove(point)

    def find_k_nearest(self, query_point, k=5):
        if k <= 0:
            raise ValueError("find_k_nearest: k must be positive.")

        heap = []          # entries: (-distance, seq, point) -- max-heap via negation
        seq_counter = count()

        def visit(node):
            if node is None:
                return

            if len(heap) >= k:
                farthest_dist = -heap[0][0]
                if node.boundary.distance_to_point(query_point) >= farthest_dist:
                    return

            for stored in node.points:
                d = self._distance(stored, query_point)
                if len(heap) < k:
                    heapq.heappush(heap, (-d, next(seq_counter), stored))
                elif d < -heap[0][0]:
                    heapq.heapreplace(heap, (-d, next(seq_counter), stored))

            if not node.divided:
                return

            children = [node.northwest, node.northeast, node.southwest, node.southeast]
            children.sort(key=lambda c: c.boundary.distance_to_point(query_point))
            for child in children:
                visit(child)

        visit(self.root)

        results = [(-neg_d, pt) for (neg_d, _, pt) in heap]
        results.sort(key=lambda item: item[0])
        return [pt for (_, pt) in results]

    def find_nearest(self, query_point):
        results = self.find_k_nearest(query_point, k=1)
        return results[0] if results else None

    @staticmethod
    def _distance(p1, p2):
        dx = p1.x - p2.x
        dy = p1.y - p2.y
        return math.sqrt(dx * dx + dy * dy)