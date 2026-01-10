(define (domain exam_scheduling)
  (:requirements :strips :typing)
  (:types exam room slot group)

  (:predicates
    (unassigned ?e - exam)
    (assigned ?e - exam)
    (at ?e - exam ?r - room ?s - slot)
    (free ?r - room ?s - slot)
    (cap_ok ?e - exam ?r - room)

    (belongs ?e - exam ?g - group)
    (group_free ?g - group ?s - slot)

    (period_ok ?e - exam ?s - slot)
  )

  (:action assign_exam
    :parameters (?e - exam ?r - room ?s - slot ?g - group)
    :precondition (and
      (unassigned ?e)
      (free ?r ?s)
      (cap_ok ?e ?r)
      (belongs ?e ?g)
      (group_free ?g ?s)
      (period_ok ?e ?s)
    )
    :effect (and
      (assigned ?e)
      (not (unassigned ?e))
      (at ?e ?r ?s)
      (not (free ?r ?s))
      (not (group_free ?g ?s))
    )
  )
)