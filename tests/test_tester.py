import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from rexplain.core.tester import RegexTester, MatchResult

def test_full_match():
    tester = RegexTester()
    result = tester.test('abc', 'abc')
    assert result.matches is True
    assert result.reason == 'Full match.'
    assert result.failed_at is None
    assert result.partial_matches is None
    print('test_full_match passed')

def test_no_match():
    tester = RegexTester()
    result = tester.test('abc', 'xyz')
    assert result.matches is False
    assert result.failed_at == 0
    assert result.partial_matches == []
    # Should mention expected literal and got
    assert 'expected literal' in result.reason and 'got' in result.reason
    print('test_no_match passed')

def test_partial_match():
    tester = RegexTester()
    result = tester.test('abc', 'abx')
    print('DEBUG: failed_at =', result.failed_at)
    print('DEBUG: partial_matches =', result.partial_matches)
    assert result.matches is False
    assert result.failed_at == 2
    assert result.partial_matches == ['ab']
    # Should mention expected literal and got
    assert 'expected literal' in result.reason and 'got' in result.reason
    print('test_partial_match passed')
    
def test_too_short():
    tester = RegexTester()
    result = tester.test('abc', 'ab')
    assert result.matches is False
    assert result.failed_at == 2
    assert result.partial_matches == ['ab']
    # Should mention string too short or expected more input
    assert 'too short' in result.reason or 'expected more input' in result.reason
    print('test_too_short passed')

def test_charclass_fail():
    tester = RegexTester()
    result = tester.test(r'[0-9][a-z][A-Z]', '1a!')
    assert result.matches is False
    assert result.failed_at == 2
    assert 'expected character in [A-Z]' in result.reason and 'got' in result.reason
    print('test_charclass_fail passed')

def test_escape_fail():
    tester = RegexTester()
    # \d
    result = tester.test(r'\d', 'a')
    assert result.matches is False
    assert result.failed_at == 0
    assert r'expected \d' in result.reason and 'got' in result.reason
    # \w
    result = tester.test(r'\w', '!')
    assert result.matches is False
    assert result.failed_at == 0
    assert r'expected \w' in result.reason and 'got' in result.reason
    # \s
    result = tester.test(r'\s', 'A')
    assert result.matches is False
    assert result.failed_at == 0
    assert r'expected \s' in result.reason and 'got' in result.reason
    # \D
    result = tester.test(r'\D', '5')
    assert result.matches is False
    assert result.failed_at == 0
    assert r'expected \D' in result.reason and 'got' in result.reason
    # \S
    result = tester.test(r'\S', ' ')
    assert result.matches is False
    assert result.failed_at == 0
    assert r'expected \S' in result.reason and 'got' in result.reason
    # \W
    result = tester.test(r'\W', 'a')
    assert result.matches is False
    assert result.failed_at == 0
    assert r'expected \W' in result.reason and 'got' in result.reason
    print('test_escape_fail passed')

def test_regex_features():
    tester = RegexTester()
    result = tester.test(r'\d{2,4}', '123')
    assert result.matches is True
    result = tester.test(r'foo|bar', 'bar')
    assert result.matches is True
    result = tester.test(r'[a-z]+', 'abcxyz')
    assert result.matches is True
    print('test_regex_features passed')

def test_flag_sensitive_match():
    import re
    tester = RegexTester()
    # Without IGNORECASE, should not match
    result = tester.test('abc', 'ABC')
    assert result.matches is False
    # With IGNORECASE, should match
    result = tester.test('abc', 'ABC', flags=re.IGNORECASE)
    assert result.matches is True
    print('test_flag_sensitive_match passed')

def main():
    test_full_match()
    test_no_match()
    test_partial_match()
    test_too_short()
    test_charclass_fail()
    test_escape_fail()
    test_regex_features()
    test_flag_sensitive_match()
    print('All tester tests passed!')

if __name__ == '__main__':
    main() 