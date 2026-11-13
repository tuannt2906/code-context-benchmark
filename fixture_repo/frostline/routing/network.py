"""Depot network: undirected weighted graph of road distances in km."""

REMOTE_DEPOTS = {"HGI", "LCU"}

EDGES = [
    ("HAN", "HPH", 120),
    ("HAN", "NDH", 95),
    ("HAN", "TNG", 80),
    ("HPH", "NDH", 70),
    ("NDH", "THO", 85),
    ("TNG", "LCU", 210),
    ("THO", "VIN", 140),
    ("VIN", "HUE", 360),
    ("THO", "HUE", 520),
    ("HUE", "DNG", 95),
    ("DNG", "HCM", 960),
    ("HCM", "CTH", 170),
    ("CTH", "HGI", 115),
    ("DNG", "QNH", 300),
    ("QNH", "HCM", 650),
]


class Network:
    def __init__(self, edges):
        self._adj = {}
        for a, b, km in edges:
            self._adj.setdefault(a, {})[b] = km
            self._adj.setdefault(b, {})[a] = km

    def edge(self, a, b):
        return self._adj[a][b]

    def neighbours(self, node):
        return sorted(self._adj.get(node, {}).items())

    def nodes(self):
        return sorted(self._adj)

    def has(self, node):
        return node in self._adj


def default_network():
    return Network(EDGES)
