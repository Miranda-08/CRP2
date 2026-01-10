def seed_demo_data(onto):
    Room = onto.Room
    Equipment = onto.Equipment
    Course = onto.Course
    Lecture = onto.Lecture
    Exam = onto.Exam
    RoomBooking = onto.RoomBooking

    Teacher = onto.Teacher
    Student = onto.Student

    # ----------------------
    # Equipamentos
    # ----------------------
    projector = Equipment("Projector")
    computers = Equipment("Computers")
    whiteboard = Equipment("Whiteboard")

    # ----------------------
    # Salas (cria variedade para testes)
    # ----------------------
    r101 = Room("R101")
    r101.capacity = 30
    r101.hasEquipment = [projector, whiteboard]  # projector, no computers

    r202 = Room("R202")
    r202.capacity = 60
    r202.hasEquipment = [projector, computers]

    r303 = Room("R303")
    r303.capacity = 20
    r303.hasEquipment = []  # nenhuma

    # Sala extra útil: grande mas sem projector (para falha por equipamento)
    r404 = Room("R404")
    r404.capacity = 80
    r404.hasEquipment = [computers]  # sem projector

    # ----------------------
    # Cursos
    # ----------------------
    crp = Course("CRP")
    alg = Course("ALG")
    prog = Course("PROG")

    # ----------------------
    # Pessoas (mínimo, mas útil)
    # ----------------------
    t_ana = Teacher("Teacher_Ana")
    t_bruno = Teacher("Teacher_Bruno")

    s_joao = Student("Student_Joao")
    s_maria = Student("Student_Maria")
    s_rita = Student("Student_Rita")
    s_joao.enrolledIn = [crp]
    s_maria.enrolledIn = [alg]
    s_rita.enrolledIn = [prog]

    # ----------------------
    # Atividades (variedade para testes)
    # ----------------------

    # Lecture normal: precisa projector, 25 alunos
    lec_crp = Lecture("Lecture_CRP_1")
    lec_crp.belongsToCourse = [crp]
    lec_crp.expectedAttendance = 25
    lec_crp.requiresEquipment = [projector]

    # Exame grande: 55 alunos, precisa projector
    exam_alg = Exam("Exam_ALG_1")
    exam_alg.belongsToCourse = [alg]
    exam_alg.expectedAttendance = 55
    exam_alg.requiresEquipment = [projector]

    # Exame pequeno (para demonstrar prioridade/repair): 25 alunos, precisa projector
    exam_crp_small = Exam("Exam_CRP_SMALL")
    exam_crp_small.belongsToCourse = [crp]
    exam_crp_small.expectedAttendance = 25
    exam_crp_small.requiresEquipment = [projector]

    # Aula que exige computadores (para demonstrar MissingEquipment)
    lab_prog = Lecture("Lab_PROG_1")
    lab_prog.belongsToCourse = [prog]
    lab_prog.expectedAttendance = 30
    lab_prog.requiresEquipment = [computers]  # exige computadores

    # Exame impossível por capacidade (opcional para demo): 120 alunos
    exam_massive = Exam("Exam_MASSIVE_1")
    exam_massive.belongsToCourse = [prog]
    exam_massive.expectedAttendance = 120
    exam_massive.requiresEquipment = [projector]

    # Teachers teach activities
    t_ana.teaches = [lec_crp, exam_crp_small]
    t_bruno.teaches = [exam_alg, lab_prog, exam_massive]

    # ----------------------
    # Bookings (cenário de demonstração)
    # ----------------------

    # Booking_1: lecture em R101 (prio baixa) - cria conflito com Booking_3
    b1 = RoomBooking("Booking_1")
    b1.bookingRoom = r101
    b1.bookingOf = lec_crp
    b1.start = "2026-01-05T10:00"
    b1.end = "2026-01-05T12:00"
    b1.priority = 1

    # Booking_2: exame grande em R202 (prio alta)
    b2 = RoomBooking("Booking_2")
    b2.bookingRoom = r202
    b2.bookingOf = exam_alg
    b2.start = "2026-01-05T10:00"
    b2.end = "2026-01-05T13:00"
    b2.priority = 10

    # Booking_3: exame grande em R101 (propositadamente errado: capacity fail + conflito temporal)
    b3 = RoomBooking("Booking_3")
    b3.bookingRoom = r101
    b3.bookingOf = exam_alg
    b3.start = "2026-01-05T11:00"
    b3.end = "2026-01-05T12:30"
    b3.priority = 10

    # Booking_4: Lab a correr em R101 (errado por equipamento: precisa computers; R101 não tem)
    # Este booking NÃO precisa de ser conflitante; é só para aparecer em MissingEquipmentBooking
    b4 = RoomBooking("Booking_4")
    b4.bookingRoom = r101
    b4.bookingOf = lab_prog
    b4.start = "2026-01-06T09:00"
    b4.end = "2026-01-06T11:00"
    b4.priority = 1

    # Booking_5: "bloqueador" de baixa prioridade em R101 num horário onde queremos testar o repair
    # Ex.: 2026-01-05 14:00..16:00 (slot bom para demonstração)
    b5 = RoomBooking("Booking_5")
    b5.bookingRoom = r101
    b5.bookingOf = lec_crp
    b5.start = "2026-01-05T14:00"
    b5.end = "2026-01-05T16:00"
    b5.priority = 1

    return onto
