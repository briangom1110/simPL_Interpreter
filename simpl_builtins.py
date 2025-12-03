import abstract
import values
import state

# Builtin function implementations
def builtin_fst(arg):
    if not isinstance(arg, values.PairVal):
        raise Exception("Runtime Error")
    return arg.fst


def builtin_snd(arg):
    if not isinstance(arg, values.PairVal):
        raise Exception("Runtime Error")
    return arg.snd


def builtin_hd(arg):
    if isinstance(arg, values.ConsVal):
        return arg.head
    raise Exception("Runtime Error")


def builtin_tl(arg):
    if isinstance(arg, values.ConsVal):
        return arg.tail
    raise Exception("Runtime Error")

def make_builtin_fun(param, py_func):
    return values.FunVal(
        env=state.Env({}),
        param=param,       
        body=abstract.Builtin(py_func)
    )

# Initial environmen
def initial_runtime_env():
    return state.Env({
        "fst": make_builtin_fun("p", builtin_fst),
        "snd": make_builtin_fun("p", builtin_snd),
        "hd":  make_builtin_fun("xs", builtin_hd),
        "tl":  make_builtin_fun("xs", builtin_tl),
    })