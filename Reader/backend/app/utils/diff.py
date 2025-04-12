from typing import List
import difflib

def generate_diff(text1: str, text2: str) -> List[str]:
    """
    Generate a diff between two text versions.
    Returns a list of diff lines with markers for additions and deletions.
    """
    differ = difflib.Differ()
    diff = list(differ.compare(
        text1.splitlines(),
        text2.splitlines()
    ))
    
    # Format the diff lines
    formatted_diff = []
    for line in diff:
        if line.startswith('+ '):
            formatted_diff.append(f"<span class='addition'>{line[2:]}</span>")
        elif line.startswith('- '):
            formatted_diff.append(f"<span class='deletion'>{line[2:]}</span>")
        elif line.startswith('? '):
            continue  # Skip the ? lines that show character differences
        else:
            formatted_diff.append(line[2:])
            
    return formatted_diff 