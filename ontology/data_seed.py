def seed_demo_data(onto):
    Room = onto.Room
    Equipment = onto.Equipment
    Course = onto.Course
    Lecture = onto.Lecture
    Exam = onto.Exam
    RoomBooking = onto.RoomBooking

    # Equipamentos
    projector = Equipment("Projector")
    computers = Equipment("Computers")

    # Salas
    r101 = Room("R101")
    r101.capacity = 30
    r101.hasEquipment = [projector]

    r202 = Room("R202")
    r202.capacity = 60
    r202.hasEquipment = [projector, computers]

    r303 = Room("R303")
    r303.capacity = 20
    r303.hasEquipment = []

    # Cursos
    crp = Course("CRP")
    alg = Course("ALG")

    # Atividades
    lec_crp = Lecture("Lecture_CRP_1")
    lec_crp.belongsToCourse = [crp]
    lec_crp.expectedAttendance = 25
    lec_crp.requiresEquipment = [projector]

    exam_alg = Exam("Exam_ALG_1")
    exam_alg.belongsToCourse = [alg]
    exam_alg.expectedAttendance = 55
    exam_alg.requiresEquipment = [projector]

    # Reservas (uma delas “força” um possível problema de capacidade se escolheres sala errada mais tarde)
    b1 = RoomBooking("Booking_1")
    b1.bookingRoom = r101
    b1.bookingOf = lec_crp
    b1.start = "2026-01-05T10:00"
    b1.end = "2026-01-05T12:00"
    b1.priority = 1

    b2 = RoomBooking("Booking_2")
    b2.bookingRoom = r202
    b2.bookingOf = exam_alg
    b2.start = "2026-01-05T10:00"
    b2.end = "2026-01-05T13:00"
    b2.priority = 10

    b3 = RoomBooking("Booking_3")
    b3.bookingRoom = r101
    b3.bookingOf = exam_alg
    b3.start = "2026-01-05T11:00"
    b3.end = "2026-01-05T12:30"
    b3.priority = 10


    return onto