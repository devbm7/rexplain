from typing import List

class RegexToken:
    """Represents a single regex component"""
    pass

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
        pass
