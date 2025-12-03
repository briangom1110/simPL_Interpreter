from __future__ import annotations
from dataclasses import dataclass, field
from typing import Dict
from values import Value

@dataclass
class Env:
    mapping: Dict[str, Value]
    parent: "Env | None" = None

    def lookup(self, name: str) -> Value:
        if name in self.mapping:
            return self.mapping[name]
        if self.parent is not None:
            return self.parent.lookup(name)
        raise RuntimeError(f"unbound variable {name}")

    def extend(self, name: str, val: Value) -> "Env":
        return Env({name: val}, parent=self)

@dataclass
class Mem:
    cells: Dict[int, Value] = field(default_factory=dict)

    def read(self, addr: int) -> Value:
        if addr not in self.cells:
            raise RuntimeError(f"invalid address {addr}")
        return self.cells[addr]

    def write(self, addr: int, val: Value) -> None:
        self.cells[addr] = val

@dataclass
class State:
    env: Env
    mem: Mem
    next_addr: int = 0

    def alloc(self, val: Value) -> int:
        addr = self.next_addr
        self.mem.write(addr, val)
        self.next_addr += 1
        return addr