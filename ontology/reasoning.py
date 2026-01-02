from datetime import datetime

def parse_iso(dt: str) -> datetime:
    # "2026-01-05T10:00"
    return datetime.fromisoformat(dt)

def overlaps(a_start, a_end, b_start, b_end) -> bool:
    return a_start < b_end and b_start < a_end

def refresh_inferences(onto):
    """
    Recomputes inferred classes by scanning bookings and asserting class membership.
    This avoids requiring a Java reasoner early on.
    """

    # Convenience
    ConflictingBooking = onto.ConflictingBooking
    MissingEquipmentBooking = onto.MissingEquipmentBooking
    UnderCapacityBooking = onto.UnderCapacityBooking
    OverBookedRoom = onto.OverBookedRoom
    AvailableRoom = onto.AvailableRoom

    # 1) Clear old inferred types (only our inferred classes)
    for b in onto.RoomBooking.instances():
        b.is_a = [c for c in b.is_a if c not in (ConflictingBooking, MissingEquipmentBooking, UnderCapacityBooking)]

    for r in onto.Room.instances():
        r.is_a = [c for c in r.is_a if c not in (OverBookedRoom, AvailableRoom)]

    # 2) Equipment + capacity checks per booking
    for b in onto.RoomBooking.instances():
        if not b.bookingRoom or not b.bookingOf:
            continue

        room = b.bookingRoom
        act = b.bookingOf

        # capacity
        cap = getattr(room, "capacity", None)
        exp = getattr(act, "expectedAttendance", None)
        if cap is not None and exp is not None and cap < exp:
            b.is_a.append(UnderCapacityBooking)

        # equipment
        room_eq = set(getattr(room, "hasEquipment", []))
        req_eq = set(getattr(act, "requiresEquipment", []))
        if req_eq and not req_eq.issubset(room_eq):
            b.is_a.append(MissingEquipmentBooking)

    # 3) Time conflicts (same room, overlapping intervals)
    bookings = list(onto.RoomBooking.instances())
    conflict_rooms = set()

    for i in range(len(bookings)):
        b1 = bookings[i]
        if not b1.bookingRoom or not b1.start or not b1.end:
            continue
        r1 = b1.bookingRoom
        s1 = parse_iso(b1.start)
        e1 = parse_iso(b1.end)

        for j in range(i + 1, len(bookings)):
            b2 = bookings[j]
            if not b2.bookingRoom or not b2.start or not b2.end:
                continue
            if b2.bookingRoom != r1:
                continue

            s2 = parse_iso(b2.start)
            e2 = parse_iso(b2.end)

            if overlaps(s1, e1, s2, e2):
                # mark both as conflicting
                if ConflictingBooking not in b1.is_a:
                    b1.is_a.append(ConflictingBooking)
                if ConflictingBooking not in b2.is_a:
                    b2.is_a.append(ConflictingBooking)

                conflict_rooms.add(r1)

    # 4) Rooms: OverBookedRoom vs AvailableRoom
    for r in onto.Room.instances():
        if r in conflict_rooms:
            r.is_a.append(OverBookedRoom)
        else:
            r.is_a.append(AvailableRoom)