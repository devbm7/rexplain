from typing import Union
from .parser import RegexAST, Literal, CharClass, Escape, Quantifier, Anchor, Sequence, Alternation, Group

import string

def _token_and_explanation(ast: RegexAST) -> list:
    lines = []
    if isinstance(ast, Sequence):
        for elem in ast.elements:
            lines.extend(_token_and_explanation(elem))
    elif isinstance(ast, Alternation):
        # Each option on a new line, with 'or' for clarity
        for i, opt in enumerate(ast.options):
            opt_lines = _token_and_explanation(opt)
            if i > 0:
                opt_lines[0] = 'or ' + opt_lines[0]
            lines.extend(opt_lines)
    elif isinstance(ast, Quantifier):
        # Combine quantifier with its child token
        child = ast.child
        if isinstance(child, (Literal, Escape, CharClass, Group)):
            token = _get_token(child) + ast.quant
            explanation = _explain_token(child, quant=ast.quant)
            lines.append(f"{token} - {explanation}")
        else:
            # For complex children, recurse
            for l in _token_and_explanation(child):
                lines.append(f"{l.split(' - ')[0]}{ast.quant} - {l.split(' - ')[1]} repeated as per quantifier '{ast.quant}'")
    else:
        token = _get_token(ast)
        explanation = _explain_token(ast)
        lines.append(f"{token} - {explanation}")
    return lines

def _get_token(ast: RegexAST) -> str:
    if isinstance(ast, Literal):
        return ast.value
    elif isinstance(ast, Escape):
        return ast.value
    elif isinstance(ast, CharClass):
        return ast.value
    elif isinstance(ast, Anchor):
        return ast.value
    elif isinstance(ast, Group):
        if ast.group_type == 'GROUP_NAMED' and ast.name:
            return f"(?P<{ast.name}>)"
        elif ast.group_type == 'GROUP_NONCAP':
            return "(?:...)"
        elif ast.group_type == 'GROUP_FLAGS' and ast.flags:
            return f"(?{ast.flags})"
        else:
            return "(...)"
    return str(ast)

def _explain_token(ast: RegexAST, quant: str = None) -> str:
    if isinstance(ast, Literal):
        c = ast.value
        code = ord(c) if len(c) == 1 else None
        code_str = f" (ASCII {code})" if code is not None and c in string.printable else ""
        return f"matches the character '{c}'{code_str} literally (case sensitive)"
    elif isinstance(ast, Escape):
        escape_map = {
            r'\\': 'a literal backslash',
            r'\d': 'a digit character',
            r'\w': 'a word character',
            r'\s': 'a whitespace character',
            r'\D': 'a non-digit character',
            r'\W': 'a non-word character',
            r'\S': 'a non-whitespace character',
            r'\n': 'a newline character',
            r'\t': 'a tab character',
            r'\r': 'a carriage return',
            r'\b': 'a word boundary',
            r'\B': 'a non-word boundary',
        }
        return f"matches {escape_map.get(ast.value, 'the escape sequence ' + ast.value)}"
    elif isinstance(ast, CharClass):
        return f"matches any character in the set {ast.value}"
    elif isinstance(ast, Anchor):
        anchor_map = {
            '^': 'asserts position at the start of a line',
            '$': 'asserts position at the end of a line',
            r'\b': 'a word boundary',
            r'\B': 'a non-word boundary',
        }
        return anchor_map.get(ast.value, f"the anchor '{ast.value}'")
    elif isinstance(ast, Group):
        group_type_map = {
            'GROUP_NONCAP': 'a non-capturing group',
            'GROUP_NAMED': f"a named group '{ast.name}'" if ast.name else 'a named group',
            'GROUP_LOOKAHEAD': 'a lookahead group (must be followed by)',
            'GROUP_NEG_LOOKAHEAD': 'a negative lookahead group (must NOT be followed by)',
            'GROUP_LOOKBEHIND': 'a lookbehind group (must be preceded by)',
            'GROUP_NEG_LOOKBEHIND': 'a negative lookbehind group (must NOT be preceded by)',
            'GROUP_FLAGS': f'a group with flags ({ast.flags})' if ast.flags else 'a group with flags',
            'GROUP_CONDITIONAL': 'a conditional group',
            'GROUP_OPEN': 'a capturing group',
        }
        desc = group_type_map.get(ast.group_type, 'a group')
        if ast.children:
            child_lines = []
            for child in ast.children:
                child_lines.extend(_token_and_explanation(child))
            return f"{desc} containing:\n  " + "\n  ".join(child_lines)
        else:
            return desc
    if quant:
        quant_desc = _quantifier_explanation(quant)
        return f"{_explain_token(ast)} {quant_desc}"
    return f"matches {ast}"

def _quantifier_explanation(quant: str) -> str:
    if quant == '*':
        return 'zero or more times (greedy)'
    elif quant == '+':
        return 'one or more times (greedy)'
    elif quant == '?':
        return 'zero or one time (greedy)'
    elif quant.endswith('?'):
        base = quant[:-1]
        if base == '*':
            return 'zero or more times (non-greedy)'
        elif base == '+':
            return 'one or more times (non-greedy)'
        elif base == '?':
            return 'zero or one time (non-greedy)'
        elif base.startswith('{'):
            return f"{base} times (non-greedy)"
        else:
            return f"{quant} times"
    elif quant.startswith('{'):
        import re
        m = re.match(r'\{(\d+)(,(\d*)?)?\}', quant)
        if m:
            n1 = m.group(1)
            n2 = m.group(3)
            if n2 == '' or n2 is None:
                return f"exactly {n1} times"
            else:
                return f"{n1} to {n2} times"
        else:
            return f"{quant} times"
    else:
        return f"{quant} times"


def explain(ast: RegexAST) -> str:
    r"""
    Return a line-by-line, context-aware explanation of the regex AST.

    Args:
        ast (RegexAST): The root node of the regex AST.

    Returns:
        str: A formatted, line-by-line explanation of the regex pattern.
    """
    lines = _token_and_explanation(ast)
    return '\n'.join(lines)

class RegexExplainer:
    """
    Provides human-readable explanations for regex patterns.
    """
    def explain(self, pattern: str, flags: int = 0) -> str:
        r"""
        Explain a regex pattern as a formatted, line-by-line string.

        Args:
            pattern (str): The regex pattern to explain.
            flags (int, optional): Regex flags (e.g., re.IGNORECASE). Defaults to 0.

        Returns:
            str: A line-by-line explanation of the regex pattern.
        """
        from .parser import RegexParser
        ast = RegexParser().parse(pattern, flags=flags)
        return explain(ast)
