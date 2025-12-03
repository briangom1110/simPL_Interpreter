from dataclasses import dataclass

@dataclass
class Token:
    type: str
    value: any = None

class Lexer:
    def __init__(self, text):
        self.text = text
        self.pos = 0
        self.length = len(text)

        # keywords in SimPL lang
        self.KEYWORDS = {
            "let": "LET", "in": "IN", "end": "END", "fn": "FN","rec": "REC", "if": "IF", "then": "THEN",
            "else": "ELSE", "while": "WHILE", "do": "DO", "true": "TRUE", "false": "FALSE", "nil": "NIL", "not": "NOT",
            "andalso": "ANDALSO","orelse": "ORELSE", "ref": "REF",
        }

    def peek(self, n=0):
        if self.pos + n < self.length:
            return self.text[self.pos + n]
        return None

    def advance(self, n=1):
        self.pos += n

    def skip_whitespace(self):
        while self.peek() is not None and self.peek().isspace():
            self.advance()

    # Work on comment
    def skip_comment(self):

        self.advance(2)
        depth = 1

        # Checks for nested comments
        while depth > 0:
            c = self.peek()
            if c is None:
                raise Exception("Syntax Error")

            if c == "(" and self.peek(1) == "*":
                depth += 1
                self.advance(2)
            elif c == "*" and self.peek(1) == ")":
                depth -= 1
                self.advance(2)
            else:
                self.advance()

    # 2.2 Atoms

    def integer(self):
        start = self.pos
        while self.peek() is not None and self.peek().isdigit():
            self.advance()
        value = int(self.text[start:self.pos])
        return Token("INT", value)

    def identifier(self):
        start = self.pos
        while self.peek() and (self.peek().isalnum() or self.peek() in "_’"):
            self.advance()
        name = self.text[start:self.pos]
        if name in self.KEYWORDS:
            return Token(self.KEYWORDS[name])
        return Token("ID", name)



    def next_token(self):
        self.skip_whitespace()

        c = self.peek()
        if c is None:
            return Token("EOF")

        # comments
        if c == "(" and self.peek(1) == "*":
            self.skip_comment()
            return self.next_token()

        # integer
        if c.isdigit():
            return self.integer()

        # identifier
        if c.isalpha() or c == "_":
            return self.identifier()

        # :: 
        if c == ":" and self.peek(1) == ":":
            self.advance(2)
            return Token("CONS")

        # := 
        if c == ":" and self.peek(1) == "=":
            self.advance(2)
            return Token("ASSIGN")

        # <=
        if c == "<" and self.peek(1) == "=":
            self.advance(2)
            return Token("LTEQ")

        # <>
        if c == "<" and self.peek(1) == ">":
            self.advance(2)
            return Token("NEQ")

        # >=
        if c == ">" and self.peek(1) == "=":
            self.advance(2)
            return Token("GTEQ")

        # =>
        if c == "=" and self.peek(1) == ">":
            self.advance(2)
            return Token("ARROW")

        single_char = {
            "+": "PLUS", "-": "MINUS", "*": "TIMES", "/": "DIV", "%": "MOD", "~": "NEG",
            "=": "EQ", "<": "LT", ">": "GT", "!": "BANG", "(": "LPAREN", ")": "RPAREN",
            ",": "COMMA", ";": "SEMI"
        }

        if c in single_char:
            tok_type = single_char[c]
            self.advance()
            return Token(tok_type)

        # Unknown char
        raise Exception("Syntax Error")