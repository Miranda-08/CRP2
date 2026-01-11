from owlready2 import *

# TODO: If needed, update with the path to the Java interpreter
owlready2.JAVA_EXE = "java"

onto = get_ontology("http://crp.dei.uc.pt/university.owl")
with onto:
    # ========================================
    # ONTOLOGY CLASSES (Categories)
    # ========================================

    class Classroom(Thing):
        """Classroom for courses"""
        def update_status_based_on_bookings(self):
            """Update room status based on whether it has bookings."""
            if hasattr(self, 'has_booking') and self.has_booking:
                self.has_status = True  # Busy
            else:
                self.has_status = False  # Available
        
        def is_available(self) -> bool:
            """Check if room is available (no bookings)."""
            return not (hasattr(self, 'has_booking') and self.has_booking)
        
        def get_booking_count(self) -> int:
            """Get number of bookings for this room."""
            if hasattr(self, 'has_booking') and self.has_booking:
                return len(self.has_booking)
            return 0
        
        def add_booking(self, booking):
            """Add a booking to this room."""
            if not hasattr(self, 'has_booking'):
                self.has_booking = [booking]
            else:
                if not self.has_booking:
                    self.has_booking = [booking]
                else:
                    self.has_booking.append(booking)
            self.update_status_based_on_bookings()
            if hasattr(booking, 'is_booking_for'):
                booking.is_booking_for.append(self)
            else:
                booking.is_booking_for = [self]
    
        def remove_booking(self, booking):
            """Remove a booking from this room."""
            if hasattr(self, 'has_booking') and booking in self.has_booking:
                self.has_booking.remove(booking)
                if hasattr(booking, 'is_booking_for') and self in booking.is_booking_for:
                    booking.is_booking_for.remove(self)
                self.update_status_based_on_bookings()
        
    
    class RoomBooking(Thing): 
        """RoomBooking for courses"""

    class Person(Thing):
        """Base class for all people"""
        
    class Student(Person):
        """Students enrolled in university"""
        
    class Professor(Person):
        """Faculty members"""

    class Activity(Thing): 
        """Base Activity"""
        
    class Lecture(Activity):
        """Lecture for courses"""
        
    class Exam(Activity):
        """Exam for courses"""

    class Course(Thing):
        """Academic courses"""
        
    class Equipment(Thing):
        """Equipment for courses"""

    # ========================================
    # OBJECT PROPERTIES (Relations)
    # ========================================

    class EnrolledIn(Student >> Course):
        """Student is enrolled in a Course"""
        python_name = "enrolled_in"

    class Teaches(Professor >> Course):
        """Professor teaches a Course"""
        python_name = "teaches"

    class RequiresEquipment(Activity >> Equipment):
        """Course has Equipment as prerequisite"""
        python_name = "has_prerequisite"

    class HasEquipment(Classroom >> Equipment):
        """Classroom has prerequisite equipment"""
        python_name = "has_prerequisite_equipment"

    class TakesPlaceIn(Activity >> Classroom):
        """Activity takes place in a Classroom"""
        python_name = "takes_place_in"

    class BelongsToCourse(Activity >> Course):
        """Activity belongs to a Course"""
        python_name = "belongs_to_course"
    
    class HasBooking(Classroom >> RoomBooking):
        """Classroom has bookings"""
        python_name = "has_booking"

    class IsBookingFor(RoomBooking >> Classroom):
        """RoomBooking is for a Classroom"""
        python_name = "is_booking_for"
        inverse_property = HasBooking

    class BookingOf(Activity >> RoomBooking):
        """Activity to Book a Room"""
        python_name = "booking_of"

    class AdvisedBy(Student >> Professor):
        """Student is advised by Professor"""
        python_name = "advised_by"

    # ========================================
    # DATA PROPERTIES
    # ========================================

    class HasCapacity(DataProperty, FunctionalProperty):
        domain = [Classroom]
        range = [int]
        python_name = "has_capacity"
    
    class HasName(DataProperty, FunctionalProperty):
        """Person or Course have a name"""
        domain = [Person | Course | Activity | Classroom | Equipment]
        range = [str]
        python_name = "has_name"

    class HasAge(DataProperty, FunctionalProperty):
        """Person has an age"""
        domain = [Person]
        range = [int]
        python_name = "has_age"

    class HasExpectedAttendance(DataProperty, FunctionalProperty):
        domain = [Activity]
        range = [int]
        python_name = "has_expected_attendance"

    class HasStartTime(DataProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [str]
        python_name = "has_start_time"

    class HasEndTime(DataProperty, FunctionalProperty):
        domain = [RoomBooking]
        range = [str]
        python_name = "has_end_time"

    class HasPriority(DataProperty, FunctionalProperty):
        """Booking priority (higher number = higher priority)"""
        domain = [RoomBooking]
        range = [int]
        python_name = "has_priority"

    class HasGrade(DataProperty, FunctionalProperty):
        """Student has a grade (0-20 scale)"""
        domain = [Student]
        range = [float]
        python_name = "has_grade"

    class HasDegreeType(DataProperty, FunctionalProperty):
        """Student has a degree type (BSc, MSc, PhD)"""
        domain = [Student]
        range = [str]
        python_name = "has_degree_type"

    class HasYearsOfService(DataProperty, FunctionalProperty):
        """Professor has years of service"""
        domain = [Professor]
        range = [int]
        python_name = "has_years_of_service"

    class HasStatus(DataProperty, FunctionalProperty):
        """Classroom has status"""
        domain = [Classroom]
        range = [bool]
        python_name = "has_status"

    # ========================================
    # INFERRED CLASSES (First-Order Logic)
    # ========================================

    class AvailableRoom(Classroom):
        """Room with no bookings"""
        equivalent_to = [Classroom & Not(HasBooking.some(RoomBooking))]

    class OverBookedRoom(Classroom):
        """Room with more than one booking """
        equivalent_to = [Classroom & HasBooking.min(2, RoomBooking)]

    #=======================================
    # AGENTS
    #=======================================

    class CapacityOptimizationAgent(RoomBooking):
        """
        Agent that optimizes room capacity utilization by suggesting better room assignments.
        Identifies wasteful bookings and proposes efficient alternatives.
        """

        def analyze_room_efficiency(self):
                efficiencies = []
                
                for room in Classroom.instances():
                    if hasattr(room, 'has_booking') and room.has_booking:
                        for booking in room.has_booking:
                            # Find the activity for this booking
                            activity = self._find_activity_for_booking(booking)
                            if activity and hasattr(activity, 'has_expected_attendance'):
                                efficiency = self._calculate_efficiency(activity, room)
                                
                                efficiencies.append({
                                    'room': room,
                                    'booking': booking,
                                    'activity': activity,
                                    'efficiency': efficiency,
                                    'status': self._classify_efficiency(efficiency)
                                })
                
                return sorted(efficiencies, key=lambda x: x['efficiency'])
                   
        def _find_activity_for_booking(self, booking):
                for activity in list(Lecture.instances()) + list(Exam.instances()):
                    if hasattr(activity, 'booking_of') and booking in activity.booking_of:
                        return activity
                return None

        def _calculate_efficiency(self, activity, room):
            """Calculate room utilization efficiency (0-1 scale)."""
            if not hasattr(activity, 'has_expected_attendance'):
                return 0.0
            if not hasattr(room, 'has_capacity') or room.has_capacity == 0:
                return 0.0
            
            attendance = activity.has_expected_attendance
            capacity = room.has_capacity
            
            utilization = attendance / capacity
            
            if utilization < 0.6:
                return utilization / 0.6
            elif utilization > 1.4:
                if utilization > 2.0:
                    return 0.0
                return 1.0 - ((utilization - 1.4) / 0.6)
            else:
                # Optimal range: efficiency is 1.0
                return 1.0

        def _classify_efficiency(self, efficiency: float):
            """Classify the efficiency score."""
            if efficiency >= 0.9:
                return "OPTIMAL"
            elif efficiency >= 0.7:
                return "GOOD"
            elif efficiency >= 0.5:
                return "ACCEPTABLE"
            elif efficiency >= 0.3:
                return "POOR"
            else:
                return "VERY_POOR"

        
        def find_wasteful_bookings(self, threshold: float = 0.3):
            """Find bookings with efficiency below threshold."""
            efficiencies = self.analyze_room_efficiency()
            return [item for item in efficiencies if item['efficiency'] < threshold]

        def suggest_better_rooms(self, activity: Activity, exclude_rooms:[Classroom] = None):
            """Suggest better room options for an activity."""
            if not hasattr(activity, 'has_expected_attendance'):
                return []
            
            attendance = activity.has_expected_attendance
            current_room = activity.takes_place_in[0] if hasattr(activity, 'takes_place_in') and activity.takes_place_in else None
            
            suggestions = []
            exclude_rooms = exclude_rooms or []
            
            for room in Classroom.instances():
                if room in exclude_rooms or room == current_room:
                    continue
                
                # Check if room is available at the booking time
                if not self._is_room_available_for_activity(room, activity):
                    continue
                
                # Check if room has required equipment
                if not self._room_has_required_equipment(room, activity):
                    continue
                
                efficiency = self._calculate_efficiency(activity, room)
                capacity_diff = abs(attendance - room.has_capacity) if hasattr(room, 'has_capacity') else float('inf')
                
                suggestions.append({
                    'room': room,
                    'efficiency': efficiency,
                    'capacity': room.has_capacity if hasattr(room, 'has_capacity') else 0,
                    'capacity_difference': capacity_diff,
                    'utilization': attendance / room.has_capacity if hasattr(room, 'has_capacity') and room.has_capacity > 0 else 0
                })
            
            return sorted(suggestions, 
                        key=lambda x: (-x['efficiency'], x['capacity_difference']))
        
        
        def _is_room_available_for_activity(self, room: Classroom, activity: Activity) -> bool:
            """Check if room is available during the activity's booking time."""
            if not hasattr(activity, 'booking_of') or not activity.booking_of:
                return True
            
            activity_booking = activity.booking_of[0]
            activity_start = activity_booking.has_start_time if hasattr(activity_booking, 'has_start_time') else "00:00"
            activity_end = activity_booking.has_end_time if hasattr(activity_booking, 'has_end_time') else "23:59"
            
            if not hasattr(room, 'has_booking') or not room.has_booking:
                return True
            
            for booking in room.has_booking:
                if booking == activity_booking:
                    continue
                
                booking_start = booking.has_start_time if hasattr(booking, 'has_start_time') else "00:00"
                booking_end = booking.has_end_time if hasattr(booking, 'has_end_time') else "23:59"
                
                # Check for time overlap
                if self._times_overlap(activity_start, activity_end, booking_start, booking_end):
                    return False
            
            return True
        
        def _times_overlap(self, start1: str, end1: str, start2: str, end2: str) -> bool:
            """Check if two time intervals overlap."""
            def to_minutes(time_str):
                if not time_str:
                    return 0
                parts = time_str.split(':')
                return int(parts[0]) * 60 + int(parts[1])
            
            s1, e1 = to_minutes(start1), to_minutes(end1)
            s2, e2 = to_minutes(start2), to_minutes(end2)
            
            return not (e1 <= s2 or e2 <= s1)
        
        def _room_has_required_equipment(self, room: Classroom, activity: Activity):
            """Check if room has all equipment required by the activity."""
            if not hasattr(activity, 'has_prerequisite') or not activity.has_prerequisite:
                return True
            
            if not hasattr(room, 'has_prerequisite_equipment') or not room.has_prerequisite_equipment:
                return False
            
            required_equipment = set(activity.has_prerequisite)
            room_equipment = set(room.has_prerequisite_equipment)
            
            return required_equipment.issubset(room_equipment)

        
        def generate_optimization_report(self):
            """Generate a comprehensive optimization report."""
            efficiencies = self.analyze_room_efficiency()
            wasteful = self.find_wasteful_bookings(threshold=0.7)
            
            report = {
                'total_bookings': len(efficiencies),
                'average_efficiency': sum(item['efficiency'] for item in efficiencies) / len(efficiencies) if efficiencies else 0,
                'wasteful_bookings_count': len(wasteful),
                'wasteful_bookings': [],
                'optimization_suggestions': []
            }
            
            # Analyze wasteful bookings
            for item in wasteful:
                activity = item['activity']
                suggestions = self.suggest_better_rooms(activity)
                
                wasteful_info = {
                    'activity': activity.has_name if hasattr(activity, 'has_name') else activity.name,
                    'current_room': item['room'].has_name,
                    'current_efficiency': item['efficiency'],
                    'attendance': activity.has_expected_attendance,
                    'current_capacity': item['room'].has_capacity,
                    'better_options': []
                }
                
                # Add top 3 suggestions
                for suggestion in suggestions[:3]:
                    wasteful_info['better_options'].append({
                        'room': suggestion['room'].has_name,
                        'efficiency': suggestion['efficiency'],
                        'capacity': suggestion['capacity'],
                        'utilization': f"{suggestion['utilization']*100:.1f}%"
                    })
                
                report['wasteful_bookings'].append(wasteful_info)
                
                # If there are good alternatives, add to optimization suggestions
                if suggestions and suggestions[0]['efficiency'] > item['efficiency']:
                    report['optimization_suggestions'].append({
                        'activity': activity.has_name if hasattr(activity, 'has_name') else activity.name,
                        'move_from': item['room'].has_name,
                        'move_to': suggestions[0]['room'].has_name,
                        'efficiency_gain': suggestions[0]['efficiency'] - item['efficiency'],
                        'new_utilization': f"{suggestions[0]['utilization']*100:.1f}%"
                    })
            
            return report
        
        def apply_optimizations(self, min_efficiency_gain: float = 0.2):
            """Apply the best optimization suggestions automatically."""
            report = self.generate_optimization_report()
            applied_changes = []
            
            for suggestion in report['optimization_suggestions']:
                if suggestion['efficiency_gain'] >= min_efficiency_gain:
                    # Find the activity and rooms
                    activity_name = suggestion['activity']
                    old_room_name = suggestion['move_from']
                    new_room_name = suggestion['move_to']
                    
                    # Find the actual instances
                    activity = None
                    for act in list(Lecture.instances()) + list(Exam.instances()):
                        if hasattr(act, 'has_name') and act.has_name == activity_name:
                            activity = act
                            break
                    
                    old_room = None
                    new_room = None
                    for room in Classroom.instances():
                        if room.has_name == old_room_name:
                            old_room = room
                        elif room.has_name == new_room_name:
                            new_room = room
                    
                    if activity and old_room and new_room:
                        # Move the booking
                        if hasattr(activity, 'booking_of') and activity.booking_of:
                            booking = activity.booking_of[0]
                            
                            # Remove from old room
                            old_room.remove_booking(booking)
                            
                            # Add to new room
                            new_room.add_booking(booking)
                            
                            # Update activity location
                            activity.takes_place_in = [new_room]
                            
                            applied_changes.append({
                                'activity': activity_name,
                                'from_room': old_room_name,
                                'to_room': new_room_name,
                                'efficiency_gain': suggestion['efficiency_gain']
                            })
            
            return applied_changes

    class OverBookedRoomAgent(RoomBooking):
            """
            Agent that detects and resolves room booking conflicts.
            Identifies overlapping bookings and suggests alternative solutions.
            """

            def find_booking_conflicts(self):
                """Find all rooms with overlapping bookings."""
                conflicts = []
                
                for room in Classroom.instances():
                    if not hasattr(room, 'has_booking') or not room.has_booking:
                        continue
                    
                    bookings = list(room.has_booking)
                    
                    # Check all pairs of bookings for time conflicts
                    for i, booking1 in enumerate(bookings):
                        for booking2 in bookings[i+1:]:
                            if self._bookings_overlap(booking1, booking2):
                                conflicts.append({
                                    'room': room,
                                    'booking1': booking1,
                                    'booking2': booking2,
                                    'activity1': self._find_activity_for_booking(booking1),
                                    'activity2': self._find_activity_for_booking(booking2)
                                })
                
                return conflicts
            
            def _bookings_overlap(self, booking1: RoomBooking, booking2: RoomBooking) -> bool:
                """Check if two bookings have overlapping times."""
                start1 = booking1.has_start_time if hasattr(booking1, 'has_start_time') else "00:00"
                end1 = booking1.has_end_time if hasattr(booking1, 'has_end_time') else "23:59"
                start2 = booking2.has_start_time if hasattr(booking2, 'has_start_time') else "00:00"
                end2 = booking2.has_end_time if hasattr(booking2, 'has_end_time') else "23:59"
                
                return self._times_overlap(start1, end1, start2, end2)
            
            def _times_overlap(self, start1: str, end1: str, start2: str, end2: str) -> bool:
                """Check if two time intervals overlap."""
                def to_minutes(time_str):
                    if not time_str:
                        return 0
                    parts = time_str.split(':')
                    return int(parts[0]) * 60 + int(parts[1])
                
                s1, e1 = to_minutes(start1), to_minutes(end1)
                s2, e2 = to_minutes(start2), to_minutes(end2)
                
                return not (e1 <= s2 or e2 <= s1)
            
            def _find_activity_for_booking(self, booking):
                """Find the activity associated with a booking."""
                for activity in list(Lecture.instances()) + list(Exam.instances()):
                    if hasattr(activity, 'booking_of') and booking in activity.booking_of:
                        return activity
                return None
            
            def _is_room_available_at_time(self, room: Classroom, start_time: str, 
                                        end_time: str, exclude_booking=None) -> bool:
                """Check if room is available during specified time."""
                if not hasattr(room, 'has_booking') or not room.has_booking:
                    return True
                
                for booking in room.has_booking:
                    if booking == exclude_booking:
                        continue
                    
                    booking_start = booking.has_start_time if hasattr(booking, 'has_start_time') else "00:00"
                    booking_end = booking.has_end_time if hasattr(booking, 'has_end_time') else "23:59"
                    
                    if self._times_overlap(start_time, end_time, booking_start, booking_end):
                        return False
                
                return True
            
            def _room_meets_requirements(self, room: Classroom, activity: Activity) -> bool:
                """Check if room meets capacity and equipment requirements."""
                # Check capacity
                if hasattr(activity, 'has_expected_attendance') and hasattr(room, 'has_capacity'):
                    if room.has_capacity < activity.has_expected_attendance:
                        return False
                
                # Check equipment
                if hasattr(activity, 'has_prerequisite') and activity.has_prerequisite:
                    if not hasattr(room, 'has_prerequisite_equipment') or not room.has_prerequisite_equipment:
                        return False
                    
                    required = set(activity.has_prerequisite)
                    available = set(room.has_prerequisite_equipment)
                    
                    if not required.issubset(available):
                        return False
                
                return True
            
            def find_alternative_rooms(self, activity: Activity, booking: RoomBooking, 
                                    current_room: Classroom):
                """Find alternative rooms for a conflicting booking."""
                alternatives = []
                
                start_time = booking.has_start_time if hasattr(booking, 'has_start_time') else "00:00"
                end_time = booking.has_end_time if hasattr(booking, 'has_end_time') else "23:59"
                
                for room in Classroom.instances():
                    if room == current_room:
                        continue
                    
                    # Check if available at the required time
                    if not self._is_room_available_at_time(room, start_time, end_time):
                        continue
                    
                    # Check if room meets requirements
                    if not self._room_meets_requirements(room, activity):
                        continue
                    
                    # Calculate suitability score
                    capacity_match = 0
                    if hasattr(activity, 'has_expected_attendance') and hasattr(room, 'has_capacity'):
                        utilization = activity.has_expected_attendance / room.has_capacity
                        if 0.6 <= utilization <= 1.0:
                            capacity_match = 1.0
                        elif utilization < 0.6:
                            capacity_match = utilization / 0.6
                        else:
                            capacity_match = max(0, 1.0 - (utilization - 1.0) / 0.4)
                    
                    alternatives.append({
                        'room': room,
                        'capacity': room.has_capacity if hasattr(room, 'has_capacity') else 0,
                        'suitability': capacity_match,
                        'current_bookings': room.get_booking_count()
                    })
                
                return sorted(alternatives, key=lambda x: (-x['suitability'], x['current_bookings']))
            
            def generate_conflict_report(self):
                """Generate a comprehensive report of all booking conflicts."""
                conflicts = self.find_booking_conflicts()
                
                report = {
                    'total_conflicts': len(conflicts),
                    'conflicts': [],
                    'resolution_suggestions': []
                }
                
                for conflict in conflicts:
                    room = conflict['room']
                    booking1 = conflict['booking1']
                    booking2 = conflict['booking2']
                    activity1 = conflict['activity1']
                    activity2 = conflict['activity2']
                    
                    conflict_info = {
                        'room': room.has_name,
                        'booking1': {
                            'name': booking1.name,
                            'time': f"{booking1.has_start_time} - {booking1.has_end_time}",
                            'priority': booking1.has_priority if hasattr(booking1, 'has_priority') else 0,
                            'activity': activity1.has_name if activity1 and hasattr(activity1, 'has_name') else 'Unknown'
                        },
                        'booking2': {
                            'name': booking2.name,
                            'time': f"{booking2.has_start_time} - {booking2.has_end_time}",
                            'priority': booking2.has_priority if hasattr(booking2, 'has_priority') else 0,
                            'activity': activity2.has_name if activity2 and hasattr(activity2, 'has_name') else 'Unknown'
                        }
                    }
                    
                    report['conflicts'].append(conflict_info)
                    
                    # Determine which booking to move (lower priority or later time)
                    priority1 = booking1.has_priority if hasattr(booking1, 'has_priority') else 0
                    priority2 = booking2.has_priority if hasattr(booking2, 'has_priority') else 0
                    
                    if priority1 < priority2:
                        booking_to_move = booking1
                        activity_to_move = activity1
                    elif priority2 < priority1:
                        booking_to_move = booking2
                        activity_to_move = activity2
                    else:
                        # Same priority, move the one with more alternatives
                        booking_to_move = booking1
                        activity_to_move = activity1
                    
                    # Find alternatives for the booking to move
                    if activity_to_move:
                        alternatives = self.find_alternative_rooms(activity_to_move, booking_to_move, room)
                        
                        if alternatives:
                            suggestion = {
                                'conflict_room': room.has_name,
                                'activity_to_move': activity_to_move.has_name if hasattr(activity_to_move, 'has_name') else 'Unknown',
                                'booking_to_move': booking_to_move.name,
                                'reason': 'Lower priority' if priority1 < priority2 or priority2 < priority1 else 'Equal priority',
                                'alternative_rooms': []
                            }
                            
                            for alt in alternatives[:3]:  # Top 3 alternatives
                                suggestion['alternative_rooms'].append({
                                    'room': alt['room'].has_name,
                                    'capacity': alt['capacity'],
                                    'suitability': f"{alt['suitability']*100:.1f}%",
                                    'current_bookings': alt['current_bookings']
                                })
                            
                            report['resolution_suggestions'].append(suggestion)
                
                return report
            
            def resolve_conflict(self, conflict: dict, use_alternative: int = 0):
                """
                Resolve a specific conflict by moving one booking to an alternative room.
                
                Args:
                    conflict: The conflict dictionary from find_booking_conflicts()
                    use_alternative: Index of the alternative room to use (default: 0 for best option)
                """
                room = conflict['room']
                booking1 = conflict['booking1']
                booking2 = conflict['booking2']
                activity1 = conflict['activity1']
                activity2 = conflict['activity2']
                
                # Determine which to move based on priority
                priority1 = booking1.has_priority if hasattr(booking1, 'has_priority') else 0
                priority2 = booking2.has_priority if hasattr(booking2, 'has_priority') else 0
                
                if priority1 < priority2:
                    booking_to_move = booking1
                    activity_to_move = activity1
                else:
                    booking_to_move = booking2
                    activity_to_move = activity2
                
                if not activity_to_move:
                    return False
                
                # Find alternative rooms
                alternatives = self.find_alternative_rooms(activity_to_move, booking_to_move, room)
                
                if not alternatives or use_alternative >= len(alternatives):
                    return False
                
                new_room = alternatives[use_alternative]['room']
                
                # Move the booking
                room.remove_booking(booking_to_move)
                new_room.add_booking(booking_to_move)
                
                # Update activity location
                activity_to_move.takes_place_in = [new_room]
                
                return True
            
            def auto_resolve_all_conflicts(self):
                """Automatically resolve all booking conflicts."""
                conflicts = self.find_booking_conflicts()
                resolved = []
                failed = []
                
                for conflict in conflicts:
                    activity_name = None
                    old_room = conflict['room'].has_name
                    
                    if self.resolve_conflict(conflict):
                        # Find which activity was moved
                        priority1 = conflict['booking1'].has_priority if hasattr(conflict['booking1'], 'has_priority') else 0
                        priority2 = conflict['booking2'].has_priority if hasattr(conflict['booking2'], 'has_priority') else 0
                        
                        if priority1 < priority2 and conflict['activity1']:
                            activity_name = conflict['activity1'].has_name if hasattr(conflict['activity1'], 'has_name') else 'Unknown'
                            new_room = conflict['activity1'].takes_place_in[0].has_name if conflict['activity1'].takes_place_in else 'Unknown'
                        elif conflict['activity2']:
                            activity_name = conflict['activity2'].has_name if hasattr(conflict['activity2'], 'has_name') else 'Unknown'
                            new_room = conflict['activity2'].takes_place_in[0].has_name if conflict['activity2'].takes_place_in else 'Unknown'
                        
                        resolved.append({
                            'activity': activity_name,
                            'from_room': old_room,
                            'to_room': new_room
                        })
                    else:
                        failed.append({
                            'room': old_room,
                            'reason': 'No suitable alternative found'
                        })
                
                return {
                    'resolved': resolved,
                    'failed': failed
                }
        
if __name__ == "__main__":
    with onto:
        # Professors
        prof_smith = Professor("Prof_Smith")
        prof_smith.has_name = "Dr. John Smith"
        prof_smith.has_age = 45
        prof_smith.has_years_of_service = 4

        prof_jones = Professor("Prof_Jones")
        prof_jones.has_name = "Dr. Sarah Jones"
        prof_jones.has_age = 38
        prof_jones.has_years_of_service = 10

        prof_brown = Professor("Prof_Brown")
        prof_brown.has_name = "Dr. Michael Brown"
        prof_brown.has_age = 58
        prof_brown.has_years_of_service = 15

        # Equipment
        projector = Equipment("Projector")
        projector.has_name = "Projector"

        computador = Equipment("Computador")
        computador.has_name = "Computador"
        
        whiteboard = Equipment("Whiteboard")
        whiteboard.has_name = "Whiteboard"

        microphone = Equipment("Microphone")
        microphone.has_name = "Microphone"

        A1 = Classroom("A1")
        A1.has_name = "A1"
        A1.has_capacity = 30
        A1.has_prerequisite_equipment = [projector]
        A1.has_status = False 

        r202 = Classroom("R202")
        r202.has_name = "R202"
        r202.has_capacity = 60
        r202.has_prerequisite_equipment = [projector, computador]
        r202.has_status = False

        r303 = Classroom("R303")
        r303.has_name = "R303"
        r303.has_capacity = 20
        r303.has_prerequisite_equipment = []
        r303.has_status = False

        r404 = Classroom("R404")
        r404.has_name = "R404"
        r404.has_capacity = 120
        r404.has_prerequisite_equipment = [projector, microphone]
        r404.has_status = False
        

        r505 = Classroom("R505")
        r505.has_name = "R505"
        r505.has_capacity = 15
        r505.has_prerequisite_equipment = [whiteboard]
        r505.has_status = False

        r606 = Classroom("R606")
        r606.has_name = "R606"
        r606.has_capacity = 80
        r606.has_prerequisite_equipment = [projector, computador, whiteboard]
        r606.has_status = False

        r707 = Classroom("R707")
        r707.has_name = "R707"
        r707.has_capacity = 80
        r707.has_prerequisite_equipment = [projector, computador, whiteboard]
        r707.has_status = False

        c34 = Classroom("c34")
        c34.has_name = "c34"
        c34.has_capacity = 25
        c34.has_prerequisite_equipment = [projector, computador, whiteboard]
        c34.has_status = False

        e34 = Classroom("e34")
        e34.has_name = "e34"
        e34.has_capacity = 60
        e34.has_prerequisite_equipment = [projector, computador, whiteboard]
        e34.has_status = False
        
        # Courses
        crp = Course("CRP")
        crp.has_name = "Conhecimento Razão e Planeamento"

        alg = Course("ALG")
        alg.has_name = "Algorithms"

        ai = Course("AI")
        ai.has_name = "Artificial Intelligence"

        db = Course("DB")
        db.has_name = "Databases"



        booking_r202_1 = RoomBooking("Booking_R202_1")
        booking_r202_1.has_start_time = "09:00"
        booking_r202_1.has_end_time = "10:30"
        booking_r202_1.has_priority = 2

        booking_r202_2 = RoomBooking("Booking_R202_2")
        booking_r202_2.has_start_time = "11:00"
        booking_r202_2.has_end_time = "12:30"
        booking_r202_2.has_priority = 1

        r202.add_booking(booking_r202_1)
        r202.add_booking(booking_r202_2)

        booking_r303_1 = RoomBooking("Booking_R303_1")
        booking_r303_1.has_start_time = "10:00"
        booking_r303_1.has_end_time = "11:30"
        booking_r303_1.has_priority = 1
        r303.add_booking(booking_r303_1)

        booking_r404_1 = RoomBooking("Booking_R404_1")
        booking_r404_1.has_start_time = "08:00"
        booking_r404_1.has_end_time = "09:30"
        booking_r404_1.has_priority = 1

        booking_r404_2 = RoomBooking("Booking_R404_2_test")
        booking_r404_2.has_start_time = "13:00"
        booking_r404_2.has_end_time = "14:30"
        booking_r404_2.has_priority = 1

        r404.add_booking(booking_r404_1)
        r404.add_booking(booking_r404_2)

        booking_r505_1 = RoomBooking("Booking_R505_1")
        booking_r505_1.has_start_time = "09:30"
        booking_r505_1.has_end_time = "11:00"
        booking_r505_1.has_priority = 1

        booking_r505_2 = RoomBooking("Booking_R505_2_test")
        booking_r505_2.has_start_time = "13:00"
        booking_r505_2.has_end_time = "14:30"
        booking_r505_2.has_priority = 1
        r505.add_booking(booking_r505_1)
        r505.add_booking(booking_r505_2)

        booking_r707_1 = RoomBooking("Booking_R707_1")
        booking_r707_1.has_start_time = "08:00"
        booking_r707_1.has_end_time = "09:30"
        booking_r707_1.has_priority = 2

        booking_r707_2 = RoomBooking("Booking_R707_2")
        booking_r707_2.has_start_time = "10:00"
        booking_r707_2.has_end_time = "11:30"
        booking_r707_2.has_priority = 1

        booking_r707_3 = RoomBooking("Booking_R707_3")
        booking_r707_3.has_start_time = "14:00"
        booking_r707_3.has_end_time = "15:30"
        booking_r707_3.has_priority = 3
        
        r707.add_booking(booking_r707_1)
        r707.add_booking(booking_r707_2)
        r707.add_booking(booking_r707_3)


        #Testes de overlaping
        booking_a1_1 = RoomBooking("Booking_A1_1")
        booking_a1_1.has_start_time = "08:30"
        booking_a1_1.has_end_time = "10:00"
        booking_a1_1.has_priority = 1
        
        booking_a1_2 = RoomBooking("Booking_A1_2")
        booking_a1_2.has_start_time = "09:00"
        booking_a1_2.has_end_time = "10:30"
        booking_a1_2.has_priority = 1  # Same priority
        
        A1.add_booking(booking_a1_1)
        A1.add_booking(booking_a1_2)

        booking_r606_1 = RoomBooking("Booking_R606_1")
        booking_r606_1.has_start_time = "14:00"
        booking_r606_1.has_end_time = "15:30"
        booking_r606_1.has_priority = 2  #

        r606.add_booking(booking_r606_1)

        # Connect activities to bookings
        ml_lecture = Lecture("ML_Lecture")
        ml_lecture.has_name = "Machine Learning"
        ml_lecture.has_expected_attendance = 70
        ml_lecture.belongs_to_course = [ai]
        ml_lecture.takes_place_in = [r606]
        ml_lecture.booking_of = [booking_r606_1]
        ml_lecture.has_prerequisite = [projector, computador]

        stats_lecture = Lecture("Stats_Lecture")
        stats_lecture.has_name = "Statistics Overview"
        stats_lecture.has_expected_attendance = 65
        stats_lecture.belongs_to_course = [Course.instances()[0]]
        stats_lecture.takes_place_in = [A1]
        stats_lecture.booking_of = [booking_a1_2]
        stats_lecture.has_prerequisite = [Equipment("Projector")]
        

        test_lecture_small = Lecture("Test_Lecture_Small")
        test_lecture_small.has_name = "Test Small Class"
        test_lecture_small.has_expected_attendance = 10
        test_lecture_small.belongs_to_course = [crp]
        test_lecture_small.takes_place_in = [r404]
        test_lecture_small.booking_of = [booking_r404_2]
        test_lecture_small.has_prerequisite = [projector]

        test_lecture_overcrowded = Lecture("Test_Lecture_Overcrowded")
        test_lecture_overcrowded.has_name = "Test Overcrowded Class"
        test_lecture_overcrowded.has_expected_attendance = 25
        test_lecture_overcrowded.belongs_to_course = [ai]
        test_lecture_overcrowded.takes_place_in = [r505]
        test_lecture_overcrowded.booking_of = [booking_r505_2]
        test_lecture_overcrowded.has_prerequisite = [whiteboard]

        lecture_crp = Lecture("Lecture_CRP")
        lecture_crp.has_name = "CRP Introduction"
        lecture_crp.has_expected_attendance = 28
        lecture_crp.belongs_to_course = [crp]
        lecture_crp.takes_place_in = [A1]
        lecture_crp.booking_of = [booking_a1_1]

        lecture_alg1 = Lecture("Lecture_ALG_1")
        lecture_alg1.has_name = "Algorithms Basics"
        lecture_alg1.has_expected_attendance = 55
        lecture_alg1.belongs_to_course = [alg]
        lecture_alg1.takes_place_in = [r202]
        lecture_alg1.booking_of = [booking_r202_1]

        exam_ai = Exam("Exam_AI")
        exam_ai.has_name = "AI Final Exam"
        exam_ai.has_expected_attendance = 58
        exam_ai.belongs_to_course = [ai]
        exam_ai.takes_place_in = [r202]
        exam_ai.booking_of = [booking_r202_2]

        lecture_db = Lecture("Lecture_DB")
        lecture_db.has_name = "Database Design"
        lecture_db.has_expected_attendance = 18
        lecture_db.belongs_to_course = [db]
        lecture_db.takes_place_in = [r303]
        lecture_db.booking_of = [booking_r303_1]

        exam_crp = Exam("Exam_CRP")
        exam_crp.has_name = "CRP Midterm"
        exam_crp.has_expected_attendance = 110
        exam_crp.belongs_to_course = [crp]
        exam_crp.takes_place_in = [r404]
        exam_crp.booking_of = [booking_r404_1]

        lecture_ai = Lecture("Lecture_AI")
        lecture_ai.has_name = "AI Introduction"
        lecture_ai.has_expected_attendance = 14
        lecture_ai.belongs_to_course = [ai]
        lecture_ai.takes_place_in = [r505]
        lecture_ai.booking_of = [booking_r505_1]
        lecture_ai.has_prerequisite = [whiteboard]

        lecture_adv_alg = Lecture("Lecture_Advanced_ALG")
        lecture_adv_alg.has_name = "Advanced Algorithms"
        lecture_adv_alg.has_expected_attendance = 75
        lecture_adv_alg.belongs_to_course = [alg]
        lecture_adv_alg.takes_place_in = [r707]
        lecture_adv_alg.booking_of = [booking_r707_1]

        seminar_db = Lecture("Seminar_DB")
        seminar_db.has_name = "Database Seminar"
        seminar_db.has_expected_attendance = 70
        seminar_db.belongs_to_course = [db]
        seminar_db.takes_place_in = [r707]
        seminar_db.booking_of = [booking_r707_2]

        exam_final = Exam("Final_Exam")
        exam_final.has_name = "Final Examination"
        exam_final.has_expected_attendance = 78
        exam_final.belongs_to_course = [crp]
        exam_final.takes_place_in = [r707]
        exam_final.booking_of = [booking_r707_3]

        # Add some equipment requirements
        lecture_crp.has_prerequisite = [projector]
        exam_ai.has_prerequisite = [computador]
        lecture_db.has_prerequisite = [whiteboard]

        # Teaching relationships
        prof_smith.teaches = [crp, alg, ai]
        prof_jones.teaches = [alg, db]

        # Students
        alice = Student("Alice")
        alice.has_name = "Alice Johnson"
        alice.has_age = 20
        alice.has_grade = 15.5
        alice.enrolled_in = [crp, alg]
        alice.advised_by = [prof_smith]

        bob = Student("Bob")
        bob.has_name = "Bob Williams"
        bob.has_age = 19
        bob.has_grade = 11.0
        bob.enrolled_in = [alg]
        bob.advised_by = [prof_jones]

        carol = Student("Carol")
        carol.has_name = "Carol Davis"
        carol.has_age = 22
        carol.has_grade = 18.5
        carol.enrolled_in = [crp, alg]
        carol.advised_by = [prof_smith]

        emma = Student("Emma")
        emma.has_name = "Emma Wilson"
        emma.has_age = 26
        emma.has_grade = 19.0
        emma.has_degree_type = "PhD"
        emma.enrolled_in = [crp]
        emma.advised_by = [prof_brown]

        david = Student("David")
        david.has_name = "David Miller"
        david.has_age = 24
        david.has_grade = 17.0
        david.has_degree_type = "MSc"
        david.enrolled_in = [alg]
        david.advised_by = [prof_jones]
        
        # Run reasoner to infer class memberships
        sync_reasoner(infer_property_values=True)

                # Save the ontology to a file
        onto.save(file="university.owl", format="rdfxml")
        print("\nOntology saved to university.owl")