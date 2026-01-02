from dataclasses import dataclass
from typing import List, Optional, Tuple
from ontology.reasoning import parse_iso, overlaps

@dataclass
class Suggestion:
    booking: str
    issue: str
    recommendation: str

class AuditAgent:
    """
    Agent 2: audits inferred problems and proposes minimal-impact repairs.
    Strategy:
      - For time conflicts, prefer moving the lowest-priority booking.
      - Prefer same-time room change; otherwise propose rescheduling using a candidate grid.
      - For under-capacity/equipment issues, propose moving that booking.
    """

    def __init__(self, onto):
        self.onto = onto

        # Candidate time grid (can be expanded / generated later)
        self.candidate_times = [
            "2026-01-05T08:00|2026-01-05T10:00",
            "2026-01-05T13:00|2026-01-05T15:00",
            "2026-01-05T15:00|2026-01-05T17:00",
            "2026-01-06T10:00|2026-01-06T12:00",
        ]

    def _room_is_free(self, room, start_iso: str, end_iso: str, ignore_booking=None) -> bool:
        s = parse_iso(start_iso)
        e = parse_iso(end_iso)
        for b in self.onto.RoomBooking.instances():
            if ignore_booking and b == ignore_booking:
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

    def _room_meets(self, room, activity) -> bool:
        cap = getattr(room, "capacity", None)
        exp = getattr(activity, "expectedAttendance", None)
        if cap is not None and exp is not None and cap < exp:
            return False

        room_eq = set(getattr(room, "hasEquipment", []))
        req_eq = set(getattr(activity, "requiresEquipment", []))
        if req_eq and not req_eq.issubset(room_eq):
            return False

        return True

    def _suggest_room_same_time(self, booking) -> Optional[str]:
        if not booking.bookingOf or not booking.bookingRoom:
            return None
        act = booking.bookingOf
        for room in self.onto.Room.instances():
            if room == booking.bookingRoom:
                continue
            if not self._room_meets(room, act):
                continue
            if self._room_is_free(room, booking.start, booking.end, ignore_booking=booking):
                return room.name
        return None

    def _suggest_time_other_room(self, booking) -> Optional[str]:
        act = booking.bookingOf
        for time_pair in self.candidate_times:
            start_iso, end_iso = time_pair.split("|", 1)
            for room in self.onto.Room.instances():
                if not self._room_meets(room, act):
                    continue
                if self._room_is_free(room, start_iso, end_iso, ignore_booking=booking):
                    return f"{start_iso}..{end_iso} in {room.name}"
        return None

    def _find_conflict_pairs(self) -> List[Tuple[object, object]]:
        """
        Builds actual conflict pairs (b1,b2) for same-room overlaps,
        to avoid treating each ConflictingBooking in isolation.
        """
        bookings = list(self.onto.RoomBooking.instances())
        pairs = []
        for i in range(len(bookings)):
            b1 = bookings[i]
            if not b1.bookingRoom or not b1.start or not b1.end:
                continue
            r = b1.bookingRoom
            s1 = parse_iso(b1.start)
            e1 = parse_iso(b1.end)

            for j in range(i + 1, len(bookings)):
                b2 = bookings[j]
                if not b2.bookingRoom or not b2.start or not b2.end:
                    continue
                if b2.bookingRoom != r:
                    continue
                s2 = parse_iso(b2.start)
                e2 = parse_iso(b2.end)

                if overlaps(s1, e1, s2, e2):
                    pairs.append((b1, b2))
        return pairs

    def generate_suggestions(self) -> List[Suggestion]:
        suggestions: List[Suggestion] = []

        # --- Time conflicts: propose moving the lowest-priority booking only ---
        seen = set()
        for b1, b2 in self._find_conflict_pairs():
            key = tuple(sorted([b1.name, b2.name]))
            if key in seen:
                continue
            seen.add(key)

            p1 = int(getattr(b1, "priority", 0) or 0)
            p2 = int(getattr(b2, "priority", 0) or 0)

            # move the lower priority one
            move = b1 if p1 <= p2 else b2
            keep = b2 if move == b1 else b1

            alt_room = self._suggest_room_same_time(move)
            if alt_room:
                suggestions.append(Suggestion(
                    move.name,
                    "Time conflict",
                    f"Conflict with {keep.name}. Move {move.name} to room {alt_room} at the same time."
                ))
            else:
                alt = self._suggest_time_other_room(move)
                if alt:
                    suggestions.append(Suggestion(
                        move.name,
                        "Time conflict",
                        f"Conflict with {keep.name}. Reschedule {move.name}: {alt}."
                    ))
                else:
                    suggestions.append(Suggestion(
                        move.name,
                        "Time conflict",
                        f"Conflict with {keep.name}. No alternative found; expand time grid or add rooms."
                    ))

        # --- Under-capacity: fix that booking ---
        for b in self.onto.UnderCapacityBooking.instances():
            alt_room = self._suggest_room_same_time(b)
            if alt_room:
                suggestions.append(Suggestion(b.name, "Under capacity", f"Move to room {alt_room} at the same time."))
            else:
                alt = self._suggest_time_other_room(b)
                if alt:
                    suggestions.append(Suggestion(b.name, "Under capacity", f"Reschedule to a slot with a suitable room: {alt}."))
                else:
                    suggestions.append(Suggestion(b.name, "Under capacity", "No suitable room found; expand time grid or require new room."))

        # --- Missing equipment: fix that booking ---
        for b in self.onto.MissingEquipmentBooking.instances():
            alt_room = self._suggest_room_same_time(b)
            if alt_room:
                suggestions.append(Suggestion(b.name, "Missing equipment", f"Move to room {alt_room} at the same time."))
            else:
                alt = self._suggest_time_other_room(b)
                if alt:
                    suggestions.append(Suggestion(b.name, "Missing equipment", f"Reschedule: {alt}."))
                else:
                    suggestions.append(Suggestion(b.name, "Missing equipment", "No alternative found; expand time grid or add equipment."))

        return suggestions