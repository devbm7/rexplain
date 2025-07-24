import re
from typing import Optional, List
from dataclasses import dataclass

@dataclass
class MatchResult:
    matches: bool
    reason: str
    failed_at: Optional[int] = None
    partial_matches: Optional[List[str]] = None

class RegexTester:
    """
    Test if a string matches a regex pattern and provide detailed feedback.
    """
    def test(self, pattern: str, test_string: str) -> MatchResult:
        prog = re.compile(pattern)
        m = prog.fullmatch(test_string)
        if m:
            return MatchResult(matches=True, reason="Full match.")
        # Try to find the longest matching prefix
        longest = 0
        for i in range(1, len(test_string) + 1):
            m = prog.fullmatch(test_string[:i])
            if m:
                longest = i
        if longest > 0:
            # For literal patterns, find the first index where test_string and pattern differ
            failed_at = None
            for i, (c1, c2) in enumerate(zip(pattern, test_string)):
                if c1 != c2:
                    failed_at = i
                    break
            if failed_at is None:
                # If one is a prefix of the other
                failed_at = min(len(pattern), len(test_string))
            reason = (
                f"Match failed at position {failed_at}: unexpected character '{test_string[failed_at]}'"
                if failed_at < len(test_string)
                else "String too short."
            )
            # partial_matches should be the matching prefix up to 'longest'
            return MatchResult(
                matches=False,
                reason=reason,
                failed_at=failed_at,
                partial_matches=[test_string[:longest]]
            )
        # If no prefix matches, find the first index where the pattern and string differ
        failed_at = 0
        for i, (c1, c2) in enumerate(zip(pattern, test_string)):
            if c1 != c2:
                failed_at = i
                break
        else:
            failed_at = min(len(pattern), len(test_string))
        return MatchResult(matches=False, reason="No match at all.", failed_at=failed_at, partial_matches=[])
