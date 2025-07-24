from typing import List, Optional
from dataclasses import dataclass
import re

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
    def parse(self, pattern: str, flags: int = 0) -> RegexAST:
        """Parse a regex pattern string into an AST. Optionally takes re flags (default: 0)."""
        pass

    def tokenize(self, pattern: str, flags: int = 0) -> List[RegexToken]:
        """Tokenize a regex pattern string into RegexToken objects, including character classes and groups. Optionally takes re flags (default: 0)."""
        tokens: List[RegexToken] = []
        i = 0
        special_chars = {'.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '^', '$'}
        escape_sequences = {'d', 'w', 's', 'D', 'W', 'S', 'b', 'B', 'A', 'Z', 'G', 'n', 'r', 't', 'v', 'f', '\\'}
        length = len(pattern)
        while i < length:
            c = pattern[i]
            # Character class
            if c == '[':
                start = i
                i += 1
                in_escape = False
                while i < length:
                    if not in_escape and pattern[i] == ']':
                        i += 1
                        break
                    if pattern[i] == '\\' and not in_escape:
                        in_escape = True
                        i += 1
                    else:
                        in_escape = False
                        i += 1
                tokens.append(RegexToken(type='CHAR_CLASS', value=pattern[start:i]))
            # Group constructs
            elif c == '(':
                if pattern[i:i+3] == '(?:':
                    tokens.append(RegexToken(type='GROUP_NONCAP', value='(?:'))
                    i += 3
                elif pattern[i:i+4] == '(?P<':
                    # Named group: (?P<name>
                    start = i
                    j = i+4
                    while j < length and pattern[j] != '>':
                        j += 1
                    if j < length and pattern[j] == '>':
                        group_str = pattern[start:j+1]
                        tokens.append(RegexToken(type='GROUP_NAMED', value=group_str))
                        i = j+1  # Advance index to after the closing '>'
                    else:
                        tokens.append(RegexToken(type='GROUP_OPEN', value='('))
                        i += 1
                elif pattern[i:i+3] == '(?=':
                    tokens.append(RegexToken(type='GROUP_LOOKAHEAD', value='(?='))
                    i += 3
                elif pattern[i:i+4] == '(?!':
                    tokens.append(RegexToken(type='GROUP_NEG_LOOKAHEAD', value='(?!'))
                    i += 4
                elif pattern[i:i+4] == '(?<=':
                    tokens.append(RegexToken(type='GROUP_LOOKBEHIND', value='(?<='))
                    i += 4
                elif pattern[i:i+5] == '(?<!':
                    tokens.append(RegexToken(type='GROUP_NEG_LOOKBEHIND', value='(?<!'))
                    i += 5
                else:
                    tokens.append(RegexToken(type='GROUP_OPEN', value='('))
                    i += 1
            elif c == ')':
                tokens.append(RegexToken(type='GROUP_CLOSE', value=')'))
                i += 1
            # Quantifier braces
            elif c == '{':
                start = i
                i += 1
                while i < length and pattern[i] != '}':
                    i += 1
                if i < length and pattern[i] == '}':
                    i += 1
                tokens.append(RegexToken(type='QUANTIFIER', value=pattern[start:i]))
            # Escape sequences
            elif c == '\\':
                if i + 1 < length:
                    next_c = pattern[i+1]
                    tokens.append(RegexToken(type='ESCAPE', value=pattern[i:i+2]))
                    i += 2
                else:
                    tokens.append(RegexToken(type='ESCAPE', value=c))
                    i += 1
            # Specials
            elif c in special_chars:
                tokens.append(RegexToken(type='SPECIAL', value=c))
                i += 1
            # Literals
            else:
                tokens.append(RegexToken(type='LITERAL', value=c))
                i += 1
        return tokens
