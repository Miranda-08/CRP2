from owlready2 import get_ontology, Thing, ObjectProperty, DataProperty, FunctionalProperty

def build_ontology(path: str = "room_mgmt.owl"):
    onto = get_ontology("http://example.org/room_mgmt.owl")

    with onto:
        # --- Classes base ---
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

        # Para já usamos strings ISO simples. Depois podemos evoluir.
        class start(DataProperty, FunctionalProperty):
            domain = [RoomBooking]
            range = [str]

        class end(DataProperty, FunctionalProperty):
            domain = [RoomBooking]
            range = [str]

        class priority(DataProperty, FunctionalProperty):
            domain = [RoomBooking]
            range = [int]
        
        # --- Inferred / derived classes (we will assert membership via Python) ---
        # AvailableRoom: sala que não está em OverBookedRoom (vamos marcar isso via agente depois)
        class ConflictingBooking(RoomBooking): pass
        class MissingEquipmentBooking(RoomBooking): pass
        class UnderCapacityBooking(RoomBooking): pass

        class OverBookedRoom(Room): pass
        class AvailableRoom(Room): pass

        #AvailableRoom.equivalent_to = [Room & ~OverBookedRoom]

    onto.save(file=path, format="rdfxml")
    return onto
