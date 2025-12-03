from dataclasses import dataclass

class Value:
    pass


@dataclass
class IntVal(Value):
    value: int


@dataclass
class BoolVal(Value):
    value: bool


@dataclass
class UnitVal(Value):
    pass


@dataclass
class NilVal(Value):
    pass


@dataclass
class ConsVal(Value):
    head: Value
    tail: Value   # NilVal or ConsVal


@dataclass
class PairVal(Value):
    fst: Value
    snd: Value


@dataclass
class RefVal(Value):
    addr: int


@dataclass
class FunVal(Value):
    env: "state.Env"
    param: str
    body: "abstract.Expression"


@dataclass
class RecVal(Value):
    env: "state.Env"
    name: str
    body: "abstract.Expression"
