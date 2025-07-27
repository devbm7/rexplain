"""
Railroad diagram generation for regex patterns.
"""

from typing import Optional
from io import StringIO
from pyrailroad.elements import Diagram, Sequence, Terminal, NonTerminal
from .parser import Literal, CharClass, Quantifier, Alternation, Anchor, Escape, Group


def generate_railroad_diagram(pattern: str, output_path: Optional[str] = None) -> str:
    """
    Generate a railroad diagram for a regex pattern.
    
    Args:
        pattern: The regex pattern to visualize
        output_path: Optional path to save the SVG file. If None, returns SVG content.
        
    Returns:
        SVG content as string if output_path is None, otherwise the file path.
    """
    try:
        # Import all needed elements
        from pyrailroad.elements import (
            Diagram, Sequence, Terminal, NonTerminal, 
            OneOrMore, zero_or_more, optional, Choice
        )
        
        # Create a simple but meaningful diagram based on the pattern
        # This is a basic implementation that handles common regex patterns
        components = []
        
        # Handle start anchor
        if pattern.startswith('^'):
            components.append(Terminal('^'))
            pattern = pattern[1:]
        
        # Handle end anchor
        has_end_anchor = False
        if pattern.endswith('$'):
            has_end_anchor = True
            pattern = pattern[:-1]
        
        # Parse the main pattern
        if pattern:
            # Handle common patterns
            if pattern == r'\w+':
                components.append(OneOrMore(Terminal('word char')))
            elif pattern == r'\d+':
                components.append(OneOrMore(Terminal('digit')))
            elif pattern == r'\s+':
                components.append(OneOrMore(Terminal('whitespace')))
            elif pattern == r'.*':
                components.append(zero_or_more(Terminal('any char')))
            elif pattern == r'.+':
                components.append(OneOrMore(Terminal('any char')))
            elif pattern == r'\w*':
                components.append(zero_or_more(Terminal('word char')))
            elif pattern == r'\d*':
                components.append(zero_or_more(Terminal('digit')))
            elif pattern == r'\s*':
                components.append(zero_or_more(Terminal('whitespace')))
            elif pattern == r'\w?':
                components.append(optional(Terminal('word char')))
            elif pattern == r'\d?':
                components.append(optional(Terminal('digit')))
            elif pattern == r'\s?':
                components.append(optional(Terminal('whitespace')))
            elif pattern == r'\w':
                components.append(Terminal('word char'))
            elif pattern == r'\d':
                components.append(Terminal('digit'))
            elif pattern == r'\s':
                components.append(Terminal('whitespace'))
            elif pattern == r'\W':
                components.append(Terminal('non-word char'))
            elif pattern == r'\D':
                components.append(Terminal('non-digit'))
            elif pattern == r'\S':
                components.append(Terminal('non-whitespace'))
            elif pattern == r'\b':
                components.append(Terminal('word boundary'))
            elif pattern == r'\B':
                components.append(Terminal('non-word boundary'))
            elif pattern == r'\A':
                components.append(Terminal('start of string'))
            elif pattern == r'\Z':
                components.append(Terminal('end of string'))
            elif pattern == r'\z':
                components.append(Terminal('end of string'))
            elif pattern == r'\G':
                components.append(Terminal('end of prev match'))
            elif pattern == r'\n':
                components.append(Terminal('newline'))
            elif pattern == r'\r':
                components.append(Terminal('carriage return'))
            elif pattern == r'\t':
                components.append(Terminal('tab'))
            elif pattern == r'\f':
                components.append(Terminal('form feed'))
            elif pattern == r'\v':
                components.append(Terminal('vertical tab'))
            elif pattern == r'\.':
                components.append(Terminal('.'))
            elif pattern == r'\*':
                components.append(Terminal('*'))
            elif pattern == r'\+':
                components.append(Terminal('+'))
            elif pattern == r'\?':
                components.append(Terminal('?'))
            elif pattern == r'\|':
                components.append(Terminal('|'))
            elif pattern == r'\(':
                components.append(Terminal('('))
            elif pattern == r'\)':
                components.append(Terminal(')'))
            elif pattern == r'\[':
                components.append(Terminal('['))
            elif pattern == r'\]':
                components.append(Terminal(']'))
            elif pattern == r'\{':
                components.append(Terminal('{'))
            elif pattern == r'\}':
                components.append(Terminal('}'))
            elif pattern == r'\^':
                components.append(Terminal('^'))
            elif pattern == r'\$':
                components.append(Terminal('$'))
            elif pattern == r'\\':
                components.append(Terminal('\\'))
            else:
                # For other patterns, try to create a meaningful representation
                if len(pattern) == 1:
                    components.append(Terminal(f"'{pattern}'"))
                else:
                    # For complex patterns, create a better representation
                    # Handle common email-like patterns more intelligently
                    if '@' in pattern and '.' in pattern:
                        # Special handling for email-like patterns
                        parts = pattern.split('@')
                        if len(parts) == 2:
                            # Handle local part
                            if parts[0] == r'\w+':
                                components.append(OneOrMore(Terminal('word char')))
                            elif parts[0] == r'\w*':
                                components.append(zero_or_more(Terminal('word char')))
                            else:
                                components.append(Terminal(parts[0]))
                            
                            # Add @ symbol
                            components.append(Terminal('@'))
                            
                            # Handle domain part
                            domain_parts = parts[1].split('.')
                            for i, part in enumerate(domain_parts):
                                if i > 0:
                                    components.append(Terminal('.'))
                                if part == r'\w+':
                                    components.append(OneOrMore(Terminal('word char')))
                                elif part == r'\w*':
                                    components.append(zero_or_more(Terminal('word char')))
                                else:
                                    components.append(Terminal(part))
                    else:
                        # General pattern parsing with improved escape sequence handling
                        import re
                        
                        # First, let's properly handle escape sequences
                        # Split the pattern while preserving escape sequences
                        i = 0
                        current_component = None
                        current_quantifier = None
                        
                        while i < len(pattern):
                            char = pattern[i]
                            
                            if char == '\\' and i + 1 < len(pattern):
                                # Handle escape sequences
                                if current_component:
                                    components.append(current_component)
                                    current_component = None
                                
                                next_char = pattern[i + 1]
                                if next_char == 'w':
                                    current_component = Terminal('word char')
                                elif next_char == 'd':
                                    current_component = Terminal('digit')
                                elif next_char == 's':
                                    current_component = Terminal('whitespace')
                                elif next_char == 'W':
                                    current_component = Terminal('non-word char')
                                elif next_char == 'D':
                                    current_component = Terminal('non-digit')
                                elif next_char == 'S':
                                    current_component = Terminal('non-whitespace')
                                elif next_char == 'b':
                                    current_component = Terminal('word boundary')
                                elif next_char == 'B':
                                    current_component = Terminal('non-word boundary')
                                elif next_char == '.':
                                    current_component = Terminal('.')
                                elif next_char == '*':
                                    current_component = Terminal('*')
                                elif next_char == '+':
                                    current_component = Terminal('+')
                                elif next_char == '?':
                                    current_component = Terminal('?')
                                elif next_char == '|':
                                    current_component = Terminal('|')
                                elif next_char == '(':
                                    current_component = Terminal('(')
                                elif next_char == ')':
                                    current_component = Terminal(')')
                                elif next_char == '[':
                                    current_component = Terminal('[')
                                elif next_char == ']':
                                    current_component = Terminal(']')
                                elif next_char == '{':
                                    current_component = Terminal('{')
                                elif next_char == '}':
                                    current_component = Terminal('}')
                                elif next_char == '^':
                                    current_component = Terminal('^')
                                elif next_char == '$':
                                    current_component = Terminal('$')
                                elif next_char == '\\':
                                    current_component = Terminal('\\')
                                else:
                                    # Unknown escape sequence, treat as literal
                                    current_component = Terminal(f"\\{next_char}")
                                
                                i += 2  # Skip both backslash and next character
                                
                            elif char in ['*', '+', '?']:
                                # Handle quantifiers
                                if current_component:
                                    if char == '*':
                                        current_component = zero_or_more(current_component)
                                    elif char == '+':
                                        current_component = OneOrMore(current_component)
                                    elif char == '?':
                                        current_component = optional(current_component)
                                    components.append(current_component)
                                    current_component = None
                                i += 1
                                
                            elif char in ['|', '(', ')', '[', ']', '{', '}', '@', '.']:
                                # Handle special characters
                                if current_component:
                                    components.append(current_component)
                                    current_component = None
                                components.append(Terminal(char))
                                i += 1
                                
                            else:
                                # Handle literal characters
                                if current_component:
                                    components.append(current_component)
                                    current_component = None
                                current_component = Terminal(f"'{char}'")
                                i += 1
                        
                        # Add any remaining component
                        if current_component:
                            components.append(current_component)
        
        # Handle end anchor
        if has_end_anchor:
            components.append(Terminal('$'))
        
        # Create the diagram
        if len(components) == 1:
            diagram = Diagram(components[0])
        else:
            diagram = Diagram(Sequence(*components))
        
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
        raise ValueError(f"Failed to generate railroad diagram: {e}")


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
    
    # Handle different AST node types
    if isinstance(ast_node, Literal):
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
            return Terminal(f"{child}{ast_node.quant}")
    elif isinstance(ast_node, Sequence):
        elements = [_ast_to_railroad(elem) for elem in ast_node.elements]
        return Sequence(*elements)
    elif isinstance(ast_node, Alternation):
        alternatives = [_ast_to_railroad(alt) for alt in ast_node.options]
        return Choice(0, *alternatives)
    elif isinstance(ast_node, Anchor):
        return Terminal(ast_node.value)
    elif isinstance(ast_node, Escape):
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
            return Terminal("()")
    else:
        # Fallback for unknown types
        return Terminal(str(ast_node)) 