(define (domain ball_gripper_domain)
    (:predicates (BALL ?x)  (GRIPPER ?x)  (ROOM ?x)  (at-ball ?x ?y)  (at-robot ?x)  (carry ?x ?y)  (free ?x))
    (:action drop
        :parameters (?x ?y ?z)
        :precondition (and (BALL ?x) (ROOM ?y) (GRIPPER ?z) (carry ?z ?x) (at-robot ?y))
        :effect (and (at-ball ?x ?y) (free ?z) (not (carry ?z ?x)))
    )
    (:action move
        :parameters (?x ?y)
        :precondition (and (ROOM ?x) (ROOM ?y) (at-robot ?x))
        :effect (and (at-robot ?y) (not (at-robot ?x)))
    )
    (:action pickup
        :parameters (?x ?y ?z)
        :precondition (and (BALL ?x) (ROOM ?y) (GRIPPER ?z) (at-ball ?x ?y) (at-robot ?y) (free ?z))
        :effect (and (carry ?z ?x) (not (at-ball ?x ?y)) (not (free ?z)))
    )
)