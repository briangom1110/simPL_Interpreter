import simpl_types as types
import infer

#for testing
def typeof(expr):
    env = types.default_type_env()
    tr = infer.infer_expr(env, expr)
    return tr.subst.apply(tr.type)