"""Route engines registered under kind "routing"."""

import heapq

from frostline.core.errors import NotFound
from frostline.core.interfaces import RouteEngine
from frostline.core.registry import register


@register("routing", "dijkstra")
class DijkstraEngine(RouteEngine):
    """Shortest path by total distance."""

    def path(self, origin, destination):
        if not (self.network.has(origin) and self.network.has(destination)):
            raise NotFound("unknown depot")
        queue = [(0, origin, [origin])]
        seen = set()
        while queue:
            dist, node, path = heapq.heappop(queue)
            if node == destination:
                return path
            if node in seen:
                continue
            seen.add(node)
            for nxt, km in self.network.neighbours(node):
                if nxt not in seen:
                    heapq.heappush(queue, (dist + km, nxt, path + [nxt]))
        raise NotFound("no route")


@register("routing", "greedy")
class GreedyEngine(RouteEngine):
    """Always hop to the nearest unvisited neighbour; backtrack on dead ends.

    Faster than Dijkstra on large networks but not guaranteed to be shortest.
    """

    def path(self, origin, destination):
        if not (self.network.has(origin) and self.network.has(destination)):
            raise NotFound("unknown depot")
        path, visited = [origin], {origin}
        while path and path[-1] != destination:
            options = [(km, n) for n, km in self.network.neighbours(path[-1]) if n not in visited]
            if not options:
                path.pop()
                continue
            km, nxt = min(options)
            visited.add(nxt)
            path.append(nxt)
        if not path:
            raise NotFound("no route")
        return path
