(define (problem ball_gripper_problem)
    (:domain ball_gripper_domain)
    (:objects ball1 ball2 ball3 ball4 left right rooma roomb)
    (:init
        (BALL ball1)
        (BALL ball2)
        (BALL ball3)
        (BALL ball4)
        
        (GRIPPER left)
        (GRIPPER right)
        
        (ROOM rooma)
        (ROOM roomb)
        
        (at-ball ball1 rooma)
        (at-ball ball2 rooma)
        (at-ball ball3 rooma)
        (at-ball ball4 rooma)
        (at-robot rooma)
        (free left)
        (free right)
        
        (unassigned e1)
        (unassigned e2)
        (unassigned e3)

        (free r101 s1) (free r101 s2) (free r101 s3)
        (free r202 s1) (free r202 s2) (free r202 s3)
        (free r303 s1) (free r303 s2) (free r303 s3)

        (cap_ok e1 r101) (cap_ok e1 r202) (cap_ok e1 r303)
        (cap_ok e2 r101) (cap_ok e2 r202)
        (cap_ok e3 r202)
    )
    (:goal (and
        (assigned e1)
        (assigned e2)
        (assigned e3)
        )
    )
)