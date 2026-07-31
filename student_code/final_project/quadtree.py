import math


class Boundary:
    """
    Rectangular region defined by a center point and half-dimensions
    """
    def __init__(self, x, y, half_width, half_height):
        self.x = x
        self.y = y
        self.half_width = half_width
        self.half_height = half_height

    def contains(self, point):
        px, py = point
        return (self.x - self.half_width <= px < self.x + self.half_width and
                self.y - self.half_height <= py < self.y + self.half_height)

    def distance_to_point(self, point):
        """
        Shortest distance from the query point to the closest edge of this
        boundary. Returns 0 if the point is inside the boundary. 
        """
        px, py = point

        closest_x = max(self.x - self.half_width, min(px, self.x + self.half_width))
        closest_y = max(self.y - self.half_height, min(py, self.y + self.half_height))

        dx = px - closest_x
        dy = py - closest_y
        return math.sqrt(dx * dx + dy * dy)


class QuadtreeNode:
    """
    A single node in the Quadtree, representing one rectangular region
    of the map. Holds points directly until it reaches capacity, at
    which point it subdivides into four children.
    """

    # Hard ceiling on how many times a node can subdivide. 
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
        x = self.boundary.x
        y = self.boundary.y
        hw = self.boundary.half_width / 2
        hh = self.boundary.half_height / 2

        nw_boundary = Boundary(x - hw, y - hh, hw, hh)
        ne_boundary = Boundary(x + hw, y - hh, hw, hh)
        sw_boundary = Boundary(x - hw, y + hh, hw, hh)
        se_boundary = Boundary(x + hw, y + hh, hw, hh)

        child_depth = self.depth + 1
        self.northwest = QuadtreeNode(nw_boundary, self.capacity, child_depth)
        self.northeast = QuadtreeNode(ne_boundary, self.capacity, child_depth)
        self.southwest = QuadtreeNode(sw_boundary, self.capacity, child_depth)
        self.southeast = QuadtreeNode(se_boundary, self.capacity, child_depth)

        self.divided = True

    def insert(self, point):
        if not self.boundary.contains(point):
            return False

        # Past max depth, stop subdividing entirely and just bucket the point here, even if that means exceeding capacity. 
        if self.depth >= self.MAX_DEPTH:
            self.points.append(point)
            return True

        if len(self.points) < self.capacity and not self.divided:
            self.points.append(point)
            return True

        if not self.divided:
            self.subdivide()
            # Push this node's existing points down into the new children.
            existing_points = self.points
            self.points = []
            for existing_point in existing_points:
                self._insert_into_children(existing_point)

        return self._insert_into_children(point)

    def _insert_into_children(self, point):
        if self.northwest.insert(point):
            return True
        if self.northeast.insert(point):
            return True
        if self.southwest.insert(point):
            return True
        if self.southeast.insert(point):
            return True
        return False


class Quadtree:
    """
    This is the class that callers should interact with directly.
    """
    def __init__(self, x, y, half_width, half_height, capacity=4):
        self.boundary = Boundary(x, y, half_width, half_height)
        self.root = QuadtreeNode(self.boundary, capacity)

    def insert(self, point):
        return self.root.insert(point)

    def find_nearest(self, query_point):
        best = {"point": None, "distance": float("inf")}
        self._find_nearest_recursive(self.root, query_point, best)
        return best["point"]

    def _find_nearest_recursive(self, node, query_point, best):
        if node is None:
            return

        # Pruning check: if even the closest possible point in this node's boundary is farther away than our current best, there's no way anything inside this node (or its children) can improve on it.
        if node.boundary.distance_to_point(query_point) >= best["distance"]:
            return

        # Check points stored directly on this node (leaf case).
        for point in node.points:
            d = self._distance(point, query_point)
            if d < best["distance"]:
                best["distance"] = d
                best["point"] = point

        if not node.divided:
            return

        # Visit the child whose boundary contains the query point first
        children = [node.northwest, node.northeast, node.southwest, node.southeast]
        children.sort(key=lambda child: child.boundary.distance_to_point(query_point))

        for child in children:
            self._find_nearest_recursive(child, query_point, best)

    @staticmethod
    def _distance(p1, p2):
        dx = p1[0] - p2[0]
        dy = p1[1] - p2[1]
        return math.sqrt(dx * dx + dy * dy)