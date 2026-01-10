from datetime import datetime


def parse_iso(dt: str) -> datetime:
    return datetime.fromisoformat(dt)


def overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end


def list_rooms(onto):
    for r in onto.Room.instances():
        eq = [e.name for e in getattr(r, "hasEquipment", [])]
        cap = getattr(r, "capacity", None)
        print(f"- {r.name} | capacity={cap} | equipment={eq}")

def list_bookings(onto):
    def key(b):
        s = getattr(b, "start", "") or ""
        return (s, b.name)

    bookings = sorted(list(onto.RoomBooking.instances()), key=key)

    for b in bookings:
        room = b.bookingRoom.name if getattr(b, "bookingRoom", None) else "?"
        act = b.bookingOf.name if getattr(b, "bookingOf", None) else "?"
        pr = getattr(b, "priority", "?")
        s = getattr(b, "start", "?")
        e = getattr(b, "end", "?")
        print(f"- {b.name}: {s}..{e} | room={room} | activity={act} | priority={pr}")


def list_available_rooms(onto):
    rooms = onto.AvailableRoom.instances()
    print("AvailableRoom inferred:", [r.name for r in rooms])


def list_problems(onto):
    print("ConflictingBooking:", [b.name for b in onto.ConflictingBooking.instances()])
    print("UnderCapacityBooking:", [b.name for b in onto.UnderCapacityBooking.instances()])
    print("MissingEquipmentBooking:", [b.name for b in onto.MissingEquipmentBooking.instances()])
    print("OverBookedRoom:", [r.name for r in onto.OverBookedRoom.instances()])


# ---------------------------
# NEW: Complex query
# ---------------------------

def available_between(
    onto,
    start_iso: str,
    end_iso: str,
    min_capacity: int | None = None,
    required_equipment: list[str] | None = None,
):
    """
    Returns rooms that are free between [start_iso, end_iso), optionally filtering by:
      - min_capacity
      - required equipment names (e.g. ["Projector", "Computers"])
    """
    start_dt = parse_iso(start_iso)
    end_dt = parse_iso(end_iso)

    # Pre-resolve equipment objects by name (if requested)
    req_eq_objs = []
    if required_equipment:
        by_name = {e.name: e for e in onto.Equipment.instances()}
        for name in required_equipment:
            if name in by_name:
                req_eq_objs.append(by_name[name])

    free_rooms = []
    for r in onto.Room.instances():
        # capacity filter
        cap = getattr(r, "capacity", None)
        if min_capacity is not None and cap is not None and cap < min_capacity:
            continue

        # equipment filter
        if req_eq_objs:
            room_eq = set(getattr(r, "hasEquipment", []))
            if not set(req_eq_objs).issubset(room_eq):
                continue

        # temporal availability filter
        is_free = True
        for b in onto.RoomBooking.instances():
            if not b.bookingRoom or not b.start or not b.end:
                continue
            if b.bookingRoom != r:
                continue

            bs = parse_iso(b.start)
            be = parse_iso(b.end)
            if overlaps(start_dt, end_dt, bs, be):
                is_free = False
                break

        if is_free:
            free_rooms.append(r)

    return free_rooms


def print_available_between(
    onto,
    start_iso: str,
    end_iso: str,
    min_capacity: int | None = None,
    required_equipment: list[str] | None = None,
):
    rooms = available_between(onto, start_iso, end_iso, min_capacity, required_equipment)
    print("Available rooms:", [r.name for r in rooms])
