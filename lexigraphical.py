from dataclasses import dataclass

@dataclass
class Token: 
    tyep: str
    value: any

KEYWORDS = { 'nil', 'ref'
            , 'fn', 'rec'
            , 'let', 'in', 'end'
            , 'if', 'then', 'else'
            , 'while', 'do'
            , 'true', 'false'
            , 'not', 'andalso', 'orelse'}

OPPERATORS = { '+', '-', '*', '/', '%', '~', '=', 
                '<', '>', '!', '(', ')', ',', ';'}

class lex: 
    def __init__ (self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

    # View input 
    def peek(self, offset = 0):
        if self.pos + offset < self.length:
            return self.text[self.pos + offset]
        return None

    # Skip certain token
    def go_next(self, n = 1): 
        self.pos += n
    
    # If the current token is whitespace, ignore (go_next)
    def whitespace(self): 
        while self.peek() is not None and self.peek().isspace():
            self.go_next()

    # If the current token is a comment, ignore (go_next)
    def comment(self): 
        self.go_next(2)
        nest_count = 1

        while nest_count > 0: 
            curr = self.peek()

            # Nested comment detection
            if curr == '(' and self.peek(1) == '*':
                nest += 1
                self.go_next(2)

            elif curr == '*' and self.peek(1) == ')':
                nest -= 1
                self.advance(2)
            
            # If the comment isn't closed, raise an exception
            elif curr is None: 
                raise Exception("Syntax Error")

            else:
                self.advance()

    # 2.2 Atoms, integer literals 
    def integer(self): 
        first_digit = self.pos
        leading_zeroes = 0
        lead = True
        while self.peek() is not None and self.peek().isdigit():
            if int(self.peek()) is 0 and lead:
                leading_zeroes += 1

            else:
                lead = False

            self.go_next()

        value = int(self.text[start:self.pos])
        return Token('INT', value)

    def identifiers(self): 
        first_char = self.pos
        curr = self.peek()

        if curr.isdigit():
            raise Exception("Syntax Error")
        
        while self.peek() and (self.peek().isalnum() or self.peek() in '_'):
            self.go_next()

        id_name = self.text[first_char:self.pos()]
        return Token('ID', id_name)

    def next(self_tok):
        self.whitespace()

        curr = self.peek()

        if curr is None: 
            return Token('EOF')

        if curr == '(' and self.peek(1) == '*': 
            self.comment()
            return self.next()

        if curr.isdigit(): 
            return self.integer()

        if curr.isalpha() or c == '_':  # isalpha() checks if it is an alphabetic char
            return self.identifiers()

        if curr == '<' and self.peek(1) == '=': 
            self.go_next(2)
            return Token('LTEQ')

        if curr == '<' and self.peek(1) == '>':
            self.go_next(2)
            return Token('NEQ')

        if curr == '=' and self.peek(1) == '>':
            self.go_next(2)
            return Token('ARROW')

        if curr == ':' and self.peek(1) == ':':
            self.go_next(2)
            return Token('CONS')

        if curr == ':' and self.peek(1) == '=':
            self.go_next(2)
            return Token('ASSIGNMENT')

        if curr in OPPERATORS:
            self.go_next()
            return Token(OPPERATORS[curr])

            