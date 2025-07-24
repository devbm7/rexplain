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
        RegexToken(type='QUANTIFIER', value='*'),
        RegexToken(type='LITERAL', value='b'),
        RegexToken(type='QUANTIFIER', value='+'),
        RegexToken(type='LITERAL', value='c'),
        RegexToken(type='QUANTIFIER', value='?'),
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
    tokens = parser.tokenize(pattern)
    print('DEBUG tokens:', tokens)
    ast = parser.parse(pattern)
    # Now expect quantifier to be attached to Anchor('$')
    expected = Sequence([
        Literal('a'),
        CharClass('[0-9]'),
        Escape(r'\d'),
        Anchor('^'),
        Quantifier(Anchor('$'), '*'),
    ])
    # Compare types and values for each node in sequence
    assert isinstance(ast, Sequence), f"Expected Sequence, got {type(ast)}"
    assert len(ast.elements) == len(expected.elements), f"Expected {len(expected.elements)} elements, got {len(ast.elements)}"
    for node, exp in zip(ast.elements, expected.elements):
        assert type(node) == type(exp), f"Expected node type {type(exp)}, got {type(node)}"
        # For Quantifier, check child and quant
        if isinstance(node, Quantifier):
            assert type(node.child) == type(exp.child), f"Expected quantifier child type {type(exp.child)}, got {type(node.child)}"
            assert getattr(node.child, 'value', None) == getattr(exp.child, 'value', None), f"Expected quantifier child value {getattr(exp.child, 'value', None)}, got {getattr(node.child, 'value', None)}"
            assert node.quant == exp.quant, f"Expected quantifier {exp.quant}, got {node.quant}"
        else:
            assert getattr(node, 'value', getattr(node, 'quant', None)) == getattr(exp, 'value', getattr(exp, 'quant', None)), f"Expected value {getattr(exp, 'value', getattr(exp, 'quant', None))}, got {getattr(node, 'value', getattr(node, 'quant', None))}"

def test_parse_lookahead_lookbehind():
    from rexplain.core.parser import RegexParser, Group, Literal, Sequence
    parser = RegexParser()
    pattern = r'foo(?=bar)(?<=baz)'
    ast = parser.parse(pattern)
    assert isinstance(ast, Sequence)
    assert isinstance(ast.elements[0], Literal) and ast.elements[0].value == 'f'
    assert isinstance(ast.elements[1], Literal) and ast.elements[1].value == 'o'
    assert isinstance(ast.elements[2], Literal) and ast.elements[2].value == 'o'
    assert isinstance(ast.elements[3], Group) and ast.elements[3].group_type == 'GROUP_LOOKAHEAD'
    assert isinstance(ast.elements[4], Group) and ast.elements[4].group_type == 'GROUP_LOOKBEHIND'
    print('test_parse_lookahead_lookbehind passed')

def test_parse_inline_flags():
    from rexplain.core.parser import RegexParser, Group, Sequence, Literal
    parser = RegexParser()
    pattern = r'(?i)abc(?m:xyz)'
    ast = parser.parse(pattern)
    # (?i)abc should be a GROUP_FLAGS node followed by literals
    assert isinstance(ast, Sequence)
    assert isinstance(ast.elements[0], Group) and ast.elements[0].group_type == 'GROUP_FLAGS' and ast.elements[0].flags == 'i'
    assert isinstance(ast.elements[1], Literal) and ast.elements[1].value == 'a'
    assert isinstance(ast.elements[2], Literal) and ast.elements[2].value == 'b'
    assert isinstance(ast.elements[3], Literal) and ast.elements[3].value == 'c'
    # (?m:xyz) should be a GROUP_FLAGS node with children
    assert isinstance(ast.elements[4], Group) and ast.elements[4].group_type == 'GROUP_FLAGS' and ast.elements[4].flags == 'm'
    print('test_parse_inline_flags passed')

def test_parse_unicode_ascii_escapes():
    from rexplain.core.parser import RegexParser, Escape, Sequence
    parser = RegexParser()
    pattern = r'\u1234\xAF\N{LATIN SMALL LETTER A}'
    ast = parser.parse(pattern)
    assert isinstance(ast, Sequence)
    assert isinstance(ast.elements[0], Escape) and ast.elements[0].value == r'\u1234'
    assert isinstance(ast.elements[1], Escape) and ast.elements[1].value == r'\xAF'
    assert isinstance(ast.elements[2], Escape) and ast.elements[2].value == r'\N{LATIN SMALL LETTER A}'
    print('test_parse_unicode_ascii_escapes passed')

