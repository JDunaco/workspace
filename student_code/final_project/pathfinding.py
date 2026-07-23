import heapq

def find_shortest_path(graph, start_node, end_node):
    distances = {node: float('inf') for node in graph}
    distances[start_node] = 0
    predecessors = {node: None for node in graph}

    heap = [(0, start_node)]
    visited = set()

    while heap:
        current_distance, current_node = heapq.heappop(heap)

        if current_node in visited:
            continue
        visited.add(current_node)

        if current_node == end_node:
            break

        # CHANGED: iterate over list of (neighbor, weight) tuples
        for neighbor, weight in graph.get(current_node, []):
            if neighbor in visited:
                continue
            new_distance = current_distance + weight
            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                predecessors[neighbor] = current_node
                heapq.heappush(heap, (new_distance, neighbor))

    if distances[end_node] == float('inf'):
        return (None, float('inf'))

    path = []
    node = end_node
    while node is not None:
        path.append(node)
        node = predecessors[node]
    path.reverse()

    return (path, distances[end_node])