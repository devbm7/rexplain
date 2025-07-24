from typing import List
from dataclasses import dataclass

@dataclass
class RegexToken:
    """Represents a single regex component"""
    type: str
    value: str

class RegexAST:
    """Abstract Syntax Tree for regex"""
    pass

class RegexParser:
    """Parse regex string into AST"""
    def parse(self, pattern: str) -> RegexAST:
        """Parse a regex pattern string into an AST"""
        pass

    def tokenize(self, pattern: str) -> List[RegexToken]:
        """Tokenize a regex pattern string into RegexToken objects"""
        tokens: List[RegexToken] = []
        i = 0
        special_chars = {'.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '^', '$'}
        while i < len(pattern):
            c = pattern[i]
            if c == '\\':
                # Handle escape sequence
                if i + 1 < len(pattern):
                    tokens.append(RegexToken(type='ESCAPE', value=pattern[i:i+2]))
                    i += 2
                else:
                    tokens.append(RegexToken(type='ESCAPE', value=c))
                    i += 1
            elif c in special_chars:
                tokens.append(RegexToken(type='SPECIAL', value=c))
                i += 1
            else:
                tokens.append(RegexToken(type='LITERAL', value=c))
                i += 1
        return tokens
