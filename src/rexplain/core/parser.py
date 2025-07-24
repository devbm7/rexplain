from typing import List, Optional, Union
from dataclasses import dataclass, field
import re

@dataclass
class RegexAST:
    """
    Base class for all AST nodes representing regex components.
    """
    pass

@dataclass
class Sequence(RegexAST):
    """
    Represents a sequence of regex elements (e.g., abcd).
    """
    elements: List[RegexAST]

@dataclass
class Literal(RegexAST):
    """
    Represents a literal character in the regex.
    """
    value: str

@dataclass
class CharClass(RegexAST):
    """
    Represents a character class, e.g., [a-z] or [^abc].
    """
    value: str  # The raw class string, e.g., '[a-z]'

@dataclass
class Group(RegexAST):
    """
    Represents a group (capturing, non-capturing, named, lookahead, etc.).
    """
    group_type: str  # 'capturing', 'noncap', 'named', 'lookahead', etc.
    children: List[RegexAST]
    name: Optional[str] = None  # For named groups
    flags: Optional[str] = None  # For inline/scoped flags
    condition: Optional[str] = None  # For conditional expressions

@dataclass
class Quantifier(RegexAST):
    """
    Represents a quantifier applied to a subpattern, e.g., a*, b{2,3}.
    """
    child: RegexAST
    quant: str  # '*', '+', '?', '{n}', '{n,m}', etc.

@dataclass
class Anchor(RegexAST):
    r"""
    Represents anchors like ^, $, \b, etc.
    """
    value: str

@dataclass
class Escape(RegexAST):
    r"""
    Represents escape sequences like \d, \w, etc.
    """
    value: str

@dataclass
class Alternation(RegexAST):
    """
    Represents alternation, e.g., a|b|c.
    """
    options: List[RegexAST]

