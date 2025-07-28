__version__ = "0.3.3"

from .core.explainer import RegexExplainer
from .core.generator import ExampleGenerator
from .core.tester import RegexTester
from .core.diagram import generate_railroad_diagram, generate_detailed_railroad_diagram

def explain(pattern: str, flags: int = 0) -> str:
    r"""
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
    r"""
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
    r"""
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


def diagram(pattern: str, output_path: str = None, detailed: bool = False) -> str:
    r"""
    Generate a railroad diagram for a regex pattern.

    Args:
        pattern (str): The regex pattern to visualize.
        output_path (str, optional): Path to save the SVG file. If None, returns SVG content.
        detailed (bool, optional): Whether to generate a detailed diagram based on parsed components. Defaults to False.

    Returns:
        str: SVG content as string if output_path is None, otherwise the file path.

    Example:
        >>> diagram(r"^\w+$", "diagram.svg")
        'diagram.svg'
        >>> svg_content = diagram(r"^\w+$")
        >>> print(svg_content[:100])
        '<svg xmlns="http://www.w3.org/2000/svg" ...'
    """
    if detailed:
        return generate_detailed_railroad_diagram(pattern, output_path)
    else:
        return generate_railroad_diagram(pattern, output_path)