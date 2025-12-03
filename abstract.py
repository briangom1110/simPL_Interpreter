from dataclasses import dataclass
from typing import Any

class Expression:
    pass

# literals

@dataclass
class IntegerLiteral(Expression):
    value: int

@dataclass
class BooleanLiteral(Expression):
    value: bool

@dataclass
class NilLiteral(Expression):
    pass

@dataclass
class UnitLiteral(Expression):
    pass

#  Vars

@dataclass
class Var(Expression):
    name: str

# Operations

@dataclass
class UnaryOperation(Expression):
    op: str
    expr: Expression


@dataclass
class BinaryOperation(Expression):
    op: str
    left: Expression
    right: Expression

# application and fucntion
@dataclass
class Func(Expression):
    param: str
    body: Expression


@dataclass
class Apply(Expression):
    func: Expression
    arg: Expression


@dataclass
class Rec(Expression):
    name: str
    body: Expression

# pairs, refs, control
@dataclass
class Pair(Expression):
    left: Expression
    right: Expression


@dataclass
class Ref(Expression):
    expr: Expression

@dataclass
class Let(Expression):
    name: str
    value: Expression
    body: Expression


@dataclass
class If(Expression):
    condition: Expression
    then_branch: Expression
    else_branch: Expression


@dataclass
class While(Expression):
    condition: Expression
    body: Expression

# WHy is this acting weird
@dataclass
class Builtin(Expression):
    fn: callable