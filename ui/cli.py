from agents.booking_agent import BookingAgent, BookingRequest
from ontology.queries import (
    list_rooms,
    list_bookings,
    list_available_rooms,
    list_problems,
    print_available_between,
)


def run_cli(onto):
    agent = BookingAgent(onto, verbose=True)

    help_text = """
Commands:
  rooms
  bookings
  booking <Booking_X>        - show details of one booking
  available
  problems

  book <activity> <start> <end> <priority>
    example:
    book Lecture_CRP_1 2026-01-05T14:00 2026-01-05T16:00 1

  available_between <start> <end> [min_capacity] [equipment_csv]
    example:
    available_between 2026-01-05T09:00 2026-01-05T11:00 40 Projector
    available_between 2026-01-05T09:00 2026-01-05T11:00 20 Projector,Computers

  suggest
  help
  exit
"""
    print(help_text)

    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue

        cmd_lower = cmd.lower()

        if cmd_lower in ("exit", "quit"):
            break
        if cmd_lower == "help":
            print(help_text)
            continue
        if cmd_lower == "rooms":
            list_rooms(onto)
            continue
        if cmd_lower == "bookings":
            list_bookings(onto)
            continue
        if cmd_lower.startswith("booking "):
            parts = cmd.split()
            if len(parts) != 2:
                print("Usage: booking <Booking_X>")
                continue
            bid = parts[1]
            if bid in onto:
                b = onto[bid]
                room = b.bookingRoom.name if getattr(b, "bookingRoom", None) else "?"
                act = b.bookingOf.name if getattr(b, "bookingOf", None) else "?"
                print(f"{b.name}")
                print(f"  room: {room}")
                print(f"  activity: {act}")
                print(f"  time: {getattr(b,'start','?')}..{getattr(b,'end','?')}")
                print(f"  priority: {getattr(b,'priority','?')}")
            else:
                print(f"Booking '{bid}' not found.")
            continue
        if cmd_lower == "available":
            list_available_rooms(onto)
            continue
        if cmd_lower == "problems":
            list_problems(onto)
            continue

        if cmd_lower.startswith("available_between "):
            parts = cmd.split(maxsplit=4)
            if len(parts) < 3:
                print("Usage: available_between <start> <end> [min_capacity] [equipment_csv]")
                continue

            _, start, end, *rest = parts
            min_capacity = None
            equipment = None

            if len(rest) >= 1:
                try:
                    min_capacity = int(rest[0])
                    if len(rest) >= 2:
                        equipment = rest[1]
                except ValueError:
                    equipment = rest[0]

            req_eq = None
            if equipment:
                req_eq = [x.strip() for x in equipment.split(",") if x.strip()]

            print_available_between(onto, start, end, min_capacity=min_capacity, required_equipment=req_eq)
            continue

        if cmd_lower.startswith("book "):
            parts = cmd.split()
            if len(parts) != 5:
                print("Usage: book <activity> <start> <end> <priority>")
                continue

            _, activity, start, end, priority = parts
            try:
                priority = int(priority)
            except ValueError:
                print("priority must be an integer (e.g. 1 lecture, 10 exam)")
                continue

            result = agent.create_booking(BookingRequest(activity_name=activity, start=start, end=end, priority=priority))
            if result.ok:
                print(f"Created: {result.booking_id} (room={result.room_name})")
            else:
                print(result.message)
                if result.details:
                    for line in result.details:
                        print("  " + line)
            continue

        if cmd_lower == "suggest":
            # keep your existing suggest handler; leaving it as-is
            from agents.second_agent import AuditAgent
            a2 = AuditAgent(onto)
            sugg = a2.generate_suggestions()
            if not sugg:
                print("No suggestions (no detected problems).")
            else:
                for s in sugg:
                    print(f"- {s.booking} | {s.issue}: {s.recommendation}")
            continue

        print("Unknown command. Type 'help'.")