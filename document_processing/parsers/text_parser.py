"""
Text Document Parser
"""
from pathlib import Path
from typing import Dict, Any
import logging

logger = logging.getLogger(__name__)


class TextParser:
    """Parse plain text files"""
    
    @staticmethod
    def parse(file_path: Path) -> Dict[str, Any]:
        """
        Parse text file
        
        Args:
            file_path: Path to text file
            
        Returns:
            Dict with 'content' and 'metadata'
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            word_count = len(content.split())
            char_count = len(content)
            
            return {
                'content': content,
                'metadata': {
                    'word_count': word_count,
                    'character_count': char_count,
                    'encoding': 'utf-8'
                }
            }
            
        except UnicodeDecodeError:
            try:
                with open(file_path, 'r', encoding='latin-1') as f:
                    content = f.read()
                
                word_count = len(content.split())
                char_count = len(content)
                
                return {
                    'content': content,
                    'metadata': {
                        'word_count': word_count,
                        'character_count': char_count,
                        'encoding': 'latin-1'
                    }
                }
            except Exception as e:
                logger.error(f"Error parsing text file with latin-1: {e}")
                raise
                
        except Exception as e:
            logger.error(f"Error parsing text file: {e}")
            raise


class MarkdownParser(TextParser):
    """Parse Markdown files"""
    
    @staticmethod
    def parse(file_path: Path) -> Dict[str, Any]:
        """Parse markdown file"""
        result = TextParser.parse(file_path)
        result['metadata']['format'] = 'markdown'
        return result


class CSVParser:
    """Parse CSV files"""
    
    @staticmethod
    def parse(file_path: Path) -> Dict[str, Any]:
        """Parse CSV file"""
        try:
            import csv
            
            rows = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                
                if headers:
                    rows.append(' | '.join(headers))
                    rows.append('-' * 50)
                
                for row in reader:
                    rows.append(' | '.join(row))
            
            content = '\n'.join(rows)
            
            return {
                'content': content,
                'metadata': {
                    'format': 'csv',
                    'row_count': len(rows) - 2 if headers else len(rows),
                    'column_count': len(headers) if headers else 0
                }
            }
            
        except Exception as e:
            logger.error(f"Error parsing CSV file: {e}")
            raise
