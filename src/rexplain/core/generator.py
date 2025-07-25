import random
from typing import List, Tuple
from .parser import RegexParser, RegexAST, Literal, CharClass, Escape, Quantifier, Anchor, Sequence, Alternation, Group

class ExampleGenerator:
    """
    Generates example strings that match a given regex pattern using the AST.
    """
    def __init__(self):
        """
        Initialize the ExampleGenerator.
        """
        self.parser = RegexParser()
        # For negated char classes, pick from this set
        self.default_charset = [chr(i) for i in range(32, 127)]

    def generate(self, pattern: str, count: int = 3, flags: int = 0) -> List[str]:
        """
        Generate a list of example strings that match the given regex pattern.

        Args:
            pattern (str): The regex pattern.
            count (int, optional): Number of examples to generate. Defaults to 3.
            flags (int, optional): Regex flags (e.g., re.IGNORECASE). Defaults to 0.

        Returns:
            List[str]: Example strings matching the pattern.
        """
        ast = self.parser.parse(pattern, flags=flags)
        # For alternations, try to cover all branches if possible
        if isinstance(ast, Alternation) and count <= len(ast.options):
            return [self._generate_from_ast(opt) for opt in ast.options[:count]]
        # Special handling for anchored patterns: only generate the exact match
        if self._is_fully_anchored(ast):
            return [self._generate_from_ast(ast)] * count
        return [self._generate_from_ast(ast) for _ in range(count)]

    def _is_fully_anchored(self, ast: RegexAST) -> bool:
        # Returns True if the pattern is ^...$ (fully anchored)
        if isinstance(ast, Sequence):
            elements = ast.elements
            if len(elements) >= 2 and isinstance(elements[0], Anchor) and elements[0].value == '^' and \
               isinstance(elements[-1], Anchor) and elements[-1].value == '$':
                return True
            if len(elements) == 1 and isinstance(elements[0], Anchor):
                return True
        if isinstance(ast, Anchor):
            return True
        return False

    def _generate_from_ast(self, ast: RegexAST) -> str:
        if isinstance(ast, Literal):
            return ast.value
        elif isinstance(ast, CharClass):
            chars, negated = self._parse_char_class(ast.value)
            if negated:
                candidates = [c for c in self.default_charset if c not in chars]
                return random.choice(candidates) if candidates else '?'
            else:
                return random.choice(chars) if chars else ''
        elif isinstance(ast, Escape):
            # Map escapes to representative characters
            escape_map = {
                r'\d': lambda: str(random.randint(0, 9)),
                r'\w': lambda: random.choice('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_'),
                r'\s': lambda: random.choice([' ', '\t', '\n']),
                r'\D': lambda: random.choice([c for c in self.default_charset if not c.isdigit()]),
                r'\W': lambda: random.choice([c for c in self.default_charset if not (c.isalnum() or c == '_')]),
                r'\S': lambda: random.choice([c for c in self.default_charset if not c.isspace()]),
                r'\\': lambda: '\\',
                r'\n': lambda: '\n',
                r'\t': lambda: '\t',
                r'\r': lambda: '\r',
                r'\b': lambda: '',  # word boundary, ignore in generation
                r'\B': lambda: '',  # non-word boundary, ignore
            }
            # Unicode/hex escapes
            if ast.value.startswith(r'\u') and len(ast.value) == 6:
                try:
                    codepoint = int(ast.value[2:], 16)
                    return chr(codepoint)
                except Exception:
                    return '?'
            if ast.value.startswith(r'\x') and len(ast.value) == 4:
                try:
                    codepoint = int(ast.value[2:], 16)
                    return chr(codepoint)
                except Exception:
                    return '?'
            return escape_map.get(ast.value, lambda: '?')()
        elif isinstance(ast, Quantifier):
            min_n, max_n = self._parse_quant(ast.quant)
            # For larger ranges, limit max_n for practicality
            max_n = min(max_n, 8)
            n = random.randint(min_n, max_n)
            return ''.join(self._generate_from_ast(ast.child) for _ in range(n))
        elif isinstance(ast, Anchor):
            # Anchors do not produce characters
            return ''
        elif isinstance(ast, Sequence):
            # If fully anchored, only generate the inner content
            if self._is_fully_anchored(ast):
                elements = ast.elements
                # Remove ^ and $ anchors
                inner = elements[1:-1]
                return ''.join(self._generate_from_ast(e) for e in inner)
            # Recursively generate for each element
            return ''.join(self._generate_from_ast(e) for e in ast.elements)
        elif isinstance(ast, Alternation):
            # Randomly pick one option, support nested alternations
            option = random.choice(ast.options)
            return self._generate_from_ast(option)
        elif isinstance(ast, Group):
            # For lookahead/lookbehind, do not generate any characters
            if ast.group_type in {'GROUP_LOOKAHEAD', 'GROUP_NEG_LOOKAHEAD', 'GROUP_LOOKBEHIND', 'GROUP_NEG_LOOKBEHIND'}:
                return ''
            # Recursively generate for each child (supports nested groups)
            return ''.join(self._generate_from_ast(child) for child in ast.children)
        else:
            return ''

    def _parse_char_class(self, class_str: str) -> Tuple[List[str], bool]:
        # Enhanced char class parser: supports negation and ranges
        chars = []
        negated = False
        if class_str.startswith('[') and class_str.endswith(']'):
            inner = class_str[1:-1]
            if inner.startswith('^'):
                negated = True
                inner = inner[1:]
            i = 0
            while i < len(inner):
                if i+2 < len(inner) and inner[i+1] == '-':
                    # Range
                    start, end = inner[i], inner[i+2]
                    chars.extend([chr(c) for c in range(ord(start), ord(end)+1)])
                    i += 3
                else:
                    chars.append(inner[i])
                    i += 1
        return chars, negated

    def _parse_quant(self, quant: str) -> Tuple[int, int]:
        # Returns (min, max) for quantifier
        if quant == '*':
            return (0, 4)
        elif quant == '+':
            return (1, 4)
        elif quant == '?':
            return (0, 1)
        elif quant.endswith('?'):
            # Non-greedy, treat as normal
            return self._parse_quant(quant[:-1])
        elif quant.startswith('{'):
            import re
            m = re.match(r'\{(\d+)(,(\d*)?)?\}', quant)
            if m:
                n1 = int(m.group(1))
                n2 = m.group(3)
                if n2 == '' or n2 is None:
                    return (n1, n1)
                elif n2:
                    return (n1, int(n2) if n2.isdigit() else n1+4)
            return (1, 1)
        else:
            return (1, 1)
