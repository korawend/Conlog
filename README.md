# Conlog

## SMT (Satisfying Maze Traversal) Solver




`next_lcm_machine.cla`:

```

    [comment__computes_x_the_next_lcm_of_all_the_numbers=0]


    (Start)---+
              |
              |
              |
              |
              |
          (dummy+=x)               +------+----+--(db++?x)         +------+----+--(db++?x)
              |                    |      |    |     |             |      |    |     |
              |                    |   (x-=3)  |  (neg_x-=x)       |   (x-=7)  |  (neg_x-=x)
           (da-=1)                 |      |    |     |             |      |    |     |
              |                    |      +----+ (db++?neg_x)      |      +----+ (db++?neg_x)
          (db++?da)                |                 |             |                 |
              |                    |             (neg_x+=x)        |             (neg_x+=x)
           (da+=1)                 |                 |             |                 |
              |                    +------+   +--(x+=dummy)        +------+   +--(x+=dummy)
              |                           |   |                           |   |
              +------+----+--(db++?x)     |   +------+----+--(db++?x)     |   +------+----+--(db++?x)
                     |    |     |         |          |    |     |         |          |    |     |         |----------|
                  (x-=12) |  (neg_x-=x)   |       (x-=4)  |  (neg_x-=x)   |       (x-=6)  |  (neg_x-=x)   |          |
                     |    |     |         |          |    |     |         |          |    |     |         |          |
                     +----+ (db++?neg_x)  |          +----+ (db++?neg_x)  |          +----+ (db++?neg_x)  |          |
                                |         |                     |         |                     |         |          |
                            (neg_x+=x)    |                 (neg_x+=x)    |                 (neg_x+=x)    |          |
                                |         |                     |         |                     |         |          |
                            (x+=dummy)    |                 (x+=dummy)    |                     |         |          |
                                |         |                     |         |                     |         |          |
                                +---------+                     +---------+                     +---------+          |
                                                                                                                     |
                                                                                                                     |
                                                                                                                     |
                                                                                                                     |
                                +------------------------------------------------------------------------------------+
                                |
                                |               +-(dummy-=1)-+
                                |               |            |
                                +---(dummy-=42)-+------------+-(da-=1)-(End)

    [x=?]
    [dummy=0]
    [neg_x=0]
    [da=1]
    [db=0]


```

Output: `x = 84`

