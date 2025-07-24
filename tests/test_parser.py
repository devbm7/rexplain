import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from rexplain.core.parser import RegexParser, RegexToken

def test_tokenize_basic():
    parser = RegexParser()
    pattern = r'a*b+c?\d'
    tokens = parser.tokenize(pattern)
    expected = [
        RegexToken(type='LITERAL', value='a'),
        RegexToken(type='SPECIAL', value='*'),
        RegexToken(type='LITERAL', value='b'),
        RegexToken(type='SPECIAL', value='+'),
        RegexToken(type='LITERAL', value='c'),
        RegexToken(type='SPECIAL', value='?'),
        RegexToken(type='ESCAPE', value=r'\d'),
    ]
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_tokenize_char_class():
    parser = RegexParser()
    pattern = r'[a-zA-Z0-9_]'
    tokens = parser.tokenize(pattern)
    expected = [
        RegexToken(type='CHAR_CLASS', value='[a-zA-Z0-9_]'),
    ]
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_tokenize_non_capturing_group():
    parser = RegexParser()
    pattern = r'(?:abc)'
    tokens = parser.tokenize(pattern)
    expected = [
        RegexToken(type='GROUP_NONCAP', value='(?:'),
        RegexToken(type='LITERAL', value='a'),
        RegexToken(type='LITERAL', value='b'),
        RegexToken(type='LITERAL', value='c'),
        RegexToken(type='GROUP_CLOSE', value=')'),
    ]
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_tokenize_named_group():
    parser = RegexParser()
    pattern = r'(?P<name>abc)'
    tokens = parser.tokenize(pattern)
    expected = [
        RegexToken(type='GROUP_NAMED', value='(?P<name>'),
        RegexToken(type='LITERAL', value='a'),
        RegexToken(type='LITERAL', value='b'),
        RegexToken(type='LITERAL', value='c'),
        RegexToken(type='GROUP_CLOSE', value=')'),
    ]
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_tokenize_quantifier_braces():
    parser = RegexParser()
    pattern = r'a{2,3}'
    tokens = parser.tokenize(pattern)
    expected = [
        RegexToken(type='LITERAL', value='a'),
        RegexToken(type='QUANTIFIER', value='{2,3}'),
    ]
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_tokenize_lookahead():
    parser = RegexParser()
    pattern = r'foo(?=bar)'
    tokens = parser.tokenize(pattern)
    expected = [
        RegexToken(type='LITERAL', value='f'),
        RegexToken(type='LITERAL', value='o'),
        RegexToken(type='LITERAL', value='o'),
        RegexToken(type='GROUP_LOOKAHEAD', value='(?='),
        RegexToken(type='LITERAL', value='b'),
        RegexToken(type='LITERAL', value='a'),
        RegexToken(type='LITERAL', value='r'),
        RegexToken(type='GROUP_CLOSE', value=')'),
    ]
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_tokenize_lookbehind():
    parser = RegexParser()
    pattern = r'(?<=foo)bar'
    tokens = parser.tokenize(pattern)
    expected = [
        RegexToken(type='GROUP_LOOKBEHIND', value='(?<='),
        RegexToken(type='LITERAL', value='f'),
        RegexToken(type='LITERAL', value='o'),
        RegexToken(type='LITERAL', value='o'),
        RegexToken(type='GROUP_CLOSE', value=')'),
        RegexToken(type='LITERAL', value='b'),
        RegexToken(type='LITERAL', value='a'),
        RegexToken(type='LITERAL', value='r'),
    ]
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_parse_flat_ast():
    from rexplain.core.parser import RegexParser, Sequence, Literal, CharClass, Escape, Anchor, Quantifier, Group
    parser = RegexParser()
    pattern = r'a[0-9]\d^$*'
    ast = parser.parse(pattern)
    # For MVP, quantifier and group are not context-aware, so '*' is Quantifier(Literal(''), '*')
    expected = Sequence([
        Literal('a'),
        CharClass('[0-9]'),
        Escape(r'\d'),
        Anchor('^'),
        Anchor('$'),
        Quantifier(Literal(''), '*'),
    ])
    # Compare types and values for each node in sequence
    assert isinstance(ast, Sequence), f"Expected Sequence, got {type(ast)}"
    assert len(ast.elements) == len(expected.elements), f"Expected {len(expected.elements)} elements, got {len(ast.elements)}"
    for node, exp in zip(ast.elements, expected.elements):
        assert type(node) == type(exp), f"Expected node type {type(exp)}, got {type(node)}"
        assert getattr(node, 'value', getattr(node, 'quant', None)) == getattr(exp, 'value', getattr(exp, 'quant', None)), f"Expected value {getattr(exp, 'value', getattr(exp, 'quant', None))}, got {getattr(node, 'value', getattr(node, 'quant', None))}"

def main():
    test_tokenize_basic()
    print('test_tokenize_basic passed')
    test_tokenize_char_class()
    print('test_tokenize_char_class passed')
    test_tokenize_non_capturing_group()
    print('test_tokenize_non_capturing_group passed')
    test_tokenize_named_group()
    print('test_tokenize_named_group passed')
    test_tokenize_quantifier_braces()
    print('test_tokenize_quantifier_braces passed')
    test_tokenize_lookahead()
    print('test_tokenize_lookahead passed')
    test_tokenize_lookbehind()
    print('test_tokenize_lookbehind passed')
    test_parse_flat_ast()
    print('test_parse_flat_ast passed')
    print('All tests passed!')

if __name__ == '__main__':
    main() 