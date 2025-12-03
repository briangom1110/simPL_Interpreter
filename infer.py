from __future__ import annotations
import abstract
import simpl_types as types

tvgen = types.TypeVarGen()


def infer_expr(env: types.TypeEnv, expr: abstract.Expression) -> types.TypeResult:

    # literals 
    if isinstance(expr, abstract.IntegerLiteral):
        return types.TypeResult(types.Substitution.identity(), types.INT)

    if isinstance(expr, abstract.BooleanLiteral):
        return types.TypeResult(types.Substitution.identity(), types.BOOL)

    if isinstance(expr, abstract.NilLiteral):
        a = tvgen.fresh()
        return types.TypeResult(types.Substitution.identity(), types.ListType(a))

    if isinstance(expr, abstract.UnitLiteral):
        return types.TypeResult(types.Substitution.identity(), types.UNIT)

    # variable implementation

    if isinstance(expr, abstract.Var):
        t = env.get(expr.name)
        if t is None:
            raise Exception("Type Error")
        return types.TypeResult(types.Substitution.identity(), t)

    # operations
    if isinstance(expr, abstract.UnaryOperation):
        tr_e = infer_expr(env, expr.expr)
        s = tr_e.subst
        t_e = s.apply(tr_e.type)

        if expr.op == "~":
            s2 = t_e.unify(types.INT)
            return types.TypeResult(s2.compose(s), types.INT)

        if expr.op == "not":
            s2 = t_e.unify(types.BOOL)
            return types.TypeResult(s2.compose(s), types.BOOL)

        if expr.op == "!":
            a = tvgen.fresh()
            s2 = t_e.unify(types.RefType(a))
            return types.TypeResult(s2.compose(s), s2.apply(a))

        raise Exception("Type Error")

    if isinstance(expr, abstract.BinaryOperation):
        op = expr.op

        if op == ";":
            tr1 = infer_expr(env, expr.left)
            env1 = env.apply(tr1.subst)
            tr2 = infer_expr(env1, expr.right)
            s_total = tr2.subst.compose(tr1.subst)

            return types.TypeResult(s_total, s_total.apply(tr2.type))


        if op == ":=":
            tr1 = infer_expr(env, expr.left)
            env1 = env.apply(tr1.subst)
            tr2 = infer_expr(env1, expr.right)
            s = tr2.subst.compose(tr1.subst)
            t1 = s.apply(tr1.type)
            t2 = s.apply(tr2.type)
            a = tvgen.fresh()

            s1 = t1.unify(types.RefType(a))
            s2 = s1.apply(t2).unify(s1.apply(a))
            s_total = s2.compose(s1).compose(s)

            return types.TypeResult(s_total, types.UNIT)

        if op == "::":
            tr1 = infer_expr(env, expr.left)
            env1 = env.apply(tr1.subst)
            tr2 = infer_expr(env1, expr.right)
            s = tr2.subst.compose(tr1.subst)

            t1 = s.apply(tr1.type)
            t2 = s.apply(tr2.type)

            s1 = t2.unify(types.ListType(t1))
            return types.TypeResult(s1.compose(s), s1.apply(types.ListType(t1)))


        if op in {"+", "-", "*", "/", "%"}:
            tr1 = infer_expr(env, expr.left)
            env1 = env.apply(tr1.subst)
            tr2 = infer_expr(env1, expr.right)
            s = tr2.subst.compose(tr1.subst)

            t1 = s.apply(tr1.type)
            t2 = s.apply(tr2.type)

            s1 = t1.unify(types.INT)
            s2 = s1.apply(t2).unify(types.INT)
            return types.TypeResult(s2.compose(s1).compose(s), types.INT)

        if op in {"andalso", "orelse"}:
            tr1 = infer_expr(env, expr.left)
            env1 = env.apply(tr1.subst)
            tr2 = infer_expr(env1, expr.right)

            s = tr2.subst.compose(tr1.subst)
            t1 = s.apply(tr1.type)
            t2 = s.apply(tr2.type)

            s1 = t1.unify(types.BOOL)
            s2 = s1.apply(t2).unify(types.BOOL)

            return types.TypeResult(s2.compose(s1).compose(s), types.BOOL)


        if op in {"<", "<=", ">", ">=", "=", "<>"}:
            tr1 = infer_expr(env, expr.left)
            env1 = env.apply(tr1.subst)
            tr2 = infer_expr(env1, expr.right)
            s = tr2.subst.compose(tr1.subst)

            t1 = s.apply(tr1.type)
            t2 = s.apply(tr2.type)

            if op in {"<", "<=", ">", ">=",}:
                s1 = t1.unify(types.INT)
                s2 = s1.apply(t2).unify(types.INT)

                return types.TypeResult(s2.compose(s1).compose(s), types.BOOL)

            else:  # "=" or "<>"
                s1 = t1.unify(t2)

                return types.TypeResult(s1.compose(s), types.BOOL)

        raise Exception("Type Error")


    # complete the rest later
    if isinstance(expr, abstract.Func):
        a = tvgen.fresh()
        env1 = env.extend(expr.param, a)
        tr_body = infer_expr(env1, expr.body)
        s = tr_body.subst

        t_arg = s.apply(a)
        t_ret = s.apply(tr_body.type)
        return types.TypeResult(s, types.ArrowType(t_arg, t_ret))


    if isinstance(expr, abstract.Rec):
        a = tvgen.fresh()
        env1 = env.extend(expr.name, a)
        tr_body = infer_expr(env1, expr.body)
        s = tr_body.subst
        t_body = s.apply(tr_body.type)

        s1 = t_body.unify(s.apply(a))
        s_total = s1.compose(s)
        return types.TypeResult(s_total, s_total.apply(t_body))


    if isinstance(expr, abstract.Apply):
        tr_f = infer_expr(env, expr.func)
        env1 = env.apply(tr_f.subst)

        tr_arg = infer_expr(env1, expr.arg)
        s = tr_arg.subst.compose(tr_f.subst)

        t_f = s.apply(tr_f.type)
        t_arg = s.apply(tr_arg.type)

        a = tvgen.fresh()
        s1 = t_f.unify(types.ArrowType(t_arg, a))
        s_total = s1.compose(s)
        return types.TypeResult(s_total, s_total.apply(a))


    if isinstance(expr, abstract.Let):
        tr_val = infer_expr(env, expr.value)
        env1 = env.apply(tr_val.subst).extend(expr.name, tr_val.subst.apply(tr_val.type))
        tr_body = infer_expr(env1, expr.body)
        s_total = tr_body.subst.compose(tr_val.subst)
        return types.TypeResult(s_total, s_total.apply(tr_body.type))


    if isinstance(expr, abstract.If):
        tr_c = infer_expr(env, expr.condition)
        env1 = env.apply(tr_c.subst)

        tr_t = infer_expr(env1, expr.then_branch)
        env2 = env1.apply(tr_t.subst)

        tr_e = infer_expr(env2, expr.else_branch)

        s = tr_e.subst.compose(tr_t.subst).compose(tr_c.subst)
        t_c = s.apply(tr_c.type)
        t_t = s.apply(tr_t.type)
        t_e = s.apply(tr_e.type)

        s1 = t_c.unify(types.BOOL)
        s2 = s1.apply(t_t).unify(s1.apply(t_e))
        return types.TypeResult(s2.compose(s1).compose(s), s2.apply(t_t))

    if isinstance(expr, abstract.While):
        tr_c = infer_expr(env, expr.condition)
        env1 = env.apply(tr_c.subst)
        tr_b = infer_expr(env1, expr.body)

        s = tr_b.subst.compose(tr_c.subst)
        t_c = s.apply(tr_c.type)
        s1 = t_c.unify(types.BOOL)
        return types.TypeResult(s1.compose(s), types.UNIT)

    if isinstance(expr, abstract.Pair):
        tr1 = infer_expr(env, expr.left)
        env1 = env.apply(tr1.subst)
        tr2 = infer_expr(env1, expr.right)
        s = tr2.subst.compose(tr1.subst)

        t1 = s.apply(tr1.type)
        t2 = s.apply(tr2.type)
        return types.TypeResult(s, types.PairType(t1, t2))


    if isinstance(expr, abstract.Ref):
        tr = infer_expr(env, expr.expr)
        s = tr.subst
        t = s.apply(tr.type)
        return types.TypeResult(s, types.RefType(t))

    raise Exception("Type Error")