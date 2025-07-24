from typing import Union
from .parser import RegexAST, Literal, CharClass, Escape, Quantifier, Anchor, Sequence, Alternation, Group

def explain(ast: RegexAST) -> str:
    """Recursively explain a regex AST node as a human-readable string."""
    if isinstance(ast, Literal):
        return f"the character '{ast.value}'"
    elif isinstance(ast, CharClass):
        return f"a character in the set {ast.value}"
    elif isinstance(ast, Escape):
        # Map common escapes to English
        escape_map = {
            r'\d': 'a digit character',
            r'\w': 'a word character',
            r'\s': 'a whitespace character',
            r'\D': 'a non-digit character',
            r'\W': 'a non-word character',
            r'\S': 'a non-whitespace character',
            r'\\': 'a literal backslash',
        }
        return escape_map.get(ast.value, f"the escape sequence '{ast.value}'")
    elif isinstance(ast, Quantifier):
        quant_map = {
            '*': 'zero or more times',
            '+': 'one or more times',
            '?': 'zero or one time',
        }
        quant = quant_map.get(ast.quant, f"{ast.quant} times")
        return f"{explain(ast.child)} repeated {quant}"
    elif isinstance(ast, Anchor):
        anchor_map = {
            '^': 'the start of the string',
            '$': 'the end of the string',
        }
        return anchor_map.get(ast.value, f"the anchor '{ast.value}'")
    elif isinstance(ast, Sequence):
        return ' followed by '.join([explain(e) for e in ast.elements])
    elif isinstance(ast, Alternation):
        return ' or '.join([explain(opt) for opt in ast.options])
    elif isinstance(ast, Group):
        group_type_map = {
            'GROUP_NONCAP': 'a non-capturing group containing',
            'GROUP_NAMED': 'a named group containing',
            'GROUP_LOOKAHEAD': 'a lookahead group containing',
            'GROUP_NEG_LOOKAHEAD': 'a negative lookahead group containing',
            'GROUP_LOOKBEHIND': 'a lookbehind group containing',
            'GROUP_NEG_LOOKBEHIND': 'a negative lookbehind group containing',
            'GROUP_FLAGS': 'a group with flags containing',
            'GROUP_CONDITIONAL': 'a conditional group containing',
            'GROUP_OPEN': 'a capturing group containing',
        }
        desc = group_type_map.get(ast.group_type, 'a group containing')
        if ast.name:
            desc += f" '{ast.name}'"
        if ast.children:
            children_desc = ' followed by '.join([explain(child) for child in ast.children])
            return f"{desc} {children_desc}"
        else:
            return f"{desc} (empty)"
    else:
        return f"an unknown regex construct: {ast}"