class RegexParser:
    """
    Parses a regex string into an abstract syntax tree (AST).
    """
    def parse(self, pattern: str, flags: int = 0) -> RegexAST:
        r"""
        Parse a regex pattern string into an AST.

        Args:
            pattern (str): The regex pattern to parse.
            flags (int, optional): Regex flags (e.g., re.IGNORECASE). Defaults to 0.

        Returns:
            RegexAST: The root node of the parsed regex AST.
        """
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
            if tok is None or (tok.type == 'SPECIAL' and tok.value == '|') or (tok.type == 'GROUP_CLOSE'):
                break
            elements.append(self._parse_quantifier())
        if len(elements) == 1:
            return elements[0]
        return Sequence(elements)

    def _parse_quantifier(self):
        # Always allow quantifiers to apply to any atom, including Anchor
        atom = self._parse_atom()
        tok = self._peek()
        if tok and tok.type == 'QUANTIFIER':
            quant_tok = self._advance()
            # Check for non-greedy quantifier (e.g., *?, +?, ??, {n,m}?)
            next_tok = self._peek()
            if next_tok and next_tok.type == 'SPECIAL' and next_tok.value == '?':
                self._advance()
                quant_str = quant_tok.value + '?'
            else:
                quant_str = quant_tok.value
            return Quantifier(atom, quant_str)
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
        flags = None
        condition = None
        # Inline flags: (?i), (?m), (?s), or scoped flags (?i:...)
        if group_type == 'GROUP_FLAGS':
            # Distinguish between inline and scoped flags
            import re
            m = re.match(r'\(\?[a-zA-Z]+([):])', tok.value)
            if m and m.group(1) == ')':
                # Inline flags group, e.g., (?i)
                flags = tok.value[2:-1]  # extract flags between (? and )
                return Group('GROUP_FLAGS', [], None, flags=flags)
            elif m and m.group(1) == ':':
                # Scoped flags group, e.g., (?m:...)
                flags = tok.value[2:-1]  # extract flags between (? and :
                group_type = 'GROUP_FLAGS'
                # Parse group contents until closing paren
                children = []
                if self._peek() and self._peek().type == 'GROUP_CLOSE':
                    self._advance()  # empty group
                    return Group(group_type, children, name, flags, condition)
                children.append(self._parse_alternation())
                if self._peek() and self._peek().type == 'GROUP_CLOSE':
                    self._advance()
                else:
                    raise ValueError('Unclosed group: missing )')
                return Group(group_type, children, name, flags, condition)
        if group_type == 'GROUP_NAMED':
            # Extract group name from value, e.g., (?P<name>
            import re
            m = re.match(r'\(\?P<([^>]+)>', tok.value)
            if m:
                name = m.group(1)  # FIX: should be group(1), not group(2)
        # For lookahead/lookbehind/noncap/flags/conditional and other group types, parse contents then expect GROUP_CLOSE
        children = []
        if group_type in {'GROUP_LOOKAHEAD', 'GROUP_NEG_LOOKAHEAD', 'GROUP_LOOKBEHIND', 'GROUP_NEG_LOOKBEHIND', 'GROUP_NONCAP', 'GROUP_FLAGS', 'GROUP_CONDITIONAL', 'GROUP_NAMED'}:
            # Parse group contents until closing paren
            if self._peek() and self._peek().type == 'GROUP_CLOSE':
                self._advance()  # empty group
                return Group(group_type, children, name, flags, condition)
            children.append(self._parse_alternation())
            if self._peek() and self._peek().type == 'GROUP_CLOSE':
                self._advance()
            else:
                raise ValueError('Unclosed group: missing )')
            return Group(group_type, children, name, flags, condition)
        # For capturing groups, parse alternation (may be nested)
        if self._peek() and self._peek().type == 'GROUP_CLOSE':
            self._advance()  # consume ')'
            return Group(group_type, children, name, flags, condition)
        while self._peek() and not (self._peek().type == 'GROUP_CLOSE'):
            children.append(self._parse_alternation())
        if self._peek() and self._peek().type == 'GROUP_CLOSE':
            self._advance()  # consume ')'
        else:
            raise ValueError('Unclosed group: missing )')
        return Group(group_type, children, name, flags, condition)

    def tokenize(self, pattern: str, flags: int = 0) -> List['RegexToken']:
        r"""
        Tokenize a regex pattern string into RegexToken objects, including character classes and groups.

        Args:
            pattern (str): The regex pattern to tokenize.
            flags (int, optional): Regex flags (e.g., re.IGNORECASE). Defaults to 0.

        Returns:
            List[RegexToken]: List of tokens representing the regex pattern.
        """
        tokens: List[RegexToken] = []
        i = 0
        special_chars = {'.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '^', '$'}
        escape_sequences = {'d', 'w', 's', 'D', 'W', 'S', 'b', 'B', 'A', 'Z', 'G', 'n', 'r', 't', 'v', 'f', '\\', 'u', 'x', 'N'}
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
                if i > length or (i == length and (length == 0 or pattern[i-1] != ']')):
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
                # Inline flags or conditional expressions
                elif pattern[i:i+2] == '(?':
                    # Could be inline flags, scoped flags, or conditional
                    j = i+2
                    flag_str = ''
                    while j < length and pattern[j] in 'imsxauL':
                        flag_str += pattern[j]
                        j += 1
                    if j < length and pattern[j] == ':':
                        tokens.append(RegexToken(type='GROUP_FLAGS', value=pattern[i:j+1]))
                        i = j+1
                    elif j < length and pattern[j] == ')':
                        tokens.append(RegexToken(type='GROUP_FLAGS', value=pattern[i:j+1]))
                        i = j+1
                    else:
                        tokens.append(RegexToken(type='GROUP_OPEN', value='('))
                        i += 1
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
                else:
                    raise ValueError('Unclosed quantifier braces: missing }')
                tokens.append(RegexToken(type='QUANTIFIER', value=pattern[start:i]))
            # Quantifiers *, +, ?
            elif c in {'*', '+', '?'}:
                tokens.append(RegexToken(type='QUANTIFIER', value=c))
                i += 1
            # Escape sequences (including Unicode/ASCII/Named)
            elif c == '\\':
                if i + 1 < length:
                    next_c = pattern[i+1]
                    if next_c in escape_sequences:
                        # Unicode: \uXXXX, ASCII: \xXX, Named: \N{...}
                        if next_c == 'u' and i+5 < length:
                            tokens.append(RegexToken(type='ESCAPE', value=pattern[i:i+6]))
                            i += 6
                        elif next_c == 'x' and i+3 < length:
                            tokens.append(RegexToken(type='ESCAPE', value=pattern[i:i+4]))
                            i += 4
                        elif next_c == 'N' and i+2 < length and pattern[i+2] == '{':
                            j = i+3
                            while j < length and pattern[j] != '}':
                                j += 1
                            if j < length and pattern[j] == '}':
                                tokens.append(RegexToken(type='ESCAPE', value=pattern[i:j+1]))
                                i = j+1
                            else:
                                tokens.append(RegexToken(type='ESCAPE', value=pattern[i:i+2]))
                                i += 2
                        else:
                            tokens.append(RegexToken(type='ESCAPE', value=pattern[i:i+2]))
                            i += 2
                    else:
                        tokens.append(RegexToken(type='ESCAPE', value=pattern[i:i+2]))
                        i += 2
                else:
                    tokens.append(RegexToken(type='ESCAPE', value=c))
                    i += 1
            # Specials (other than quantifiers)
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
    """
    Represents a single regex component (token) in the pattern.
    """
    type: str
    value: str
