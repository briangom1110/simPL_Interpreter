import abstract
from lexigraphical import Lexer, Token

class Parser:
    def __init__(self, lexer: Lexer):
        self.lexer = lexer
        self.tok: Token = self.lexer.next_token()

    def error(self, msg="syntax error"):
        raise Exception(msg)

    def eat(self, expected_type: str):
        if self.tok.type == expected_type:
            self.tok = self.lexer.next_token()
        else:
            raise Exception("Syntax Error")

    def starts_atom(self, ttype: str) -> bool:
        return ttype in (
            "INT", "TRUE", "FALSE", "NIL", "ID", "LPAREN", "FN", "REC", "REF", "NEG", "NOT", "BANG", )


    #  Work on parse function and any additional 
    def parse(self):
        expr = self.parse_seq()
        if self.tok.type != "EOF":
            raise Exception("Syntax Error")
        return expr

    # Operator precedence needs to be maintained as in pdf 

    # sequence e1 ; e2
    def parse_seq(self):
        expr = self.parse_assign()
        while self.tok.type == "SEMI":

            self.eat("SEMI")
            right = self.parse_assign()
            expr = abstract.BinaryOperation(";", expr, right)

        return expr

    # assign e1 := e2
    def parse_assign(self):
        expr = self.parse_orelse()
        if self.tok.type == "ASSIGN":
            self.eat("ASSIGN")
            rhs = self.parse_orelse()
            return abstract.BinaryOperation(":=", expr, rhs)

        return expr

    # orelse, e1 orelse e2
    def parse_orelse(self):
        expr = self.parse_andalso()
        while self.tok.type == "ORELSE":
            self.eat("ORELSE")
            rhs = self.parse_andalso()
            expr = abstract.BinaryOperation("orelse", expr, rhs)

        return expr

    # e1 andalso e2
    def parse_andalso(self):
        expr = self.parse_compare()
        while self.tok.type == "ANDALSO":

            self.eat("ANDALSO")
            rhs = self.parse_compare()
            expr = abstract.BinaryOperation("andalso", expr, rhs)
        return expr

    # comparisons
    def parse_compare(self):
        expr = self.parse_cons()
        while self.tok.type in ("EQ", "NEQ", "LT", "LTEQ", "GT", "GTEQ"):
            op_map = {
                "EQ": "=", "NEQ": "<>", "LT": "<", "LTEQ": "<=", "GT": ">", "GTEQ": ">=", }

            op = op_map[self.tok.type]
            self.eat(self.tok.type)
            rhs = self.parse_cons()
            expr = abstract.BinaryOperation(op, expr, rhs)
        return expr

    # construct  e1 :: e2
    def parse_cons(self):
        expr = self.parse_add()
        if self.tok.type == "CONS":
            self.eat("CONS")
            rhs = self.parse_cons()
            expr = abstract.BinaryOperation("::", expr, rhs)
        return expr

    # Math implementation, add, sub, div, mult, mod

    def parse_add(self):

        expr = self.parse_multiply()
        while self.tok.type in ("PLUS", "MINUS"):
            op = "+" if self.tok.type == "PLUS" else "-"
            self.eat(self.tok.type)
            rhs = self.parse_multiply()
            expr = abstract.BinaryOperation(op, expr, rhs)
        return expr


    def parse_multiply(self):
        expr = self.parse_app()
        while self.tok.type in ("TIMES", "DIV", "MOD"):
            op_map = {"TIMES": "*", "DIV": "/", "MOD": "%"}
            op = op_map[self.tok.type]
            self.eat(self.tok.type)
            rhs = self.parse_app()
            expr = abstract.BinaryOperation(op, expr, rhs)
        return expr

    # application: e1 e2
    def parse_app(self):
        expr = self.parse_unary()
        while self.starts_atom(self.tok.type):
            rhs = self.parse_unary()
            expr = abstract.Apply(expr, rhs)
        return expr

    # unary operations
    def parse_unary(self):
        t = self.tok.type

        if t in ("NEG", "NOT", "BANG"):
            op_map = {"NEG": "~", "NOT": "not", "BANG": "!"}
            op = op_map[t]
            self.eat(t)
            return abstract.UnaryOperation(op, self.parse_unary())

        if t == "REF":
            self.eat("REF")
            expr = self.parse_unary()
            return abstract.Ref(expr)

        return self.parse_atom()

    # atoms
    def parse_atom(self):
        t = self.tok.type

        # literals
        if t == "INT":
            v = self.tok.value
            self.eat("INT")
            return abstract.IntegerLiteral(v)

        if t == "TRUE":
            self.eat("TRUE")
            return abstract.BooleanLiteral(True)

        if t == "FALSE":
            self.eat("FALSE")
            return abstract.BooleanLiteral(False)

        if t == "NIL":
            self.eat("NIL")
            return abstract.NilLiteral()

        # variables
        if t == "ID":
            name = self.tok.value
            self.eat("ID")
            return abstract.Var(name)

        # parentheses
        if t == "LPAREN":
            self.eat("LPAREN")

            # unit ()
            if self.tok.type == "RPAREN":
                self.eat("RPAREN")
                return abstract.UnitLiteral()

            # parse one expression
            expr = self.parse_seq()

            # possibly pair (e1, e2)
            if self.tok.type == "COMMA":
                self.eat("COMMA")
                rhs = self.parse_seq()
                self.eat("RPAREN")
                return abstract.Pair(expr, rhs)

            self.eat("RPAREN")
            return expr

        # fn x => e
        if t == "FN":
            self.eat("FN")
            if self.tok.type != "ID":

                # Syntax error found if this runs 
                raise Exception("Syntax Error")
            param = self.tok.value
            self.eat("ID")
            self.eat("ARROW")
            body = self.parse_seq()
            return abstract.Func(param, body)

        # rec x => e
        if t == "REC":
            self.eat("REC")
            if self.tok.type != "ID":
                raise Exception("Syntax Error")
            name = self.tok.value
            self.eat("ID")
            self.eat("ARROW")
            body = self.parse_seq()
            return abstract.Rec(name, body)

        # let x = e1 in e2 end
        if t == "LET":

            self.eat("LET")
            if self.tok.type != "ID":
                raise Exception("Syntax Error")
            name = self.tok.value
            self.eat("ID")
            self.eat("EQ")
            val = self.parse_seq()
            self.eat("IN")
            body = self.parse_seq()
            self.eat("END")
            return abstract.Let(name, val, body)

        # if e1 then e2 else e3
        if t == "IF":
            self.eat("IF")
            cond = self.parse_seq()
            self.eat("THEN")
            then = self.parse_seq()
            self.eat("ELSE")
            els = self.parse_seq()
            return abstract.If(cond, then, els)

        # while e1 do e2
        if t == "WHILE":
            self.eat("WHILE")
            # condition can be any expression
            cond = self.parse_seq()
            self.eat("DO")
            body = self.parse_assign()
            return abstract.While(cond, body)

