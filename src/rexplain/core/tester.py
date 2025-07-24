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
            return MatchResult(
                matches=False,
                reason=f"Match failed at position {longest}: unexpected character '{test_string[longest]}'" if longest < len(test_string) else "String too short.",
                failed_at=longest,
                partial_matches=[test_string[:longest]]
            )
        return MatchResult(matches=False, reason="No match at all.", failed_at=0, partial_matches=[])
