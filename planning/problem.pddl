(define (problem exam_scheduling_problem)
  (:domain exam_scheduling)

  (:objects
    e1 e2 e3 - exam
    r101 r202 r303 - room
    s1 s2 s3 - slot
    g1 g2 - group
  )

  (:init
    ;; exams start unassigned
    (unassigned e1)
    (unassigned e2)
    (unassigned e3)

    ;; room availability
    (free r101 s1) (free r101 s2) (free r101 s3)
    (free r202 s1) (free r202 s2) (free r202 s3)
    (free r303 s1) (free r303 s2) (free r303 s3)

    ;; group availability
    (group_free g1 s1) (group_free g1 s2) (group_free g1 s3)
    (group_free g2 s1) (group_free g2 s2) (group_free g2 s3)

    ;; exam-group mapping
    (belongs e1 g1)
    (belongs e2 g1)
    (belongs e3 g2)

    ;; capacity compatibility
    (cap_ok e1 r101) (cap_ok e1 r202) (cap_ok e1 r303)
    (cap_ok e2 r101) (cap_ok e2 r202)
    (cap_ok e3 r202)
  )

  (:goal
    (and
      (assigned e1)
      (assigned e2)
      (assigned e3)
    )
  )
)