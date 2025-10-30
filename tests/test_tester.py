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

def test_match_result_str():
    tester = RegexTester()
    result = tester.test('abc', 'abc')
    str_repr = str(result)
    assert 'MatchResult' in str_repr
    assert 'matches=True' in str_repr
    print('test_match_result_str passed')

def test_string_too_long():
    tester = RegexTester()
    result = tester.test('abc', 'abcdef')
    assert result.matches is False
    assert 'too long' in result.reason.lower() or 'extra input' in result.reason.lower()
    print('test_string_too_long passed')

def test_complex_alternation():
    tester = RegexTester()
    result = tester.test(r'(foo|bar|baz)', 'foo')
    assert result.matches is True
    result = tester.test(r'(foo|bar|baz)', 'qux')
    assert result.matches is False
    print('test_complex_alternation passed')

def test_quantifier_patterns():
    tester = RegexTester()
    # Test ? quantifier
    result = tester.test(r'ab?c', 'ac')
    assert result.matches is True
    result = tester.test(r'ab?c', 'abc')
    assert result.matches is True
    # Test {n,m} quantifier
    result = tester.test(r'a{2,3}', 'aa')
    assert result.matches is True
    result = tester.test(r'a{2,3}', 'aaaa')
    assert result.matches is False
    print('test_quantifier_patterns passed')

def test_anchor_patterns():
    tester = RegexTester()
    result = tester.test(r'^abc', 'abc')
    assert result.matches is True
    result = tester.test(r'abc$', 'abc')
    assert result.matches is True
    result = tester.test(r'^abc$', 'abc')
    assert result.matches is True
    print('test_anchor_patterns passed')

def test_empty_pattern():
    tester = RegexTester()
    result = tester.test('', '')
    assert result.matches is True
    print('test_empty_pattern passed')

def test_special_characters():
    tester = RegexTester()
    result = tester.test(r'\.\*\+', '.*+')
    assert result.matches is True
    print('test_special_characters passed')

def test_unicode_patterns():
    tester = RegexTester()
    result = tester.test(r'\u0061', 'a')
    assert result.matches is True
    print('test_unicode_patterns passed')

def test_lookahead_pattern():
    tester = RegexTester()
    result = tester.test(r'foo(?=bar)', 'foo')
    assert result.matches is False
    result = tester.test(r'foo(?=bar)bar', 'foobar')
    assert result.matches is True
    print('test_lookahead_pattern passed')

def test_partial_match_details():
    tester = RegexTester()
    result = tester.test('abcdef', 'abcxyz')
    assert result.matches is False
    assert result.partial_matches is not None
    assert 'abc' in result.partial_matches
    print('test_partial_match_details passed')

def test_match_result_to_dict():
    tester = RegexTester()
    result = tester.test('abc', 'abc')
    # Test that MatchResult can be converted to dict
    assert hasattr(result, 'to_dict')
    result_dict = result.to_dict()
    assert isinstance(result_dict, dict)
    assert 'matches' in result_dict
    assert 'reason' in result_dict
    assert 'failed_at' in result_dict
    assert 'partial_matches' in result_dict
    assert result_dict['matches'] is True
    print('test_match_result_to_dict passed')

def main():
    test_full_match()
    test_no_match()
    test_partial_match()
    test_too_short()
    test_charclass_fail()
    test_escape_fail()
    test_regex_features()
    test_flag_sensitive_match()
    test_match_result_str()
    test_string_too_long()
    test_complex_alternation()
    test_quantifier_patterns()
    test_anchor_patterns()
    test_empty_pattern()
    test_special_characters()
    test_unicode_patterns()
    test_lookahead_pattern()
    test_partial_match_details()
    test_match_result_to_dict()
    print('All tester tests passed!')

if __name__ == '__main__':
    main() 