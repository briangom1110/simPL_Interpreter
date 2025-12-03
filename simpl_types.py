from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional, Tuple, Any

class TypeError(Exception):
    pass


class TypeMismatchError(TypeError):
    pass


class TypeCircularityError(TypeError):
    pass


class Type:
    def is_equality_type(self) -> bool:
        raise NotImplementedError

    def contains(self, tv: "TypeVar") -> bool:
        raise NotImplementedError

    def replace(self, tv: "TypeVar", t: "Type") -> "Type":
        raise NotImplementedError

    def unify(self, other: "Type") -> "Substitution":
        raise NotImplementedError

# Type definitions

@dataclass(eq=False)
class TypeVar(Type):
    id: int

    def is_equality_type(self) -> bool:
        # type variables are equality types, subject to later constraints
        return True

    def contains(self, tv: "TypeVar") -> bool:
        return self is tv

    def replace(self, tv: "TypeVar", t: Type) -> Type:
        return t if self is tv else self

    def unify(self, other: Type) -> "Substitution":
        if self is other:
            return Substitution.identity()
        if other.contains(self):
            raise TypeCircularityError()
        return Substitution.of(self, other)

    def __str__(self) -> str:
        return f"'a{self.id}"


@dataclass(eq=False)
class IntType(Type):
    def is_equality_type(self) -> bool:
        return True

    def contains(self, tv: TypeVar) -> bool:
        return False

    def replace(self, tv: TypeVar, t: Type) -> Type:
        return self

    def unify(self, other: Type) -> "Substitution":
        if isinstance(other, IntType):
            return Substitution.identity()
        if isinstance(other, TypeVar):
            return other.unify(self)
        raise Exception("Type Error")


@dataclass(eq=False)
class BoolType(Type):
    def is_equality_type(self) -> bool:
        return True

    def contains(self, tv: TypeVar) -> bool:
        return False

    def replace(self, tv: TypeVar, t: Type) -> Type:
        return self

    def unify(self, other: Type) -> "Substitution":
        if isinstance(other, BoolType):
            return Substitution.identity()
        if isinstance(other, TypeVar):
            return other.unify(self)
        raise Exception("Type Error")


@dataclass(eq=False)
class UnitType(Type):
    def is_equality_type(self) -> bool:
        return True

    def contains(self, tv: TypeVar) -> bool:
        return False

    def replace(self, tv: TypeVar, t: Type) -> Type:
        return self

    def unify(self, other: Type) -> "Substitution":
        if isinstance(other, UnitType):
            return Substitution.identity()
        if isinstance(other, TypeVar):
            return other.unify(self)
        raise Exception("Type Error")


@dataclass(eq=False)
class ListType(Type):
    elem: Type

    def is_equality_type(self) -> bool:
        return self.elem.is_equality_type()

    def contains(self, tv: TypeVar) -> bool:
        return self.elem.contains(tv)

    def replace(self, tv: TypeVar, t: Type) -> Type:
        return ListType(self.elem.replace(tv, t))

    def unify(self, other: Type) -> "Substitution":
        if isinstance(other, ListType):
            return self.elem.unify(other.elem)
        if isinstance(other, TypeVar):
            return other.unify(self)
        raise Exception("Type Error")


@dataclass(eq=False)
class PairType(Type):
    fst: Type
    snd: Type

    def is_equality_type(self) -> bool:
        return self.fst.is_equality_type() and self.snd.is_equality_type()

    def contains(self, tv: TypeVar) -> bool:
        return self.fst.contains(tv) or self.snd.contains(tv)

    def replace(self, tv: TypeVar, t: Type) -> Type:
        return PairType(self.fst.replace(tv, t), self.snd.replace(tv, t))

    def unify(self, other: Type) -> "Substitution":
        if isinstance(other, PairType):
            s1 = self.fst.unify(other.fst)
            s2 = s1.apply(self.snd).unify(s1.apply(other.snd))
            return s2.compose(s1)
        if isinstance(other, TypeVar):
            return other.unify(self)
        raise Exception("Type Error")


