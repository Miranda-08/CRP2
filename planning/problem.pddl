(define (problem dei_exam_scheduling_semester)
  (:domain exam_scheduling)

  (:objects
    ; Rooms (choose as needed; more rooms = easier planning)
    r101 r202 r303 rAud - room

    ; Time slots: 6 for Normal season (N1..N6) + 6 for Resit season (R1..R6)
    N1 N2 N3 N4 N5 N6 R1 R2 R3 R4 R5 R6 - slot

    ; Year groups (hard constraint: exams of same year cannot overlap)
    gY1 gY2 gY3 - group

    ; Exams: 15 normal + 15 resit = 30
    n_y1_c1 n_y1_c2 n_y1_c3 n_y1_c4 n_y1_c5
    n_y2_c1 n_y2_c2 n_y2_c3 n_y2_c4 n_y2_c5
    n_y3_c1 n_y3_c2 n_y3_c3 n_y3_c4 n_y3_c5
    r_y1_c1 r_y1_c2 r_y1_c3 r_y1_c4 r_y1_c5
    r_y2_c1 r_y2_c2 r_y2_c3 r_y2_c4 r_y2_c5
    r_y3_c1 r_y3_c2 r_y3_c3 r_y3_c4 r_y3_c5
    - exam
  )

  (:init
    ; ----------------------------
    ; All exams start unassigned
    ; ----------------------------
    (unassigned n_y1_c1) (unassigned n_y1_c2) (unassigned n_y1_c3) (unassigned n_y1_c4) (unassigned n_y1_c5)
    (unassigned n_y2_c1) (unassigned n_y2_c2) (unassigned n_y2_c3) (unassigned n_y2_c4) (unassigned n_y2_c5)
    (unassigned n_y3_c1) (unassigned n_y3_c2) (unassigned n_y3_c3) (unassigned n_y3_c4) (unassigned n_y3_c5)

    (unassigned r_y1_c1) (unassigned r_y1_c2) (unassigned r_y1_c3) (unassigned r_y1_c4) (unassigned r_y1_c5)
    (unassigned r_y2_c1) (unassigned r_y2_c2) (unassigned r_y2_c3) (unassigned r_y2_c4) (unassigned r_y2_c5)
    (unassigned r_y3_c1) (unassigned r_y3_c2) (unassigned r_y3_c3) (unassigned r_y3_c4) (unassigned r_y3_c5)

    ; ----------------------------
    ; Room availability (all rooms free in all slots initially)
    ; ----------------------------
    (free r101 N1) (free r101 N2) (free r101 N3) (free r101 N4) (free r101 N5) (free r101 N6)
    (free r101 R1) (free r101 R2) (free r101 R3) (free r101 R4) (free r101 R5) (free r101 R6)

    (free r202 N1) (free r202 N2) (free r202 N3) (free r202 N4) (free r202 N5) (free r202 N6)
    (free r202 R1) (free r202 R2) (free r202 R3) (free r202 R4) (free r202 R5) (free r202 R6)

    (free r303 N1) (free r303 N2) (free r303 N3) (free r303 N4) (free r303 N5) (free r303 N6)
    (free r303 R1) (free r303 R2) (free r303 R3) (free r303 R4) (free r303 R5) (free r303 R6)

    (free rAud N1) (free rAud N2) (free rAud N3) (free rAud N4) (free rAud N5) (free rAud N6)
    (free rAud R1) (free rAud R2) (free rAud R3) (free rAud R4) (free rAud R5) (free rAud R6)

    ; ----------------------------
    ; Group availability (each year can have at most 1 exam per slot)
    ; ----------------------------
    (group_free gY1 N1) (group_free gY1 N2) (group_free gY1 N3) (group_free gY1 N4) (group_free gY1 N5) (group_free gY1 N6)
    (group_free gY1 R1) (group_free gY1 R2) (group_free gY1 R3) (group_free gY1 R4) (group_free gY1 R5) (group_free gY1 R6)

    (group_free gY2 N1) (group_free gY2 N2) (group_free gY2 N3) (group_free gY2 N4) (group_free gY2 N5) (group_free gY2 N6)
    (group_free gY2 R1) (group_free gY2 R2) (group_free gY2 R3) (group_free gY2 R4) (group_free gY2 R5) (group_free gY2 R6)

    (group_free gY3 N1) (group_free gY3 N2) (group_free gY3 N3) (group_free gY3 N4) (group_free gY3 N5) (group_free gY3 N6)
    (group_free gY3 R1) (group_free gY3 R2) (group_free gY3 R3) (group_free gY3 R4) (group_free gY3 R5) (group_free gY3 R6)

    ; ----------------------------
    ; Exam -> Year group mapping (hard constraint: same year cannot overlap)
    ; ----------------------------
    (belongs n_y1_c1 gY1) (belongs n_y1_c2 gY1) (belongs n_y1_c3 gY1) (belongs n_y1_c4 gY1) (belongs n_y1_c5 gY1)
    (belongs r_y1_c1 gY1) (belongs r_y1_c2 gY1) (belongs r_y1_c3 gY1) (belongs r_y1_c4 gY1) (belongs r_y1_c5 gY1)

    (belongs n_y2_c1 gY2) (belongs n_y2_c2 gY2) (belongs n_y2_c3 gY2) (belongs n_y2_c4 gY2) (belongs n_y2_c5 gY2)
    (belongs r_y2_c1 gY2) (belongs r_y2_c2 gY2) (belongs r_y2_c3 gY2) (belongs r_y2_c4 gY2) (belongs r_y2_c5 gY2)

    (belongs n_y3_c1 gY3) (belongs n_y3_c2 gY3) (belongs n_y3_c3 gY3) (belongs n_y3_c4 gY3) (belongs n_y3_c5 gY3)
    (belongs r_y3_c1 gY3) (belongs r_y3_c2 gY3) (belongs r_y3_c3 gY3) (belongs r_y3_c4 gY3) (belongs r_y3_c5 gY3)

    ; ----------------------------
    ; Period constraint: Normal exams only in N slots; Resit exams only in R slots
    ; (Requires period_ok(e,s) predicate in the domain + precondition in assign_exam)
    ; ----------------------------
    ; Normal exams allowed in N1..N6
    (period_ok n_y1_c1 N1) (period_ok n_y1_c1 N2) (period_ok n_y1_c1 N3) (period_ok n_y1_c1 N4) (period_ok n_y1_c1 N5) (period_ok n_y1_c1 N6)
    (period_ok n_y1_c2 N1) (period_ok n_y1_c2 N2) (period_ok n_y1_c2 N3) (period_ok n_y1_c2 N4) (period_ok n_y1_c2 N5) (period_ok n_y1_c2 N6)
    (period_ok n_y1_c3 N1) (period_ok n_y1_c3 N2) (period_ok n_y1_c3 N3) (period_ok n_y1_c3 N4) (period_ok n_y1_c3 N5) (period_ok n_y1_c3 N6)
    (period_ok n_y1_c4 N1) (period_ok n_y1_c4 N2) (period_ok n_y1_c4 N3) (period_ok n_y1_c4 N4) (period_ok n_y1_c4 N5) (period_ok n_y1_c4 N6)
    (period_ok n_y1_c5 N1) (period_ok n_y1_c5 N2) (period_ok n_y1_c5 N3) (period_ok n_y1_c5 N4) (period_ok n_y1_c5 N5) (period_ok n_y1_c5 N6)

    (period_ok n_y2_c1 N1) (period_ok n_y2_c1 N2) (period_ok n_y2_c1 N3) (period_ok n_y2_c1 N4) (period_ok n_y2_c1 N5) (period_ok n_y2_c1 N6)
    (period_ok n_y2_c2 N1) (period_ok n_y2_c2 N2) (period_ok n_y2_c2 N3) (period_ok n_y2_c2 N4) (period_ok n_y2_c2 N5) (period_ok n_y2_c2 N6)
    (period_ok n_y2_c3 N1) (period_ok n_y2_c3 N2) (period_ok n_y2_c3 N3) (period_ok n_y2_c3 N4) (period_ok n_y2_c3 N5) (period_ok n_y2_c3 N6)
    (period_ok n_y2_c4 N1) (period_ok n_y2_c4 N2) (period_ok n_y2_c4 N3) (period_ok n_y2_c4 N4) (period_ok n_y2_c4 N5) (period_ok n_y2_c4 N6)
    (period_ok n_y2_c5 N1) (period_ok n_y2_c5 N2) (period_ok n_y2_c5 N3) (period_ok n_y2_c5 N4) (period_ok n_y2_c5 N5) (period_ok n_y2_c5 N6)

    (period_ok n_y3_c1 N1) (period_ok n_y3_c1 N2) (period_ok n_y3_c1 N3) (period_ok n_y3_c1 N4) (period_ok n_y3_c1 N5) (period_ok n_y3_c1 N6)
    (period_ok n_y3_c2 N1) (period_ok n_y3_c2 N2) (period_ok n_y3_c2 N3) (period_ok n_y3_c2 N4) (period_ok n_y3_c2 N5) (period_ok n_y3_c2 N6)
    (period_ok n_y3_c3 N1) (period_ok n_y3_c3 N2) (period_ok n_y3_c3 N3) (period_ok n_y3_c3 N4) (period_ok n_y3_c3 N5) (period_ok n_y3_c3 N6)
    (period_ok n_y3_c4 N1) (period_ok n_y3_c4 N2) (period_ok n_y3_c4 N3) (period_ok n_y3_c4 N4) (period_ok n_y3_c4 N5) (period_ok n_y3_c4 N6)
    (period_ok n_y3_c5 N1) (period_ok n_y3_c5 N2) (period_ok n_y3_c5 N3) (period_ok n_y3_c5 N4) (period_ok n_y3_c5 N5) (period_ok n_y3_c5 N6)

    ; Resit exams allowed in R1..R6
    (period_ok r_y1_c1 R1) (period_ok r_y1_c1 R2) (period_ok r_y1_c1 R3) (period_ok r_y1_c1 R4) (period_ok r_y1_c1 R5) (period_ok r_y1_c1 R6)
    (period_ok r_y1_c2 R1) (period_ok r_y1_c2 R2) (period_ok r_y1_c2 R3) (period_ok r_y1_c2 R4) (period_ok r_y1_c2 R5) (period_ok r_y1_c2 R6)
    (period_ok r_y1_c3 R1) (period_ok r_y1_c3 R2) (period_ok r_y1_c3 R3) (period_ok r_y1_c3 R4) (period_ok r_y1_c3 R5) (period_ok r_y1_c3 R6)
    (period_ok r_y1_c4 R1) (period_ok r_y1_c4 R2) (period_ok r_y1_c4 R3) (period_ok r_y1_c4 R4) (period_ok r_y1_c4 R5) (period_ok r_y1_c4 R6)
    (period_ok r_y1_c5 R1) (period_ok r_y1_c5 R2) (period_ok r_y1_c5 R3) (period_ok r_y1_c5 R4) (period_ok r_y1_c5 R5) (period_ok r_y1_c5 R6)

    (period_ok r_y2_c1 R1) (period_ok r_y2_c1 R2) (period_ok r_y2_c1 R3) (period_ok r_y2_c1 R4) (period_ok r_y2_c1 R5) (period_ok r_y2_c1 R6)
    (period_ok r_y2_c2 R1) (period_ok r_y2_c2 R2) (period_ok r_y2_c2 R3) (period_ok r_y2_c2 R4) (period_ok r_y2_c2 R5) (period_ok r_y2_c2 R6)
    (period_ok r_y2_c3 R1) (period_ok r_y2_c3 R2) (period_ok r_y2_c3 R3) (period_ok r_y2_c3 R4) (period_ok r_y2_c3 R5) (period_ok r_y2_c3 R6)
    (period_ok r_y2_c4 R1) (period_ok r_y2_c4 R2) (period_ok r_y2_c4 R3) (period_ok r_y2_c4 R4) (period_ok r_y2_c4 R5) (period_ok r_y2_c4 R6)
    (period_ok r_y2_c5 R1) (period_ok r_y2_c5 R2) (period_ok r_y2_c5 R3) (period_ok r_y2_c5 R4) (period_ok r_y2_c5 R5) (period_ok r_y2_c5 R6)

    (period_ok r_y3_c1 R1) (period_ok r_y3_c1 R2) (period_ok r_y3_c1 R3) (period_ok r_y3_c1 R4) (period_ok r_y3_c1 R5) (period_ok r_y3_c1 R6)
    (period_ok r_y3_c2 R1) (period_ok r_y3_c2 R2) (period_ok r_y3_c2 R3) (period_ok r_y3_c2 R4) (period_ok r_y3_c2 R5) (period_ok r_y3_c2 R6)
    (period_ok r_y3_c3 R1) (period_ok r_y3_c3 R2) (period_ok r_y3_c3 R3) (period_ok r_y3_c3 R4) (period_ok r_y3_c3 R5) (period_ok r_y3_c3 R6)
    (period_ok r_y3_c4 R1) (period_ok r_y3_c4 R2) (period_ok r_y3_c4 R3) (period_ok r_y3_c4 R4) (period_ok r_y3_c4 R5) (period_ok r_y3_c4 R6)
    (period_ok r_y3_c5 R1) (period_ok r_y3_c5 R2) (period_ok r_y3_c5 R3) (period_ok r_y3_c5 R4) (period_ok r_y3_c5 R5) (period_ok r_y3_c5 R6)

    ; ----------------------------
    ; Capacity compatibility (cap_ok)
    ; Model (reasonable, simple):
    ; - Year 1 exams: fit in all rooms (r303 small room included)
    ; - Year 2 exams: fit in r101, r202, rAud (not r303)
    ; - Year 3 exams: fit only in r202, rAud (bigger cohorts)
    ; Apply same logic to Normal + Resit.
    ; ----------------------------

    ; Year 1 (normal)
    (cap_ok n_y1_c1 r101) (cap_ok n_y1_c1 r202) (cap_ok n_y1_c1 r303) (cap_ok n_y1_c1 rAud)
    (cap_ok n_y1_c2 r101) (cap_ok n_y1_c2 r202) (cap_ok n_y1_c2 r303) (cap_ok n_y1_c2 rAud)
    (cap_ok n_y1_c3 r101) (cap_ok n_y1_c3 r202) (cap_ok n_y1_c3 r303) (cap_ok n_y1_c3 rAud)
    (cap_ok n_y1_c4 r101) (cap_ok n_y1_c4 r202) (cap_ok n_y1_c4 r303) (cap_ok n_y1_c4 rAud)
    (cap_ok n_y1_c5 r101) (cap_ok n_y1_c5 r202) (cap_ok n_y1_c5 r303) (cap_ok n_y1_c5 rAud)

    ; Year 2 (normal)
    (cap_ok n_y2_c1 r101) (cap_ok n_y2_c1 r202) (cap_ok n_y2_c1 rAud)
    (cap_ok n_y2_c2 r101) (cap_ok n_y2_c2 r202) (cap_ok n_y2_c2 rAud)
    (cap_ok n_y2_c3 r101) (cap_ok n_y2_c3 r202) (cap_ok n_y2_c3 rAud)
    (cap_ok n_y2_c4 r101) (cap_ok n_y2_c4 r202) (cap_ok n_y2_c4 rAud)
    (cap_ok n_y2_c5 r101) (cap_ok n_y2_c5 r202) (cap_ok n_y2_c5 rAud)

    ; Year 3 (normal)
    (cap_ok n_y3_c1 r202) (cap_ok n_y3_c1 rAud)
    (cap_ok n_y3_c2 r202) (cap_ok n_y3_c2 rAud)
    (cap_ok n_y3_c3 r202) (cap_ok n_y3_c3 rAud)
    (cap_ok n_y3_c4 r202) (cap_ok n_y3_c4 rAud)
    (cap_ok n_y3_c5 r202) (cap_ok n_y3_c5 rAud)

    ; Year 1 (resit)
    (cap_ok r_y1_c1 r101) (cap_ok r_y1_c1 r202) (cap_ok r_y1_c1 r303) (cap_ok r_y1_c1 rAud)
    (cap_ok r_y1_c2 r101) (cap_ok r_y1_c2 r202) (cap_ok r_y1_c2 r303) (cap_ok r_y1_c2 rAud)
    (cap_ok r_y1_c3 r101) (cap_ok r_y1_c3 r202) (cap_ok r_y1_c3 r303) (cap_ok r_y1_c3 rAud)
    (cap_ok r_y1_c4 r101) (cap_ok r_y1_c4 r202) (cap_ok r_y1_c4 r303) (cap_ok r_y1_c4 rAud)
    (cap_ok r_y1_c5 r101) (cap_ok r_y1_c5 r202) (cap_ok r_y1_c5 r303) (cap_ok r_y1_c5 rAud)

    ; Year 2 (resit)
    (cap_ok r_y2_c1 r101) (cap_ok r_y2_c1 r202) (cap_ok r_y2_c1 rAud)
    (cap_ok r_y2_c2 r101) (cap_ok r_y2_c2 r202) (cap_ok r_y2_c2 rAud)
    (cap_ok r_y2_c3 r101) (cap_ok r_y2_c3 r202) (cap_ok r_y2_c3 rAud)
    (cap_ok r_y2_c4 r101) (cap_ok r_y2_c4 r202) (cap_ok r_y2_c4 rAud)
    (cap_ok r_y2_c5 r101) (cap_ok r_y2_c5 r202) (cap_ok r_y2_c5 rAud)

    ; Year 3 (resit)
    (cap_ok r_y3_c1 r202) (cap_ok r_y3_c1 rAud)
    (cap_ok r_y3_c2 r202) (cap_ok r_y3_c2 rAud)
    (cap_ok r_y3_c3 r202) (cap_ok r_y3_c3 rAud)
    (cap_ok r_y3_c4 r202) (cap_ok r_y3_c4 rAud)
    (cap_ok r_y3_c5 r202) (cap_ok r_y3_c5 rAud)
  )

  (:goal
    (and
      ; All Normal exams assigned
      (assigned n_y1_c1) (assigned n_y1_c2) (assigned n_y1_c3) (assigned n_y1_c4) (assigned n_y1_c5)
      (assigned n_y2_c1) (assigned n_y2_c2) (assigned n_y2_c3) (assigned n_y2_c4) (assigned n_y2_c5)
      (assigned n_y3_c1) (assigned n_y3_c2) (assigned n_y3_c3) (assigned n_y3_c4) (assigned n_y3_c5)

      ; All Resit exams assigned
      (assigned r_y1_c1) (assigned r_y1_c2) (assigned r_y1_c3) (assigned r_y1_c4) (assigned r_y1_c5)
      (assigned r_y2_c1) (assigned r_y2_c2) (assigned r_y2_c3) (assigned r_y2_c4) (assigned r_y2_c5)
      (assigned r_y3_c1) (assigned r_y3_c2) (assigned r_y3_c3) (assigned r_y3_c4) (assigned r_y3_c5)
    )
  )
)