def list_rooms(onto):
    for r in onto.Room.instances():
        eq = [e.name for e in getattr(r, "hasEquipment", [])]
        cap = getattr(r, "capacity", None)
        print(f"- {r.name} | capacity={cap} | equipment={eq}")

def list_bookings(onto):
    for b in onto.RoomBooking.instances():
        room = b.bookingRoom.name if b.bookingRoom else "?"
        act = b.bookingOf.name if b.bookingOf else "?"
        print(f"- {b.name}: room={room}, activity={act}, {b.start}..{b.end}, priority={b.priority}")


def list_available_rooms(onto):
    rooms = onto.AvailableRoom.instances()
    print("AvailableRoom inferred:", [r.name for r in rooms])

def list_problems(onto):
    print("ConflictingBooking:", [b.name for b in onto.ConflictingBooking.instances()])
    print("UnderCapacityBooking:", [b.name for b in onto.UnderCapacityBooking.instances()])
    print("MissingEquipmentBooking:", [b.name for b in onto.MissingEquipmentBooking.instances()])
    print("OverBookedRoom:", [r.name for r in onto.OverBookedRoom.instances()])
