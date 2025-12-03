import sys
import lexigraphical
import parser
import simpl_types as types
import infer
import interp
import state
import values
import simpl_builtins as builtins


def pp_value(v):
    
    # int
    if isinstance(v, values.IntVal):
        return str(v.value)
    
    # bool
    if isinstance(v, values.BoolVal):
        return "true" if v.value else "false"
    
    # nil
    if isinstance(v, values.NilVal):
        return "nil"
    
    # unit
    if isinstance(v, values.UnitVal):
        return "unit"
    
    # list
    if isinstance(v, values.ConsVal):
        return f"list@{list_length(v)}"
    
    # reference
    if isinstance(v, values.RefVal):
        # Print *content* not address
        # Section 7.1: "ref@<content>"
        return f"ref@{pp_value(load_ref(v))}"
    
    # pair
    if isinstance(v, values.PairVal):
        # pair@v1@v2
        return f"pair@{pp_value(v.fst)}@{pp_value(v.snd)}"
    
    # function
    if isinstance(v, values.FunVal) or isinstance(v, values.RecVal):
        return "fun"
    
    return "runtime error"   # fallback


def list_length(lst):

    count = 0
    cur = lst
    while isinstance(cur, values.ConsVal):
        count += 1
        cur = cur.tail
    return count


def load_ref(refval):

    global LAST_MEM
    return LAST_MEM.read(refval.addr)

def run_simpl_program(path):
    global LAST_MEM

    try:
        code = open(path, "r").read()
    except:
        print("runtime error")
        return
    
    try:
        lexer = lexigraphical.Lexer(code)
        parser_obj = parser.Parser(lexer)
        expr = parser_obj.parse()
    except Exception:
        print("syntax error")
        return
    

    try:
        env = types.default_type_env()
        tr = infer.infer_expr(env, expr)
    except Exception:
        print("type error")
        return
    
    try:
        st = state.State(env=builtins.initial_runtime_env(),mem=state.Mem())
        st_final, v = interp.eval_expr(expr, st)
        LAST_MEM = st_final.mem
    except Exception as e:
        print("runtime error:", repr(e))
        return

    
    print(pp_value(v))


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("runtime error")  # Must supply exactly one argument
        sys.exit(1)
    
    run_simpl_program(sys.argv[1])