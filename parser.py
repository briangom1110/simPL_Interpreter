class Parser: 

    def __init__ (self, lexigraphical):
        self.lexegraphical = lexigraphical
        self.tok = lexigraphical.next()

    def eat(self, type): 
        if self.tok.type == type: 
            self.tok = self.lexegraphical.next()

        else: 
            raise Exception('Syntax Error')

    def parse_seq(self): 
        expr = self.parse_assign()
        while self.tok.type == 'SEMI': 
            self.eat('SEMI')
            right = self.parse_assign()
            expr = BinaryOperation(';', expr, right)
        return expr

    def parse_assign(self): 
        expr = self.parse_orelse()
        if self.tok.type == 'ASSIGN': 
            self.eat('ASSIGN')
            rhs = self.parse_orelse()
            return BinaryOperation(':=', expr, rhs)
        return expr

    def parse_orelse(self):
        expr = self.parse_andalso()
        while self.tok.type == 'ORELSE':
            op = 'orelse'
            self.eat('orelse')
            rhs = self.parse_andalso()
            expr = BinaryOperation(op, expr, rhs)
        return expr

    def parse_andalso(self):
        expr = self.compare()
        while self.tok.type == 'ANDALSO': 
            op = 'andalso'
            self.eat('ANDALSO')
            rhs = self.compare()
            expr = BinaryOperation(op, expr, rhs)

        return expr
    
    def compare (self): 
        expr = self.parse_cons()
        while self.tok.type in ('EQ', 'NEQ', 'LT', 'LTEQ', 'GTEQ', 'GT'):
            op = self.tok.type.lower()
            self.eat(self.tok.type)
            rhs = self.parse_cons()

            expr = BinaryOperation(op, expr, rhs)
        return expr

    def parse_cons(self):
        expr = self.parse_add()
        while self.tok.type == 'CONS':
            self.eat('CONS')
            rhs = self.parse_add()
            expr = BinaryOperation('::', expr, rhs)
        
        return expr

    # do parse_add next 
    def parse_add(self): 
        expr = self.parse_multiply()
        while self.tok.type in ('PLUS', 'MINUS'):
            op = '+' if self.tok.type == 'PLUS' else '-'
            self.eat(self.tok.type)
            rhs = self.parse_null()

            expr = BinaryOperation(op, expr, rhs)
        
        return expr

    def parse_multiply(self):
        expr = self.parse_app()
        while self.tok.type in ('TIMES', 'DIV', 'MOD'):
            op = {'TIMES': '*', 'DIV': '/', 'MOD' : '%'}[self.tok.type]
            
            self.eat(self.tok.type)
            rhs = self.parse_app()
            expr = BinaryOperation(op, expr, rhs)
        
        return expr 

    def parse_app(self): 
        expr = self.parse_unary()
        while self.starts_atom(self.tok.type):
            rhs = self.parse_unary()
            expr = apply(expr, rhs)

        return expr 

    def parse_unary(self): 
        if self.tok.type in ('NEG', 'NOT', 'BANG'):
            op = {'NEG' : '~', 'NOT': 'not', 'BANG' : '!'}[self.tok.type]
            self.eat(self.tok.type)
            return UnaryOperation(op, self.parse_unary())

        return self.parse_atom()

    def parse_atom(self): 
        atom = self.tok.type

        if atom == 'INT': 
            val = self.tok.value
            self.eat('INT')
            return IntegerLiteral(val)

        if atom == 'TRUE':
            self.eat('TRUE')
            return BooleanLiteral(True)

        if atom == 'FALSE':
            self.eat('FALSE')
            return BooleanLiteral(False)

        if atom == 'ID': 
            name = self.tok.value
            self.eat('ID')
            return Var(name)

        if atom == 'LPAREN':
            self.eat('LPAREN')

            expr = self.parse_seq()
            if self.tok.type == 'COMMA':
                self.eat('COMMA')
                rhs = self.parse_seq()
                self.eat('RPAREN')
                return Pair(expr, rhs)
            self.eat('RPAREN')
            return expr

        if atom == 'FN':
            self.eat('FN')
            param = self.tok.value
            self.eat('ID')
            self.eat('ARROW')
            body = self.parse_seq()
            return Func(param, body)

        if atom == 'REC':
            self.eat('REC')
            name = self.tok.value
            self.eat('ID')
            self.eat('ARROW')
            body = self.parse_seq()
            return Rec(name, body)

        if t == "LET":
            self.eat("LET")
            name = self.tok.value
            self.eat("ID")
            self.eat("EQ")
            val = self.parse_sequence()
            self.eat("IN")
            body = self.parse_sequence()
            self.eat("END")
            return Let(name, val, body)

        if t == "IF":
            self.eat("IF")
            cond = self.parse_sequence()
            self.eat("THEN")
            then_e = self.parse_sequence()
            self.eat("ELSE")
            else_e = self.parse_sequence()
            return If(cond, then_e, else_e)

        if t == "WHILE":
            self.eat("WHILE")
            cond = self.parse_sequence()
            self.eat("DO")
            body = self.parse_sequence()
            return While(cond, body)