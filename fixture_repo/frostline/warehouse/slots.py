"""Pallet slot allocation inside temperature zones."""

from frostline.warehouse.zones import zone_for

CAPACITY = {"FRZ": 40, "CHL": 60, "CRT": 80}


class SlotAllocator:
    def __init__(self, capacity=None):
        self.capacity = dict(capacity or CAPACITY)
        self.used = {code: 0 for code in self.capacity}

    def free(self, zone_code):
        return self.capacity[zone_code] - self.used[zone_code]

    def allocate(self, product, pallets):
        zone = zone_for(product)
        if self.free(zone.code) < pallets:
            return None
        self.used[zone.code] += pallets
        return zone.code

    def release(self, zone_code, pallets):
        self.used[zone_code] = max(0, self.used[zone_code] - pallets)
