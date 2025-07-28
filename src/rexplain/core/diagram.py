"""
Railroad diagram generation for regex patterns.
"""

from typing import Optional
from io import StringIO
from pyrailroad.elements import Diagram, Sequence, Terminal, NonTerminal
from .parser import Literal, CharClass, Quantifier, Alternation, Anchor, Escape, Group, Sequence as ParserSequence
import sys


def generate_railroad_diagram(pattern: str, output_path: Optional[str] = None) -> str:
    """
    Generate a railroad diagram for a regex pattern.
    
    Args:
        pattern: The regex pattern to visualize
        output_path: Optional path to save the SVG file. If None, returns SVG content.
        
    Returns:
        SVG content as string if output_path is None, otherwise the file path.
    """
    # Use the detailed diagram generator for better results
    return generate_detailed_railroad_diagram(pattern, output_path)


def generate_detailed_railroad_diagram(pattern: str, output_path: Optional[str] = None) -> str:
    """
    Generate a detailed railroad diagram based on parsed regex components.
    
    Args:
        pattern: The regex pattern to visualize
        output_path: Optional path to save the SVG file. If None, returns SVG content.
        
    Returns:
        SVG content as string if output_path is None, otherwise the file path.
    """
    # Import here to avoid circular imports
    from .parser import RegexParser
    
    try:
        # Parse the regex to get AST
        parser = RegexParser()
        ast = parser.parse(pattern)
        
        # Convert AST to railroad diagram components
        diagram_components = _ast_to_railroad(ast)
        
        # Create the diagram
        diagram = Diagram(diagram_components)
        
        if output_path:
            # Write to file
            with open(output_path, 'w') as f:
                diagram.write_standalone(f.write)
            return output_path
        else:
            # Return SVG content as string
            svg_content = StringIO()
            diagram.write_standalone(svg_content.write)
            return svg_content.getvalue()
            
    except Exception as e:
        raise ValueError(f"Failed to generate detailed railroad diagram: {e}")


def _ast_to_railroad(ast_node):
    """
    Convert AST node to railroad diagram component.
    
    Args:
        ast_node: AST node from parser
        
    Returns:
        Railroad diagram component
    """
    # Import all needed elements
    from pyrailroad.elements import (
        Terminal, NonTerminal, Sequence, Choice, 
        OneOrMore, zero_or_more, optional
    )
    
    try:
        # Handle different AST node types
        if isinstance(ast_node, Literal):
            # Handle literal characters
            if ast_node.value in ['^', '$', '@', '.', '*', '+', '?', '|', '(', ')', '[', ']', '{', '}', '\\']:
                return Terminal(ast_node.value)
            else:
                return Terminal(f"'{ast_node.value}'")
        
        elif isinstance(ast_node, CharClass):
            return Terminal(f"[{ast_node.value}]")
        
        elif isinstance(ast_node, Quantifier):
            child = _ast_to_railroad(ast_node.child)
            if ast_node.quant == '*':
                return zero_or_more(child)
            elif ast_node.quant == '+':
                return OneOrMore(child)
            elif ast_node.quant == '?':
                return optional(child)
            else:
                # Handle other quantifiers like {n}, {n,m}, etc.
                return Terminal(f"{child}{ast_node.quant}")
        
        elif isinstance(ast_node, ParserSequence):
            # Convert each element in the sequence
            elements = [_ast_to_railroad(elem) for elem in ast_node.elements]
            if len(elements) == 1:
                return elements[0]
            else:
                return Sequence(*elements)
        
        elif isinstance(ast_node, Alternation):
            alternatives = [_ast_to_railroad(alt) for alt in ast_node.options]
            if len(alternatives) == 1:
                return alternatives[0]
            else:
                return Choice(0, *alternatives)
        
        elif isinstance(ast_node, Anchor):
            return Terminal(ast_node.value)
        
        elif isinstance(ast_node, Escape):
            # Handle escape sequences with meaningful labels
            escape_mapping = {
                '\\w': 'word char',
                '\\d': 'digit',
                '\\s': 'whitespace',
                '\\W': 'non-word char',
                '\\D': 'non-digit',
                '\\S': 'non-whitespace',
                '\\b': 'word boundary',
                '\\B': 'non-word boundary',
                '\\A': 'start of string',
                '\\Z': 'end of string',
                '\\z': 'end of string',
                '\\G': 'end of prev match',
                '\\n': 'newline',
                '\\r': 'carriage return',
                '\\t': 'tab',
                '\\f': 'form feed',
                '\\v': 'vertical tab',
                '\\u': 'unicode char',
                '\\x': 'hex char',
                '\\N': 'named char',
            }
            
            # Check if it's a known escape sequence
            if ast_node.value in escape_mapping:
                return Terminal(escape_mapping[ast_node.value])
            else:
                # For unknown escape sequences, show the raw value
                return Terminal(ast_node.value)
        
        elif isinstance(ast_node, Group):
            # Handle groups - for now, just show the group type
            if ast_node.children:
                children = [_ast_to_railroad(child) for child in ast_node.children]
                if len(children) == 1:
                    return children[0]
                else:
                    return Sequence(*children)
            else:
                # Empty group
                if ast_node.group_type == 'GROUP_NONCAP':
                    return Terminal('(?:)')
                elif ast_node.group_type == 'GROUP_NAMED':
                    return Terminal(f'(?P<{ast_node.name}>)')
                elif ast_node.group_type == 'GROUP_LOOKAHEAD':
                    return Terminal('(?=)')
                elif ast_node.group_type == 'GROUP_NEG_LOOKAHEAD':
                    return Terminal('(?!)')
                elif ast_node.group_type == 'GROUP_LOOKBEHIND':
                    return Terminal('(?<=)')
                elif ast_node.group_type == 'GROUP_NEG_LOOKBEHIND':
                    return Terminal('(?<!)')
                else:
                    return Terminal('()')
        
        else:
            # Fallback for unknown types
            return Terminal(str(ast_node))
    
    except Exception as e:
        return Terminal(str(ast_node)) 