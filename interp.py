from dataclasses import replace
import abstract
import values
import state
import simpl_builtins as builtins


class RuntimeError_(Exception):
    pass


def eval_expr(expr: abstract.Expression, st: state.State):
    E = st.env
    M = st.mem

    # literals implementation
    if isinstance(expr, abstract.IntegerLiteral):
        return st, values.IntVal(expr.value)

    if isinstance(expr, abstract.BooleanLiteral):
        return st, values.BoolVal(expr.value)

    if isinstance(expr, abstract.NilLiteral):
        return st, values.NilVal()

    if isinstance(expr, abstract.UnitLiteral):
        return st, values.UnitVal()

    # varialbes 
    if isinstance(expr, abstract.Var):
        return st, E.lookup(expr.name)

    # ref 
    if isinstance(expr, abstract.Ref):
        st1, v = eval_expr(expr.expr, st)
        addr = st1.alloc(v)
        return st1, values.RefVal(addr)

    # Operations implementation
    if isinstance(expr, abstract.UnaryOperation):
        op = expr.op
        st1, v = eval_expr(expr.expr, st)

        if op == "~":
            if not isinstance(v, values.IntVal):
                raise Exception("Runtime Error")
            return st1, values.IntVal(-v.value)

        if op == "not":
            if not isinstance(v, values.BoolVal):
                raise Exception("Runtime Error")
            return st1, values.BoolVal(not v.value)

        if op == "!":
            if not isinstance(v, values.RefVal):
                raise Exception("Runtime Error")
            return st1, st1.mem.read(v.addr)

        raise Exception("Runtime Error")

    if isinstance(expr, abstract.BinaryOperation):
        op = expr.op

        # sequence
        if op == ";":
            st1, _ = eval_expr(expr.left, st)
            return eval_expr(expr.right, st1)

        # assignment
        if op == ":=":
            st1, r = eval_expr(expr.left, st)
            st2, v = eval_expr(expr.right, st1)

            if not isinstance(r, values.RefVal):
                raise Exception("Runtime Error")
            st2.mem.write(r.addr, v)
            return st2, values.UnitVal()

        # cons
        if op == "::":
            st1, h = eval_expr(expr.left, st)
            st2, t = eval_expr(expr.right, st1)

            if not isinstance(t, (values.NilVal, values.ConsVal)):
                raise Exception("Runtime Error")
            return st2, values.ConsVal(h, t)

        # arithmetic ops
        if op in {"+", "-", "*", "/", "%"}:
            st1, v1 = eval_expr(expr.left, st)
            st2, v2 = eval_expr(expr.right, st1)

            if not (isinstance(v1, values.IntVal) and isinstance(v2, values.IntVal)):
                raise Exception("Runtime Error")

            a, b = v1.value, v2.value
            if op == "+":
                return st2, values.IntVal(a + b)
            if op == "-":
                return st2, values.IntVal(a - b)
            if op == "*":
                return st2, values.IntVal(a * b)
            if op == "/":
                if b == 0:
                    raise Exception("Runtime Error")
                return st2, values.IntVal(a // b)
            if op == "%":
                if b == 0:
                    raise Exception("Runtime Error")
                return st2, values.IntVal(a % b)

        # relational ops
        if op in {"<", "<=", ">", ">=", "=", "<>"}:
            st1, v1 = eval_expr(expr.left, st)
            st2, v2 = eval_expr(expr.right, st1)

            if not (isinstance(v1, values.IntVal) and isinstance(v2, values.IntVal)):
                raise Exception("Runtime Error")

            a, b = v1.value, v2.value
            if op == "<":
                return st2, values.BoolVal(a < b)
            if op == "<=":
                return st2, values.BoolVal(a <= b)
            if op == ">":
                return st2, values.BoolVal(a > b)
            if op == ">=":
                return st2, values.BoolVal(a >= b)
            if op == "=":
                return st2, values.BoolVal(a == b)
            if op == "<>":
                return st2, values.BoolVal(a != b)

        # boolean operations
        if op == "andalso":
            st1, v1 = eval_expr(expr.left, st)
            if not isinstance(v1, values.BoolVal):
                raise Exception("Runtime Error")
            if not v1.value:
                return st1, values.BoolVal(False)
            return eval_expr(expr.right, st1)

        if op == "orelse":
            st1, v1 = eval_expr(expr.left, st)
            if not isinstance(v1, values.BoolVal):
                raise Exception("Runtime Error")
            if v1.value:
                return st1, values.BoolVal(True)
            return eval_expr(expr.right, st1)

        raise Exception("Runtime Error")

    # funciton and recursive, app
    if isinstance(expr, abstract.Func):
        return st, values.FunVal(E, expr.param, expr.body)

    if isinstance(expr, abstract.Rec):
        rv = values.RecVal(E, expr.name, expr.body)
        return st, rv


    if isinstance(expr, abstract.Apply):
        st1, vf = eval_expr(expr.func, st)

        #Why is this not working
        if isinstance(vf, values.RecVal):
    
            func = vf.body
            fun_env = vf.env.extend(vf.name, vf)
            vf = values.FunVal(fun_env, func.param, func.body)

        # must be a function now
        if not isinstance(vf, values.FunVal):
            raise Exception("Runtime Error")

        from abstract import Builtin
        if isinstance(vf.body, Builtin):
            st_arg, arg_val = eval_expr(expr.arg, st1)
            try:
                result = vf.body.fn(arg_val)
            except Exception:
                raise Exception("Runtime Error")
            return st_arg, result

        st2, va = eval_expr(expr.arg, st1)
        new_env = vf.env.extend(vf.param, va)
        st_call = replace(st2, env=new_env)
        return eval_expr(vf.body, st_call)


    if isinstance(expr, abstract.Let):
        st1, v1 = eval_expr(expr.value, st)
        new_env = st1.env.extend(expr.name, v1)
        st1 = replace(st1, env=new_env)
        return eval_expr(expr.body, st1)

    if isinstance(expr, abstract.If):
        st1, vc = eval_expr(expr.condition, st)
        if not isinstance(vc, values.BoolVal):
            raise Exception("Runtime Error")
        if vc.value:
            return eval_expr(expr.then_branch, st1)
        else:
            return eval_expr(expr.else_branch, st1)

    if isinstance(expr, abstract.While):
        cur = st
        while True:
            st1, vc = eval_expr(expr.condition, cur)
            if not isinstance(vc, values.BoolVal):
                raise Exception("Runtime Error")
            if not vc.value:
                return st1, values.UnitVal()
            st2, _ = eval_expr(expr.body, st1)
            cur = st2


    if isinstance(expr, abstract.Pair):
        st1, v1 = eval_expr(expr.left, st)
        st2, v2 = eval_expr(expr.right, st1)
        return st2, values.PairVal(v1, v2)

    raise Exception("Runtime Error")