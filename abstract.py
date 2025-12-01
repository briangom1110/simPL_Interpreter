from dataclasses import dataclass
from typing import List, Optional

class Expression: 
    pass

class IntegerLiteral(Expression):
    value : int

class Variable(Expression): 
    name : str

class BooleanLiteral(Expression): 
    value : bool

class Ref(Expression): 
    expr : Expression

class Func(Expression): 
    param : str
    body : Expression

class Recursive(Expression): 
    name : str
    body : Expression

class emptyList (Expression): 
    pass

class Pair(Expression):
    left : Expression
    right : Expression

class UnaryOperation(Expression):
    op : str
    expr : Expression

class BinaryOperation(Expression): 
    op : str
    left : Expression
    right : Expression

class Let(Expression): 
    name : str
    value : Expression
    body : Expression

class If (Expression): 

    condition : Expression
    then : Expression
    body : Expression

class While (Expression): 
    condition: Expression
    body : Expression

class Grouping (Expression): 
    expr : Expression

class UnitLiteral(Expression): 
    pass

