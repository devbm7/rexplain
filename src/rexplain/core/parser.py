from typing import List, Optional, Union
from dataclasses import dataclass, field
import re

@dataclass
class RegexAST:
    """Base class for all AST nodes."""
    pass

@dataclass
class Sequence(RegexAST):
    """A sequence of regex elements (e.g., abcd)."""
    elements: List[RegexAST]

@dataclass
class Literal(RegexAST):
    """A literal character."""
    value: str

@dataclass
class CharClass(RegexAST):
    """A character class, e.g., [a-z] or [^abc]."""
    value: str  # The raw class string, e.g., '[a-z]'

@dataclass
class Group(RegexAST):
    """A group (capturing, non-capturing, named, lookahead, etc.)."""
    group_type: str  # 'capturing', 'noncap', 'named', 'lookahead', etc.
    children: List[RegexAST]
    name: Optional[str] = None  # For named groups

@dataclass
class Quantifier(RegexAST):
    """A quantifier applied to a subpattern, e.g., a*, b{2,3}."""
    child: RegexAST
    quant: str  # '*', '+', '?', '{n}', '{n,m}', etc.

@dataclass
class Anchor(RegexAST):
    """Anchors like ^, $, \b, etc."""
    value: str

@dataclass
class Escape(RegexAST):
    """Escape sequences like \d, \w, etc."""
    value: str

@dataclass
class Alternation(RegexAST):
    """Alternation, e.g., a|b|c."""
    options: List[RegexAST]

class RegexParser:
    """Parse regex string into AST"""
    def parse(self, pattern: str, flags: int = 0) -> RegexAST:
        """Parse a regex pattern string into an AST. Optionally takes re flags (default: 0)."""
        tokens = self.tokenize(pattern, flags)
        self._tokens = tokens
        self._pos = 0
        ast = self._parse_alternation()
        return ast

    def _peek(self):
        if self._pos < len(self._tokens):
            return self._tokens[self._pos]
        return None

    def _advance(self):
        tok = self._peek()
        if tok:
            self._pos += 1
        return tok

    def _parse_alternation(self):
        options = [self._parse_sequence()]
        while self._peek() and self._peek().type == 'SPECIAL' and self._peek().value == '|':
            self._advance()  # skip '|'
            options.append(self._parse_sequence())
        if len(options) == 1:
            return options[0]
        return Alternation(options)

    def _parse_sequence(self):
        elements = []
        while True:
            tok = self._peek()
            if tok is None or (tok.type == 'SPECIAL' and tok.value in '|)'):
                break
            elements.append(self._parse_quantifier())
        if len(elements) == 1:
            return elements[0]
        return Sequence(elements)

    def _parse_quantifier(self):
        atom = self._parse_atom()
        tok = self._peek()
        if tok and tok.type == 'QUANTIFIER':
            quant_tok = self._advance()
            return Quantifier(atom, quant_tok.value)
        return atom

    def _parse_atom(self):
        tok = self._peek()
        if tok is None:
            return None
        # Escaped metacharacters as literals
        if tok.type == 'ESCAPE':
            # If it's an escaped metacharacter, treat as Literal
            metachars = {'.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '^', '$', '\\'}
            if len(tok.value) == 2 and tok.value[1] in metachars:
                self._advance()
                return Literal(tok.value[1])
            else:
                self._advance()
                return Escape(tok.value)
        elif tok.type == 'LITERAL':
            self._advance()
            return Literal(tok.value)
        elif tok.type == 'CHAR_CLASS':
            self._advance()
            return CharClass(tok.value)
        elif tok.type == 'SPECIAL' and tok.value in {'^', '$'}:
            self._advance()
            return Anchor(tok.value)
        elif tok.type.startswith('GROUP_'):
            return self._parse_group()
        else:
            self._advance()
            return Literal(tok.value)

    def _parse_group(self):
        tok = self._advance()
        group_type = tok.type
        name = None
        if group_type == 'GROUP_NAMED':
            # Extract group name from value, e.g., (?P<name>
            import re
            m = re.match(r'\(\?P<([^>]+)>', tok.value)
            if m:
                name = m.group(2)
        children = []
        # Parse group contents until closing paren
        if self._peek() and self._peek().type == 'GROUP_CLOSE':
            # Empty group: () or (?:)
            self._advance()  # consume ')'
            return Group(group_type, children, name)
        while self._peek() and not (self._peek().type == 'GROUP_CLOSE'):
            children.append(self._parse_alternation())
        if self._peek() and self._peek().type == 'GROUP_CLOSE':
            self._advance()  # consume ')'
        else:
            # Unclosed group
            raise ValueError('Unclosed group: missing )')
        return Group(group_type, children, name)

    def tokenize(self, pattern: str, flags: int = 0) -> List['RegexToken']:
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
                if i > length:
                    raise ValueError('Unclosed character class: missing ]')
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

@dataclass
class RegexToken:
    """Represents a single regex component"""
    type: str
    value: str
