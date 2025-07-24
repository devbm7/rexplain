__version__ = "0.2.2"

from .core.explainer import RegexExplainer
from .core.generator import ExampleGenerator
from .core.tester import RegexTester

def explain(pattern: str, flags: int = 0) -> str:
    """
    Explain what a regex pattern does, line by line.

    Args:
        pattern (str): The regex pattern to explain.
        flags (int, optional): Regex flags (e.g., re.IGNORECASE). Defaults to 0.

    Returns:
        str: A line-by-line explanation of the regex pattern.

    Example:
        >>> explain(r"^\w+$")
        '^ - asserts position at the start of a line\n\w+ - matches a word character one or more times (greedy)\n$ - asserts position at the end of a line'
    """
    return RegexExplainer().explain(pattern, flags=flags)


def examples(pattern: str, count: int = 3, flags: int = 0):
    """
    Generate example strings that match the regex pattern.

    Args:
        pattern (str): The regex pattern.
        count (int, optional): Number of examples to generate. Defaults to 3.
        flags (int, optional): Regex flags (e.g., re.IGNORECASE). Defaults to 0.

    Returns:
        List[str]: Example strings matching the pattern.

    Example:
        >>> examples(r"[A-Z]{2}\d{2}", count=2)
        ['AB12', 'XY34']
    """
    return ExampleGenerator().generate(pattern, count, flags=flags)


def test(pattern: str, test_string: str, flags: int = 0):
    """
    Test if a string matches a regex pattern and explain why/why not.

    Args:
        pattern (str): The regex pattern.
        test_string (str): The string to test.
        flags (int, optional): Regex flags (e.g., re.IGNORECASE). Defaults to 0.

    Returns:
        MatchResult: Result object with match status and explanation.

    Example:
        >>> test(r"foo.*", "foobar")
        MatchResult(matches=True, reason='Full match.', ...)
    """
    result = RegexTester().test(pattern, test_string, flags=flags)
    return result