from dataclasses import dataclass
from typing import Optional, Tuple, List, Dict

from ontology.reasoning import refresh_inferences, parse_iso, overlaps


@dataclass
class BookingRequest:
    activity_name: str
    start: str
    end: str
    priority: int = 5


@dataclass
class BookingResult:
    ok: bool
    booking_id: Optional[str] = None
    room_name: Optional[str] = None
    message: str = ""
    details: List[str] = None
    repairs: List[str] = None


class BookingAgent:
    HIGH_PRIORITY_THRESHOLD = 8

    def __init__(self, onto, verbose: bool = True):
        self.onto = onto
        self.verbose = verbose
        self.repair_time_grid = [
            "2026-01-05T08:00|2026-01-05T10:00",
            "2026-01-05T13:00|2026-01-05T15:00",
            "2026-01-05T15:00|2026-01-05T17:00",
            "2026-01-06T10:00|2026-01-06T12:00",
        ]

    def _log(self, s: str):
        if self.verbose:
            print(s)

    def _get_activity(self, name: str):
        try:
            obj = self.onto[name]
        except Exception:
            return None

        if not obj or not hasattr(obj, "is_a"):
            return None

        for cls in obj.is_a:
            try:
                if cls == self.onto.Activity or self.onto.Activity in cls.ancestors():
                    return obj
            except Exception:
                continue
        return None

    def _room_has_required_equipment(self, room, activity) -> bool:
        room_eq = set(getattr(room, "hasEquipment", []))
        req_eq = set(getattr(activity, "requiresEquipment", []))
        return req_eq.issubset(room_eq)

    def _room_has_capacity(self, room, activity) -> bool:
        cap = getattr(room, "capacity", None)
        exp = getattr(activity, "expectedAttendance", None)
        if cap is None or exp is None:
            return True
        return cap >= exp

    def _room_is_free(self, room, start_iso: str, end_iso: str, ignore_booking=None) -> bool:
        s = parse_iso(start_iso)
        e = parse_iso(end_iso)

        for b in self.onto.RoomBooking.instances():
            if ignore_booking is not None and b == ignore_booking:
                continue
            if not b.bookingRoom or b.bookingRoom != room:
                continue
            if not b.start or not b.end:
                continue
            bs = parse_iso(b.start)
            be = parse_iso(b.end)
            if overlaps(s, e, bs, be):
                return False
        return True

    def _score_room(self, room, activity) -> Tuple[int, int]:
        cap = getattr(room, "capacity", 10**9)
        exp = getattr(activity, "expectedAttendance", 0)
        leftover = cap - exp
        eq_count = len(getattr(room, "hasEquipment", []))
        return (leftover, -eq_count)

    def find_candidate_rooms(self, activity, start_iso: str, end_iso: str, ignore_booking=None):
        candidates = []
        for room in self.onto.Room.instances():
            if not self._room_has_capacity(room, activity):
                continue
            if not self._room_has_required_equipment(room, activity):
                continue
            if not self._room_is_free(room, start_iso, end_iso, ignore_booking=ignore_booking):
                continue
            candidates.append(room)
        return candidates

    def _create_booking_individual(self, activity, room, start_iso: str, end_iso: str, priority: int) -> str:
        booking_id = f"Booking_{len(self.onto.RoomBooking.instances()) + 1}"
        b = self.onto.RoomBooking(booking_id)
        b.bookingRoom = room
        b.bookingOf = activity
        b.start = start_iso
        b.end = end_iso
        b.priority = priority
        return booking_id

    def _blocking_bookings(self, start_iso: str, end_iso: str) -> List[object]:
        s = parse_iso(start_iso)
        e = parse_iso(end_iso)
        blockers = []
        for b in self.onto.RoomBooking.instances():
            if not b.start or not b.end:
                continue
            bs = parse_iso(b.start)
            be = parse_iso(b.end)
            if overlaps(s, e, bs, be):
                blockers.append(b)
        return blockers

    def _try_relocate_booking(self, booking) -> bool:
        if not booking.bookingOf or not booking.bookingRoom:
            return False

        act = booking.bookingOf

        # same time, different room
        for room in self.onto.Room.instances():
            if room == booking.bookingRoom:
                continue
            if not self._room_has_capacity(room, act):
                continue
            if not self._room_has_required_equipment(room, act):
                continue
            if self._room_is_free(room, booking.start, booking.end, ignore_booking=booking):
                old = (booking.bookingRoom.name, booking.start, booking.end)
                booking.bookingRoom = room
                self._log(f"[repair] moved {booking.name}: {old[0]} {old[1]}..{old[2]}  ->  {room.name} {booking.start}..{booking.end}")
                return True

        # other time + room
        for pair in self.repair_time_grid:
            new_start, new_end = pair.split("|", 1)
            for room in self.onto.Room.instances():
                if not self._room_has_capacity(room, act):
                    continue
                if not self._room_has_required_equipment(room, act):
                    continue
                if self._room_is_free(room, new_start, new_end, ignore_booking=booking):
                    old = (booking.bookingRoom.name, booking.start, booking.end)
                    booking.start = new_start
                    booking.end = new_end
                    booking.bookingRoom = room
                    self._log(f"[repair] moved {booking.name}: {old[0]} {old[1]}..{old[2]}  ->  {room.name} {new_start}..{new_end}")
                    return True

        return False

    def _try_priority_repair(self, activity, start_iso: str, end_iso: str, req_priority: int) -> bool:
        acceptable_rooms = []
        for room in self.onto.Room.instances():
            if not self._room_has_capacity(room, activity):
                continue
            if not self._room_has_required_equipment(room, activity):
                continue
            acceptable_rooms.append(room)

        if not acceptable_rooms:
            self._log("[repair] no rooms satisfy capacity/equipment even ignoring conflicts.")
            return False

        # Rank rooms by heuristic so we know which room we'd prefer to free
        acceptable_rooms.sort(key=lambda r: self._score_room(r, activity))
        preferred_room = acceptable_rooms[0]
        self._log(f"[repair] preferred target room to free: {preferred_room.name}")

        blockers = []
        for b in self._blocking_bookings(start_iso, end_iso):
            if not b.bookingRoom:
                continue
            if b.bookingRoom in acceptable_rooms:
                try:
                    prio = int(getattr(b, "priority", 0) or 0)
                except Exception:
                    prio = 0
                if prio < req_priority:
                    # record whether it blocks the preferred room
                    blocks_preferred = (b.bookingRoom == preferred_room)
                    blockers.append((0 if blocks_preferred else 1, prio, b))

        if not blockers:
            self._log("[repair] no lower-priority blockers found for acceptable rooms.")
            return False

        # Prefer blockers that block the best room; then lowest priority
        blockers.sort(key=lambda x: (x[0], x[1]))
        _, _, booking_to_move = blockers[0]

        self._log(
            f"[repair] trying to free '{booking_to_move.bookingRoom.name}' by moving "
            f"{booking_to_move.name} (prio {getattr(booking_to_move,'priority',0)})"
        )

        old_room = booking_to_move.bookingRoom
        old_start = booking_to_move.start
        old_end = booking_to_move.end

        moved = self._try_relocate_booking(booking_to_move)
        if not moved:
            self._log("[repair] failed to relocate blocker booking.")
            return False

        candidates = self.find_candidate_rooms(activity, start_iso, end_iso)
        if candidates:
            self._log("[repair] repair succeeded: found feasible room after moving blocker.")
            return True

        booking_to_move.bookingRoom = old_room
        booking_to_move.start = old_start
        booking_to_move.end = old_end
        self._log("[repair] relocation did not free a feasible room; reverted.")
        return False


    def explain_failure(self, req: BookingRequest) -> List[str]:
        """
        Returns a list of human-readable reasons why the booking cannot be placed.
        """
        details = []
        activity = self._get_activity(req.activity_name)
        if not activity:
            return [f"Activity '{req.activity_name}' not found in ontology."]

        req_eq = [e.name for e in getattr(activity, "requiresEquipment", [])]
        exp = getattr(activity, "expectedAttendance", None)
        details.append(f"Request: activity={activity.name}, attendance={exp}, requires={req_eq}, time={req.start}..{req.end}")

        for room in self.onto.Room.instances():
            reasons = []
            cap = getattr(room, "capacity", None)
            room_eq = [e.name for e in getattr(room, "hasEquipment", [])]

            # capacity
            if exp is not None and cap is not None and cap < exp:
                reasons.append(f"capacity {cap} < {exp}")

            # equipment
            if req_eq:
                if not set(getattr(activity, "requiresEquipment", [])).issubset(set(getattr(room, "hasEquipment", []))):
                    reasons.append(f"missing equipment (room has {room_eq})")

            # conflicts
            conflicts = []
            if room.bookingRoom if False else True:  # no-op, keeps lint calm
                pass
            for b in self.onto.RoomBooking.instances():
                if not b.bookingRoom or b.bookingRoom != room:
                    continue
                if not b.start or not b.end:
                    continue
                if overlaps(parse_iso(req.start), parse_iso(req.end), parse_iso(b.start), parse_iso(b.end)):
                    conflicts.append(f"{b.name}({b.start}..{b.end}, prio={getattr(b,'priority', '?')})")
            if conflicts:
                reasons.append("conflict with " + ", ".join(conflicts))

            if reasons:
                details.append(f"- {room.name}: " + "; ".join(reasons))
            else:
                details.append(f"- {room.name}: OK")

        return details

    def create_booking(self, req: BookingRequest) -> BookingResult:
        repairs_log: List[str] = []

        activity = self._get_activity(req.activity_name)
        if not activity:
            return BookingResult(ok=False, message="Activity not found.", details=[f"Activity '{req.activity_name}' not found."])

        candidates = self.find_candidate_rooms(activity, req.start, req.end)
        if not candidates and req.priority >= self.HIGH_PRIORITY_THRESHOLD:
            repaired = self._try_priority_repair(activity, req.start, req.end, req.priority)
            if repaired:
                candidates = self.find_candidate_rooms(activity, req.start, req.end)

        if not candidates:
            refresh_inferences(self.onto)
            details = self.explain_failure(req)
            return BookingResult(ok=False, message="No suitable room found.", details=details)

        candidates.sort(key=lambda r: self._score_room(r, activity))
        chosen = candidates[0]

        booking_id = self._create_booking_individual(activity, chosen, req.start, req.end, req.priority)
        refresh_inferences(self.onto)

        return BookingResult(ok=True, booking_id=booking_id, room_name=chosen.name, message="Created.")