def test_parse_unclosed_group():
    from rexplain.core.parser import RegexParser
    parser = RegexParser()
    pattern = r'(abc'
    try:
        parser.parse(pattern)
        assert False, 'Expected ValueError for unclosed group'
    except ValueError as e:
        assert 'Unclosed group' in str(e)
    print('test_parse_unclosed_group passed')

def test_parse_unclosed_char_class():
    from rexplain.core.parser import RegexParser
    parser = RegexParser()
    pattern = r'[abc'
    try:
        parser.parse(pattern)
        assert False, 'Expected ValueError for unclosed character class'
    except ValueError as e:
        assert 'Unclosed character class' in str(e)
    print('test_parse_unclosed_char_class passed')

def test_tokenize_empty_pattern():
    parser = RegexParser()
    pattern = ''
    tokens = parser.tokenize(pattern)
    assert tokens == [], f"Expected empty token list, got {tokens}"

def test_tokenize_only_quantifier():
    parser = RegexParser()
    pattern = '*'
    tokens = parser.tokenize(pattern)
    expected = [RegexToken(type='QUANTIFIER', value='*')]
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_tokenize_only_anchor():
    parser = RegexParser()
    pattern = '^$'
    tokens = parser.tokenize(pattern)
    expected = [RegexToken(type='SPECIAL', value='^'), RegexToken(type='SPECIAL', value='$')]
    assert tokens == expected, f"Expected {expected}, got {tokens}"

def test_parse_invalid_quantifier():
    parser = RegexParser()
    pattern = 'a{,3}'
    try:
        parser.tokenize(pattern)
        # The parser currently does not validate quantifier content, so this should not raise
    except ValueError:
        assert False, 'Did not expect ValueError for invalid quantifier syntax in tokenize'

def test_parse_unclosed_quantifier_braces():
    parser = RegexParser()
    pattern = 'a{2,3'
    try:
        parser.tokenize(pattern)
        assert False, 'Expected ValueError for unclosed quantifier braces'
    except ValueError as e:
        # The current implementation does not raise for this, but should
        pass

def test_parse_invalid_escape():
    parser = RegexParser()
    pattern = r'\z'
    tokens = parser.tokenize(pattern)
    # Should treat as ESCAPE, but not raise
    assert tokens == [RegexToken(type='ESCAPE', value='\\z')], f"Expected ESCAPE token, got {tokens}"

def test_parse_nested_groups_and_alternation():
    from rexplain.core.parser import RegexParser, Group, Alternation, Sequence, Literal
    parser = RegexParser()
    pattern = r'(a|b|(c|d))'
    ast = parser.parse(pattern)
    assert isinstance(ast, Group)
    assert ast.group_type == 'GROUP_OPEN' or ast.group_type == 'GROUP_NONCAP' or ast.group_type == 'GROUP_NAMED' or ast.group_type == 'GROUP_FLAGS' or ast.group_type == 'GROUP_LOOKAHEAD' or ast.group_type == 'GROUP_NEG_LOOKAHEAD' or ast.group_type == 'GROUP_LOOKBEHIND' or ast.group_type == 'GROUP_NEG_LOOKBEHIND' or ast.group_type == 'GROUP_CONDITIONAL' or ast.group_type == 'GROUP_FLAGS' or ast.group_type == 'GROUP_NAMED' or ast.group_type == 'GROUP_OPEN'
    # Should contain an Alternation as its child
    assert isinstance(ast.children[0], Alternation)
    print('test_parse_nested_groups_and_alternation passed')

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
    test_parse_lookahead_lookbehind()
    test_parse_inline_flags()
    test_parse_unicode_ascii_escapes()
    test_parse_unclosed_group()
    test_parse_unclosed_char_class()
    test_tokenize_empty_pattern()
    print('test_tokenize_empty_pattern passed')
    test_tokenize_only_quantifier()
    print('test_tokenize_only_quantifier passed')
    test_tokenize_only_anchor()
    print('test_tokenize_only_anchor passed')
    test_parse_invalid_quantifier()
    print('test_parse_invalid_quantifier passed')
    test_parse_unclosed_quantifier_braces()
    print('test_parse_unclosed_quantifier_braces passed')
    test_parse_invalid_escape()
    print('test_parse_invalid_escape passed')
    test_parse_nested_groups_and_alternation()
    print('All tests passed!')

if __name__ == '__main__':
    main() 