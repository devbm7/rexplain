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

if __name__ == '__main__':
    test_tokenize_basic()
    print('All tests passed!') 