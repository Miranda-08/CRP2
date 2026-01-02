from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple

from ontology.reasoning import refresh_inferences, parse_iso, overlaps


@dataclass
class BookingRequest:
    activity_name: str
    start: str           # ISO e.g. "2026-01-05T14:00"
    end: str             # ISO
    priority: int = 5    # exams > lectures (e.g. 10 vs 1)


class BookingAgent:
    """
    Agent 1 (required): processes booking requests and assigns a suitable room based on:
      - capacity
      - equipment requirements
      - time conflicts
      - simple preference heuristic
    """

    def __init__(self, onto):
        self.onto = onto

    def _get_activity(self, name: str):
        act = self.onto.search_one(iri="*" + name)
        if act and act.is_a and self.onto.Activity in act.is_a[0].ancestors():
            return act
        # fallback: try by label-like direct access
        return self.onto[name] if name in self.onto else None

    def _room_has_required_equipment(self, room, activity) -> bool:
        room_eq = set(getattr(room, "hasEquipment", []))
        req_eq = set(getattr(activity, "requiresEquipment", []))
        return req_eq.issubset(room_eq)

    def _room_has_capacity(self, room, activity) -> bool:
        cap = getattr(room, "capacity", None)
        exp = getattr(activity, "expectedAttendance", None)
        if cap is None or exp is None:
            return True  # be permissive if missing data
        return cap >= exp

    def _room_is_free(self, room, start_iso: str, end_iso: str) -> bool:
        s = parse_iso(start_iso)
        e = parse_iso(end_iso)

        for b in self.onto.RoomBooking.instances():
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
        """
        Heuristic:
          - Prefer tighter fit on capacity (minimize leftover)
          - Prefer rooms with more equipment (as a tiebreaker)
        Lower is better for leftover; we return (leftover, -equipment_count) for sorting.
        """
        cap = getattr(room, "capacity", 10**9)
        exp = getattr(activity, "expectedAttendance", 0)
        leftover = cap - exp
        eq_count = len(getattr(room, "hasEquipment", []))
        return (leftover, -eq_count)

    def find_candidate_rooms(self, activity, start_iso: str, end_iso: str):
        candidates = []
        for room in self.onto.Room.instances():
            if not self._room_has_capacity(room, activity):
                continue
            if not self._room_has_required_equipment(room, activity):
                continue
            if not self._room_is_free(room, start_iso, end_iso):
                continue
            candidates.append(room)
        return candidates

    def create_booking(self, req: BookingRequest) -> Optional[str]:
        activity = self._get_activity(req.activity_name)
        if not activity:
            return None

        candidates = self.find_candidate_rooms(activity, req.start, req.end)
        if not candidates:
            return None

        # choose best room by heuristic
        candidates.sort(key=lambda r: self._score_room(r, activity))
        chosen = candidates[0]

        # create booking individual
        booking_id = f"Booking_{len(self.onto.RoomBooking.instances()) + 1}"
        b = self.onto.RoomBooking(booking_id)
        b.bookingRoom = chosen
        b.bookingOf = activity
        b.start = req.start
        b.end = req.end
        b.priority = req.priority

        # refresh inferred tags
        refresh_inferences(self.onto)

        return booking_id