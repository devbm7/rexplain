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
    def test(self, pattern: str, test_string: str, flags: int = 0) -> MatchResult:
        prog = re.compile(pattern, flags)
        m = prog.fullmatch(test_string)
        if m:
            return MatchResult(matches=True, reason="Full match.")
        # Check if pattern is a literal (no regex metacharacters)
        if not re.search(r'[.^$*+?{}\\[\\]|()]', pattern):
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
