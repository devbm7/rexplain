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

if __name__ == '__main__':
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
    print('All tests passed!') 