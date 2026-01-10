from owlready2 import Thing, ObjectProperty, DataProperty, FunctionalProperty


def build_ontology(onto):
    with onto:
        # --- Base classes ---
        class Room(Thing): pass
        class RoomBooking(Thing): pass

        class Person(Thing): pass
        class Teacher(Person): pass
        class Student(Person): pass

        class Activity(Thing): pass
        class Lecture(Activity): pass
        class Exam(Activity): pass

        class Course(Thing): pass
        class Equipment(Thing): pass

        # --- Object properties ---
        class hasEquipment(ObjectProperty):
            domain = [Room]
            range = [Equipment]

        class requiresEquipment(ObjectProperty):
            domain = [Activity]
            range = [Equipment]

        class belongsToCourse(ObjectProperty):
            domain = [Activity]
            range = [Course]

        # NEW: connect people to activities/courses (minimal, but useful)
        class teaches(ObjectProperty):
            domain = [Teacher]
            range = [Activity]

        class enrolledIn(ObjectProperty):
            domain = [Student]
            range = [Course]

        class bookingRoom(ObjectProperty, FunctionalProperty):
            domain = [RoomBooking]
            range = [Room]

        class bookingOf(ObjectProperty, FunctionalProperty):
            domain = [RoomBooking]
            range = [Activity]

        # --- Data properties ---
        class capacity(DataProperty, FunctionalProperty):
            domain = [Room]
            range = [int]

        class expectedAttendance(DataProperty, FunctionalProperty):
            domain = [Activity]
            range = [int]

        # Using ISO strings for now
        class start(DataProperty, FunctionalProperty):
            domain = [RoomBooking]
            range = [str]

        class end(DataProperty, FunctionalProperty):
            domain = [RoomBooking]
            range = [str]

        class priority(DataProperty, FunctionalProperty):
            domain = [RoomBooking]
            range = [int]

        # --- Inferred / derived classes (asserted via Python) ---
        class ConflictingBooking(RoomBooking): pass
        class MissingEquipmentBooking(RoomBooking): pass
        class UnderCapacityBooking(RoomBooking): pass

        class OverBookedRoom(Room): pass
        class AvailableRoom(Room): pass

    return onto