@dataclass(eq=False)
class RefType(Type):
    inner: Type

    def is_equality_type(self) -> bool:

        return self.inner.is_equality_type()

    def contains(self, tv: TypeVar) -> bool:
        return self.inner.contains(tv)

    def replace(self, tv: TypeVar, t: Type) -> Type:
        return RefType(self.inner.replace(tv, t))

    def unify(self, other: Type) -> "Substitution":
        if isinstance(other, RefType):
            return self.inner.unify(other.inner)
        if isinstance(other, TypeVar):
            return other.unify(self)
        raise Exception("Type Error")


@dataclass(eq=False)
class ArrowType(Type):
    arg: Type
    ret: Type

    def is_equality_type(self) -> bool:
        # functions are not equality types in SimPL
        return False

    def contains(self, tv: TypeVar) -> bool:
        return self.arg.contains(tv) or self.ret.contains(tv)

    def replace(self, tv: TypeVar, t: Type) -> Type:
        return ArrowType(self.arg.replace(tv, t), self.ret.replace(tv, t))

    def unify(self, other: Type) -> "Substitution":
        if isinstance(other, ArrowType):
            s1 = self.arg.unify(other.arg)
            s2 = s1.apply(self.ret).unify(s1.apply(other.ret))
            return s2.compose(s1)
        if isinstance(other, TypeVar):
            return other.unify(self)
        raise Exception("Type Error")


INT = IntType()
BOOL = BoolType()
UNIT = UnitType()


# substitution

class Substitution:
    def __init__(self, mapping: Optional[Dict[TypeVar, Type]] = None):
        self.mapping: Dict[TypeVar, Type] = mapping or {}

    def apply(self, t: Type) -> Type:
        if isinstance(t, TypeVar):
            if t in self.mapping:
                return self.apply(self.mapping[t])
            return t

        result = t
        for a, ty in self.mapping.items():
            result = result.replace(a, ty)
        return result

    def compose(self, inner: "Substitution") -> "Substitution":

        new_map: Dict[TypeVar, Type] = {}

        for a, ty in inner.mapping.items():
            new_map[a] = self.apply(ty)

        for a, ty in self.mapping.items():
            if a not in new_map:
                new_map[a] = ty
        return Substitution(new_map)

    @staticmethod
    def identity() -> "Substitution":
        return Substitution({})

    @staticmethod
    def of(a: TypeVar, t: Type) -> "Substitution":
        return Substitution({a: t})

    def __repr__(self) -> str:
        return "{" + ", ".join(f"{str(a)} ↦ {t}" for a, t in self.mapping.items()) + "}"




class TypeEnv:
    def __init__(self, mapping: Optional[Dict[str, Type]] = None):
        self.mapping: Dict[str, Type] = mapping or {}

    def get(self, x: str) -> Optional[Type]:
        return self.mapping.get(x)

    def extend(self, x: str, t: Type) -> "TypeEnv":
        new_map = dict(self.mapping)
        new_map[x] = t
        return TypeEnv(new_map)

    def apply(self, s: Substitution) -> "TypeEnv":
        return TypeEnv({x: s.apply(t) for x, t in self.mapping.items()})

    def __repr__(self) -> str:
        return "; ".join(f"{x}:{t}" for x, t in self.mapping.items())


@dataclass
class TypeResult:
    subst: Substitution
    type: Type

    def then(self, other: "TypeResult") -> "TypeResult":
        # do in the right order
        s = other.subst.compose(self.subst)
        return TypeResult(s, s.apply(other.type))



class TypeVarGen:
    def __init__(self):
        self.counter = 0

    def fresh(self) -> TypeVar:
        tv = TypeVar(self.counter)
        self.counter += 1      
        return tv

def default_type_env() -> TypeEnv:

    tv_a = TypeVarGen().fresh()
    tv_b = TypeVarGen().fresh()

    return TypeEnv({
        # succ : int ->int
        "succ": ArrowType(INT, INT),

        # pred : int -> int
        "pred": ArrowType(INT, INT),

        # iszero : int -> bool
        "iszero": ArrowType(INT, BOOL),

        # fst : (a * b) -> a
        "fst": ArrowType(PairType(tv_a, tv_b), tv_a),

        # snd : (a *b) -> b
        "snd": ArrowType(PairType(tv_a, tv_b), tv_b),

        # hd : a list -> a
        "hd": ArrowType(ListType(tv_a), tv_a),

        # tl : a list -> (a list)
        "tl": ArrowType(ListType(tv_a), ListType(tv_a)),
    })