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
        m = prog.match(test_string)
        if m:
            i = m.end()
            return MatchResult(
                matches=False,
                reason=f"Match failed at position {i}: unexpected character '{test_string[i]}'" if i < len(test_string) else "String too short.",
                failed_at=i,
                partial_matches=[test_string[:i]]
            )
        return MatchResult(matches=False, reason="No match at all.", failed_at=0, partial_matches=[])
