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
            r'\n': 'a newline character',
            r'\t': 'a tab character',
            r'\r': 'a carriage return',
        }
        return escape_map.get(ast.value, f"the escape sequence '{ast.value}'")
    elif isinstance(ast, Quantifier):
        # Handle nuanced quantifiers
        quant = ast.quant
        if quant == '*':
            quant_desc = 'zero or more times'
        elif quant == '+':
            quant_desc = 'one or more times'
        elif quant == '?':
            quant_desc = 'zero or one time'
        elif quant.endswith('?'):
            # Non-greedy
            base = quant[:-1]
            if base == '*':
                quant_desc = 'zero or more times (non-greedy)'
            elif base == '+':
                quant_desc = 'one or more times (non-greedy)'
            elif base == '?':
                quant_desc = 'zero or one time (non-greedy)'
            elif base.startswith('{'):
                quant_desc = f"{base} times (non-greedy)"
            else:
                quant_desc = f"{quant} times"
        elif quant.startswith('{'):
            import re
            m = re.match(r'\{(\d+)(,(\d*)?)?\}', quant)
            if m:
                n1 = m.group(1)
                n2 = m.group(3)
                if n2 == '' or n2 is None:
                    quant_desc = f"exactly {n1} times"
                else:
                    quant_desc = f"{n1} to {n2} times"
            else:
                quant_desc = f"{quant} times"
        else:
            quant_desc = f"{quant} times"
        return f"{explain(ast.child)} repeated {quant_desc}"
    elif isinstance(ast, Anchor):
        anchor_map = {
            '^': 'the start of the string',
            '$': 'the end of the string',
            r'\b': 'a word boundary',
            r'\B': 'a non-word boundary',
        }
        return anchor_map.get(ast.value, f"the anchor '{ast.value}'")
    elif isinstance(ast, Sequence):
        return ' followed by '.join([explain(e) for e in ast.elements])
    elif isinstance(ast, Alternation):
        # Use parentheses for clarity if options are complex
        options = [explain(opt) for opt in ast.options]
        return ' or '.join([f"({opt})" if 'followed by' in opt or ' or ' in opt else opt for opt in options])
    elif isinstance(ast, Group):
        group_type_map = {
            'GROUP_NONCAP': 'a non-capturing group containing',
            'GROUP_NAMED': 'a named group',
            'GROUP_LOOKAHEAD': 'a lookahead group (must be followed by)',
            'GROUP_NEG_LOOKAHEAD': 'a negative lookahead group (must NOT be followed by)',
            'GROUP_LOOKBEHIND': 'a lookbehind group (must be preceded by)',
            'GROUP_NEG_LOOKBEHIND': 'a negative lookbehind group (must NOT be preceded by)',
            'GROUP_FLAGS': 'a group with flags',
            'GROUP_CONDITIONAL': 'a conditional group',
            'GROUP_OPEN': 'a capturing group',
        }
        desc = group_type_map.get(ast.group_type, 'a group')
        if ast.group_type == 'GROUP_NAMED' and ast.name:
            desc += f" named '{ast.name}'"
        if ast.group_type == 'GROUP_FLAGS' and ast.flags:
            desc += f" (flags: {ast.flags})"
        if ast.group_type.startswith('GROUP_LOOK') or ast.group_type.startswith('GROUP_NEG_LOOK'):
            # Lookahead/lookbehind: explain as assertion
            if ast.children:
                children_desc = ' and '.join([explain(child) for child in ast.children])
                return f"{desc} {children_desc}"
            else:
                return f"{desc} (empty)"
        if ast.children:
            children_desc = ' followed by '.join([explain(child) for child in ast.children])
            return f"{desc} {children_desc}"
        else:
            return f"{desc} (empty)"
    else:
        return f"an unknown regex construct: {ast}"
