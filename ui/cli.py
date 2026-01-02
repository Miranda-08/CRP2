from agents.booking_agent import BookingAgent, BookingRequest
from ontology.queries import list_rooms, list_bookings, list_available_rooms, list_problems
from agents.second_agent import AuditAgent

def run_cli(onto):
    agent = BookingAgent(onto)

    help_text = """
Commands:
  rooms                      - list rooms
  bookings                   - list bookings
  available                  - list available rooms (derived)
  problems                   - list inferred problems (conflicts/capacity/equipment)
  book <activity> <start> <end> <priority>
                            - create booking request (ISO times)
                              example:
                              book Lecture_CRP_1 2026-01-05T14:00 2026-01-05T16:00 1
  suggest                    - show repair suggestions from Agent 2
  help
  exit
"""
    print(help_text)

    while True:
        cmd = input("> ").strip()
        if not cmd:
            continue

        if cmd in ("exit", "quit"):
            break
        if cmd == "help":
            print(help_text)
            continue
        if cmd == "rooms":
            list_rooms(onto)
            continue
        if cmd == "bookings":
            list_bookings(onto)
            continue
        if cmd == "available":
            list_available_rooms(onto)
            continue
        if cmd == "problems":
            list_problems(onto)
            continue

        if cmd.startswith("book "):
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

            booking_id = agent.create_booking(
                BookingRequest(activity_name=activity, start=start, end=end, priority=priority)
            )

            if booking_id:
                print(f"Created: {booking_id}")
            else:
                print("No suitable room found (capacity/equipment/conflicts).")
            continue
        
        if cmd == "suggest":
            a2 = AuditAgent(onto)
            sugg = a2.generate_suggestions()
            if not sugg:
                print("No suggestions (no detected problems).")
            else:
                for s in sugg:
                    print(f"- {s.booking} | {s.issue}: {s.recommendation}")
            continue


        print("Unknown command. Type 'help'.")