from typeof import typeof
from interp import eval_expr
from state import State, Env, Mem

def run(expr):

    # type check first
    try:
        t = typeof(expr)
    except Exception as e:
        raise RuntimeError("Type Error")

    # evaluate
    init = State(env=Env({}), mem=Mem())
    st, v = eval_expr(expr, init)
    return (v, t)