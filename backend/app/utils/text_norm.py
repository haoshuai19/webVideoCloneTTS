"""Simple text normalization for TTS."""
import re


def normalize_text(text: str) -> str:
    """Normalize Chinese text for TTS."""
    # Remove extra whitespace
    text = re.sub(r'\s+', ' ', text.strip())
    
    # Common number conversions
    number_map = {
        '０': '0', '１': '1', '２': '2', '３': '3', '４': '4',
        '５': '5', '６': '6', '７': '7', '８': '8', '９': '9',
    }
    for full, half in number_map.items():
        text = text.replace(full, half)
    
    # Ensure sentence ends with proper punctuation
    if text and text[-1] not in '。！？.!?\n':
        text += '。'
    
    return text
