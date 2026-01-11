import os
import sys
from typing import List
from datetime import datetime

from owlready2 import *
from version2 import *



if __name__ == "__main__":

    # Load existing ontology from file
    onto = get_ontology("university.owl").load()

    # Query: Find all honors students (grade >= 18.0)
    print("\n=== Students ===")
    for student in onto.search(type=Student):
        print(f"{student.has_name} - Grade: {student.has_grade}")



    print("\n===  Professors ===")
    for prof in onto.search(type=Professor):
        print(f"{prof.has_name}: {prof.teaches}")

    print("\n=== ClassRooms ===")
    for room in onto.search(type=Classroom):
        # Update status based on current bookings
        room.update_status_based_on_bookings()
        
        print(f"""\n--{room.has_name}--
capacity: {room.has_capacity}
prereq: {room.has_prerequisite_equipment}
bookings: {room.get_booking_count()}""")
        
        if room.has_status == False:
            print("status = available")
        else:
            print("status = busy")
    


    # Query: Calculate statistics across the university
    def university_statistics():
        print("\n=== University Statistics ===")
        total_students = len(list(onto.search(type=Student)))
        total_profs = len(list(onto.search(type=Professor)))
        total_courses = len(list(onto.search(type=Course)))
        total_classrooms = len(list(onto.search(type=Classroom)))

        # Calculate average grade
        grades = [s.has_grade for s in onto.search(type=Student)]
        avg_grade = sum(grades) / len(grades) if grades else 0

        # Count enrollments
        total_enrollments = sum(len(s.enrolled_in) for s in onto.search(type=Student))

        print(f"Total Students: {total_students}")
        print(f"Total Professors: {total_profs}")
        print(f"Total Courses: {total_courses}")
        print(f"Total Classrooms: {total_classrooms}")

        print(f"Average Grade: {avg_grade:.2f}")
        print(f"Total Enrollments: {total_enrollments}")

    def manage_overbookings():
        """Detect and manage room booking conflicts."""
        print("\n=== Room Booking Conflict Management ===")
        
        # Create agent instance
        conflict_agent = OverBookedRoomAgent("ConflictManager")
        conflict_agent.has_name = "Booking Conflict Manager"
        
        # Generate conflict report
        report = conflict_agent.generate_conflict_report()
        
        print(f"\nTotal conflicts detected: {report['total_conflicts']}")
        
        if report['conflicts']:
            print("\n--- Booking Conflicts ---")
            for i, conflict in enumerate(report['conflicts'], 1):
                print(f"\n{i}. Room: {conflict['room']}")
                print(f"   Conflict between:")
                print(f"   • {conflict['booking1']['activity']} ({conflict['booking1']['time']}) "
                    f"- Priority: {conflict['booking1']['priority']}")
                print(f"   • {conflict['booking2']['activity']} ({conflict['booking2']['time']}) "
                    f"- Priority: {conflict['booking2']['priority']}")
        
        if report['resolution_suggestions']:
            print("\n--- Resolution Suggestions ---")
            for i, suggestion in enumerate(report['resolution_suggestions'], 1):
                print(f"\n{i}. Move '{suggestion['activity_to_move']}' from {suggestion['conflict_room']}")
                print(f"   Reason: {suggestion['reason']}")
                print("   Alternative rooms:")
                
                for alt in suggestion['alternative_rooms']:
                    print(f"     • {alt['room']}: Capacity {alt['capacity']}, "
                        f"Suitability {alt['suitability']}, "
                        f"{alt['current_bookings']} existing bookings")
        if report['total_conflicts'] > 0:
            resolve = input("\nAuto-resolve all conflicts? (yes/no): ").strip().lower()
            if resolve == 'yes':
                results = conflict_agent.auto_resolve_all_conflicts()
            
                if results['resolved']:
                    print("\n✓ Successfully resolved conflicts:")
                    for res in results['resolved']:
                        print(f"  - Moved '{res['activity']}' from {res['from_room']} "
                          f"to {res['to_room']}")
            
                if results['failed']:
                    print("\n✗ Failed to resolve:")
                    for fail in results['failed']:
                        print(f"  - Room {fail['room']}: {fail['reason']}")
            
            # Run reasoner again to update inferred classes
            sync_reasoner(infer_property_values=True)
            
            # Save the updated ontology
            onto.save(file="university.owl", format="rdfxml")
            print("\nOntology updated and saved.")

    def optimization():
        print("\n=== Capacity Optimization Analysis ===")
        
        # Create agent instance
        optimization_agent = CapacityOptimizationAgent("CapacityOptimizer")
        optimization_agent.has_name = "Room Capacity Optimizer"
        
        # Generate optimization report
        report = optimization_agent.generate_optimization_report()
        
        print(f"\nTotal bookings analyzed: {report['total_bookings']}")
        print(f"Average room efficiency: {report['average_efficiency']:.2%}")
        print(f"Wasteful bookings found: {report['wasteful_bookings_count']}")
        
        if report['wasteful_bookings']:
            print("\n--- Wasteful Bookings ---")
            for i, wasteful in enumerate(report['wasteful_bookings'], 1):
                print(f"\n{i}. {wasteful['activity']}")
                print(f"   Current: {wasteful['current_room']} "
                      f"({wasteful['attendance']}/{wasteful['current_capacity']} = "
                      f"{wasteful['attendance']/wasteful['current_capacity']*100:.1f}%)")
                print(f"   Efficiency: {wasteful['current_efficiency']:.2%}")
                
                if wasteful['better_options']:
                    print("   Better options:")
                    for option in wasteful['better_options']:
                        print(f"     - {option['room']}: {option['efficiency']:.2%} efficiency "
                              f"({option['utilization']} utilization)")
        
        if report['optimization_suggestions']:
            print("\n--- Optimization Suggestions ---")
            for i, suggestion in enumerate(report['optimization_suggestions'], 1):
                print(f"{i}. Move '{suggestion['activity']}' from {suggestion['move_from']} "
                      f"to {suggestion['move_to']}")
                print(f"   Efficiency gain: +{suggestion['efficiency_gain']:.2%}")
                print(f"   New utilization: {suggestion['new_utilization']}")
        
        # Ask user if they want to apply optimizations
        apply = input("\nApply optimizations? (yes/no): ").strip().lower()
        if apply == 'yes':
            changes = optimization_agent.apply_optimizations(min_efficiency_gain=0.1)
            if changes:
                print("\nApplied optimizations:")
                for change in changes:
                    print(f"- Moved '{change['activity']}' from {change['from_room']} "
                          f"to {change['to_room']} (+{change['efficiency_gain']:.2%})")
            else:
                print("No optimizations were applied.")
        
        # Run reasoner again to update inferred classes
        sync_reasoner(infer_property_values=True)
        
        # Save the updated ontology
        onto.save(file="university.owl", format="rdfxml")


    def print_all_bookings():
            print("\n" + "="*80)
            print("BOOKINGS")
            print("="*80)
            
            # Collect all bookings by room
            room_bookings = {}
            
            for room in onto.search(type=Classroom):
                if hasattr(room, 'has_booking') and room.has_booking:
                    room_bookings[room] = sorted(
                        room.has_booking, 
                        key=lambda b: (b.has_start_time if hasattr(b, 'has_start_time') else "00:00")
                    )
            
            # Sort rooms by name
            sorted_rooms = sorted(room_bookings.items(), key=lambda x: x[0].has_name)
            
            for room, bookings in sorted_rooms:
                print(f"\n┌─ {room.has_name} ".ljust(79, "─") + "┐")
                print(f"│ Capacity: {room.has_capacity}".ljust(79) + "│")
                
                if hasattr(room, 'has_prerequisite_equipment') and room.has_prerequisite_equipment:
                    equipment_names = [eq.has_name for eq in room.has_prerequisite_equipment]
                    print(f"│ Equipment: {', '.join(equipment_names)}".ljust(79) + "│")
                
                print(f"│ Total Bookings: {len(bookings)}".ljust(79) + "│")
                print("├" + "─"*78 + "┤")
                
                for i, booking in enumerate(bookings, 1):
                    # Get booking details
                    start_time = booking.has_start_time if hasattr(booking, 'has_start_time') else "N/A"
                    end_time = booking.has_end_time if hasattr(booking, 'has_end_time') else "N/A"
                    priority = booking.has_priority if hasattr(booking, 'has_priority') else 0
                    
                    # Find associated activity
                    activity = None
                    for act in list(onto.search(type=Lecture)) + list(onto.search(type=Exam)):
                        if hasattr(act, 'booking_of') and booking in act.booking_of:
                            activity = act
                            break
                    
                    activity_name = "No Activity"
                    activity_type = ""
                    attendance = "N/A"
                    course_name = "N/A"
                    
                    if activity:
                        activity_name = activity.has_name if hasattr(activity, 'has_name') else activity.name
                        activity_type = " Exam" if isinstance(activity, onto.Exam) else " Lecture"
                        attendance = activity.has_expected_attendance if hasattr(activity, 'has_expected_attendance') else "N/A"
                        
                        if hasattr(activity, 'belongs_to_course') and activity.belongs_to_course:
                            course = activity.belongs_to_course[0]
                            course_name = course.has_name if hasattr(course, 'has_name') else course.name
                    
                    # Print booking info
                    print(f"│ #{i} ".ljust(79) + "│")
                    print(f"│    Time: {start_time} - {end_time}".ljust(79) + "│")
                    print(f"│   {activity_type} {activity_name}".ljust(79) + "│")
                    print(f"│    Course: {course_name}".ljust(79) + "│")
                    print(f"│    Expected Attendance: {attendance}".ljust(79) + "│")
                    print(f"│    Priority: {priority}".ljust(79) + "│")
                    
                    if i < len(bookings):
                        print("│" + "─"*78 + "│")
                
                print("└" + "─"*78 + "┘")
            
            # Summary statistics
            total_bookings = sum(len(bookings) for bookings in room_bookings.values())
            total_rooms = len(room_bookings)
            rooms_with_multiple = sum(1 for bookings in room_bookings.values() if len(bookings) > 1)
            
            print("\n" + "="*80)
            print(" SUMMARY")
            print("="*80)
            print(f"Total Rooms with Bookings: {total_rooms}")
            print(f"Total Bookings: {total_bookings}")
            print(f"Rooms with Multiple Bookings: {rooms_with_multiple}")
            print(f"Average Bookings per Room: {total_bookings/total_rooms:.1f}" if total_rooms > 0 else "Average Bookings per Room: 0")
            print("="*80)

    university_statistics()
    manage_overbookings()
    optimization()
    print_all_bookings()