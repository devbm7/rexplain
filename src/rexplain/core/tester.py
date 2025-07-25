import re
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class MatchResult:
    """
    Represents the result of testing a string against a regex pattern.

    Attributes:
        matches (bool): Whether the string fully matches the pattern.
        reason (str): Explanation of the match or failure.
        failed_at (Optional[int]): Index where the match failed, if applicable.
        partial_matches (Optional[List[str]]): List of partial matches, if any.
    """
    matches: bool
    reason: str
    failed_at: Optional[int] = None
    partial_matches: Optional[List[str]] = None

    def __str__(self):
        return (
            f"MatchResult(matches={self.matches}, reason=\"{self.reason}\", "
            f"failed_at={self.failed_at}, partial_matches={self.partial_matches})"
        )

class RegexTester:
    """
    Tests if a string matches a regex pattern and provides detailed feedback.
    """
    def test(self, pattern: str, test_string: str, flags: int = 0) -> MatchResult:
        r"""
        Test if a string matches a regex pattern and explain why/why not.

        Args:
            pattern (str): The regex pattern.
            test_string (str): The string to test.
            flags (int, optional): Regex flags (e.g., re.IGNORECASE). Defaults to 0.

        Returns:
            MatchResult: Result object with match status and explanation.
        """
        prog = re.compile(pattern, flags)
        m = prog.fullmatch(test_string)
        if m:
            return MatchResult(matches=True, reason="Full match.")

        # Try to use the parser for step-by-step analysis
        try:
            from .parser import RegexParser, Literal, CharClass, Escape, Sequence
            ast = RegexParser().parse(pattern, flags=flags)
            # Only handle simple sequences of literals/char classes for now
            if isinstance(ast, Sequence):
                elements = ast.elements
            else:
                elements = [ast]
            i = 0
            j = 0
            details = []
            while i < len(elements) and j < len(test_string):
                node = elements[i]
                c = test_string[j]
                if isinstance(node, Literal):
                    if c == node.value:
                        details.append(f"{c!r} matches literal '{node.value}' at position {j}")
                        i += 1
                        j += 1
                    else:
                        reason = (f"Failed at position {j}: expected literal '{node.value}', got '{c}'")
                        return MatchResult(
                            matches=False,
                            reason=reason,
                            failed_at=j,
                            partial_matches=[test_string[:j]] if j > 0 else []
                        )
                elif isinstance(node, CharClass):
                    import re as _re
                    charclass = node.value
                    # Remove brackets for eval
                    pattern = charclass
                    if pattern.startswith('[') and pattern.endswith(']'):
                        pattern = pattern[1:-1]
                    # Build a regex for the char class
                    charclass_re = _re.compile(f"[{pattern}]")
                    if charclass_re.fullmatch(c):
                        details.append(f"{c!r} matches character class {node.value} at position {j}")
                        i += 1
                        j += 1
                    else:
                        reason = (f"Failed at position {j}: expected character in {node.value}, got '{c}'")
                        return MatchResult(
                            matches=False,
                            reason=reason,
                            failed_at=j,
                            partial_matches=[test_string[:j]] if j > 0 else []
                        )
                elif isinstance(node, Escape):
                    import re as _re
                    esc = node.value
                    esc_re = _re.compile(esc)
                    display_esc = esc  # Always show as written (e.g., '\d')
                    if esc_re.fullmatch(c):
                        details.append(f"{c!r} matches escape {display_esc} at position {j}")
                        i += 1
                        j += 1
                    else:
                        reason = (f"Failed at position {j}: expected {display_esc}, got '{c}'")
                        return MatchResult(
                            matches=False,
                            reason=reason,
                            failed_at=j,
                            partial_matches=[test_string[:j]] if j > 0 else []
                        )
                else:
                    # For now, fallback to regex engine for complex nodes
                    break
            # If we finished all pattern elements but string is too short
            if i < len(elements):
                reason = f"String too short: expected more input for pattern element {elements[i]} at position {j}"
                return MatchResult(
                    matches=False,
                    reason=reason,
                    failed_at=j,
                    partial_matches=[test_string[:j]] if j > 0 else []
                )
            # If we finished all pattern elements but string is too long
            if j < len(test_string):
                reason = f"String too long: extra input '{test_string[j:]}' at position {j}"
                return MatchResult(
                    matches=False,
                    reason=reason,
                    failed_at=j,
                    partial_matches=[test_string[:j]] if j > 0 else []
                )
        except Exception as e:
            # Fallback to regex engine for complex patterns or parser errors
            pass

        # Fallback: original logic
        # Check if pattern is a literal (no regex metacharacters)
        if not re.search(r'[.^$*+?{}\[\]|()]', pattern):
            # Literal pattern: compare character by character
            match_len = 0
            for c1, c2 in zip(pattern, test_string):
                if c1 == c2:
                    match_len += 1
                else:
                    break
            failed_at = match_len
            reason = (
                f"Match failed at position {failed_at}: unexpected character '{test_string[failed_at]}'"
                if failed_at < len(test_string)
                else "String too short."
            )
            partial_matches = [test_string[:match_len]] if match_len > 0 else []
            return MatchResult(
                matches=False,
                reason=reason,
                failed_at=failed_at,
                partial_matches=partial_matches
            )
        # Regex pattern: use current logic
        longest = 0
        for i in range(1, len(test_string) + 1):
            m = prog.fullmatch(test_string[:i])
            if m:
                longest = i
        if longest > 0:
            failed_at = None
            for i, (c1, c2) in enumerate(zip(pattern, test_string)):
                if c1 != c2:
                    failed_at = i
                    break
            if failed_at is None:
                failed_at = min(len(pattern), len(test_string))
            reason = (
                f"Match failed at position {failed_at}: unexpected character '{test_string[failed_at]}'"
                if failed_at < len(test_string)
                else "String too short."
            )
            return MatchResult(
                matches=False,
                reason=reason,
                failed_at=failed_at,
                partial_matches=[test_string[:longest]]
            )
        failed_at = 0
        for i, (c1, c2) in enumerate(zip(pattern, test_string)):
            if c1 != c2:
                failed_at = i
                break
        else:
            failed_at = min(len(pattern), len(test_string))
        return MatchResult(matches=False, reason="No match at all.", failed_at=failed_at, partial_matches=[])