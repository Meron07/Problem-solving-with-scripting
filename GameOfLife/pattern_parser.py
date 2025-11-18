"""
Pattern parser for loading Game of Life patterns from text files.
"""

import re
import logging
from typing import Dict, List, Tuple
from .exceptions import PatternParseError, FileHandlingError
from .metaprogramming import memoize_pattern

logger = logging.getLogger(__name__)


class PatternParser:
    """Parse pattern files in various formats."""
    
    # Regex patterns for parsing
    COORDINATE_PATTERN = r'\(?\s*(\d+)\s*,\s*(\d+)\s*\)?'
    RLE_PATTERN = r'(\d*)([bo$!])'
    
    @staticmethod
    @memoize_pattern
    def parse(filename: str) -> Dict:
        """
        Parse a pattern file and return pattern data.
        
        Supports multiple formats:
        - Plain text (. for dead, O or * for alive)
        - Coordinate list (row,col or (row,col))
        - RLE format (Run Length Encoded)
        
        Args:
            filename: Path to pattern file
            
        Returns:
            Dictionary with pattern metadata and cell coordinates
            
        Raises:
            FileHandlingError: If file cannot be read
            PatternParseError: If pattern format is invalid
        """
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                content = f.read()
        except FileNotFoundError:
            raise FileHandlingError(f"Pattern file not found: {filename}")
        except Exception as e:
            raise FileHandlingError(f"Error reading pattern file: {e}")
        
        # Try to detect format
        if PatternParser._is_rle_format(content):
            return PatternParser._parse_rle(content, filename)
        elif PatternParser._is_coordinate_format(content):
            return PatternParser._parse_coordinates(content, filename)
        else:
            return PatternParser._parse_plaintext(content, filename)
    
    @staticmethod
    def _is_rle_format(content: str) -> bool:
        """Check if content is in RLE format."""
        return 'x = ' in content.lower() or '#Life' in content
    
    @staticmethod
    def _is_coordinate_format(content: str) -> bool:
        """Check if content is coordinate list format."""
        lines = [line.strip() for line in content.split('\n') if line.strip() and not line.startswith('#')]
        if not lines:
            return False
        # Check if first non-comment line looks like coordinates
        return bool(re.match(PatternParser.COORDINATE_PATTERN, lines[0]))
    
    @staticmethod
    def _parse_plaintext(content: str, filename: str) -> Dict:
        """
        Parse plain text format pattern.
        
        Format: . for dead, O or * for alive
        """
        cells = []
        name = filename
        comments = []
        
        lines = content.split('\n')
        
        for row, line in enumerate(lines):
            line = line.rstrip()
            
            if line.startswith('#'):
                # Comment line
                comment = line[1:].strip()
                if comment.startswith('N '):
                    name = comment[2:].strip()
                else:
                    comments.append(comment)
                continue
            
            for col, char in enumerate(line):
                if char in ('O', '*', '1'):
                    cells.append((row, col))
        
        if not cells:
            raise PatternParseError(f"No alive cells found in pattern: {filename}")
        
        logger.info(f"Parsed plaintext pattern: {name} ({len(cells)} cells)")
        
        return {
            'name': name,
            'cells': cells,
            'comments': comments,
            'format': 'plaintext'
        }
    
    @staticmethod
    def _parse_coordinates(content: str, filename: str) -> Dict:
        """
        Parse coordinate list format.
        
        Format: row,col or (row,col) per line
        """
        cells = []
        name = filename
        comments = []
        
        for line in content.split('\n'):
            line = line.strip()
            
            if not line:
                continue
            
            if line.startswith('#'):
                comment = line[1:].strip()
                if comment.startswith('N '):
                    name = comment[2:].strip()
                else:
                    comments.append(comment)
                continue
            
            match = re.match(PatternParser.COORDINATE_PATTERN, line)
            if match:
                row = int(match.group(1))
                col = int(match.group(2))
                cells.append((row, col))
            else:
                logger.warning(f"Invalid coordinate line: {line}")
        
        if not cells:
            raise PatternParseError(f"No valid coordinates found in pattern: {filename}")
        
        logger.info(f"Parsed coordinate pattern: {name} ({len(cells)} cells)")
        
        return {
            'name': name,
            'cells': cells,
            'comments': comments,
            'format': 'coordinates'
        }
    
    @staticmethod
    def _parse_rle(content: str, filename: str) -> Dict:
        """
        Parse RLE (Run Length Encoded) format.
        
        Format: x = width, y = height, rule = ...
                runcount<tag>...
        """
        cells = []
        name = filename
        comments = []
        
        lines = content.split('\n')
        row = 0
        col = 0
        
        for line in lines:
            line = line.strip()
            
            if line.startswith('#'):
                comment = line[1:].strip()
                if comment.startswith('N '):
                    name = comment[2:].strip()
                else:
                    comments.append(comment)
                continue
            
            if line.startswith('x'):
                # Header line - skip
                continue
            
            if not line:
                continue
            
            # Parse RLE data
            i = 0
            while i < len(line):
                match = re.match(PatternParser.RLE_PATTERN, line[i:])
                if match:
                    count_str = match.group(1)
                    tag = match.group(2)
                    count = int(count_str) if count_str else 1
                    
                    if tag == 'b':
                        # Dead cells
                        col += count
                    elif tag == 'o':
                        # Alive cells
                        for _ in range(count):
                            cells.append((row, col))
                            col += 1
                    elif tag == '$':
                        # End of line
                        row += count
                        col = 0
                    elif tag == '!':
                        # End of pattern
                        break
                    
                    i += len(match.group(0))
                else:
                    i += 1
        
        if not cells:
            raise PatternParseError(f"No alive cells found in RLE pattern: {filename}")
        
        logger.info(f"Parsed RLE pattern: {name} ({len(cells)} cells)")
        
        return {
            'name': name,
            'cells': cells,
            'comments': comments,
            'format': 'rle'
        }
    
    @staticmethod
    def save_pattern(filename: str, board, name: str = None, comments: List[str] = None):
        """
        Save current board state as a pattern file.
        
        Args:
            filename: Output filename
            board: Board object to save
            name: Optional pattern name
            comments: Optional list of comment lines
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                # Write header
                if name:
                    f.write(f"#N {name}\n")
                
                if comments:
                    for comment in comments:
                        f.write(f"# {comment}\n")
                
                f.write(f"# Generation: {board.generation}\n")
                f.write(f"# Alive cells: {board.count_alive()}\n")
                f.write("#\n")
                
                # Write grid
                for row in board.grid:
                    line = ''.join('O' if cell else '.' for cell in row)
                    f.write(line + '\n')
            
            logger.info(f"Saved pattern to {filename}")
            
        except Exception as e:
            raise FileHandlingError(f"Error saving pattern: {e}")