import re

def flesch_kincaid_grade_level(text: str) -> dict:
    """
    Calculate Flesch-Kincaid Grade Level for readability.
    Returns a dict with value, label, and status (good/poor).
    """
    words = len(text.split())
    sentences = text.count('.') + text.count('!') + text.count('?') + 1  # +1 to avoid division by zero
    syllables = sum([len(re.findall(r'[aeiouy]+', word.lower())) for word in text.split()])
    if sentences == 0 or words == 0:
        return {"value": 0.0, "label": "Readability Grade", "status": "neutral"}
    grade = 0.39 * (words / sentences) + 11.8 * (syllables / words) - 15.59
    grade = max(0, grade)
    status = "good" if grade < 8 else "poor"
    return {"value": grade, "label": "Readability Grade", "status": status}

def cyclomatic_complexity(code: str) -> dict:
    """
    Simple estimate of cyclomatic complexity based on keywords.
    Returns a dict with value, label, and status (good/poor).
    """
    keywords = ['if', 'for', 'while', 'elif', 'case', 'catch', '&&', '||']
    value = sum(code.lower().count(keyword) for keyword in keywords) + 1
    status = "good" if value <= 10 else "poor"
    return {"value": value, "label": "Cyclomatic Complexity", "status": status}

def calculate_maintainability_index(code: str, code_lines: int, comment_lines: int) -> dict:
    """
    Calculate a simple maintainability index.
    Returns a dict with value, label, and status (good/poor).
    """
    if code_lines == 0:
        value = 100.0
    else:
        comment_density = comment_lines / code_lines
        complexity_factor = cyclomatic_complexity(code)['value'] / 10
        value = 100 - (len(code) / 100) + (comment_density * 50) - complexity_factor
        value = max(0, min(100, value))
    status = "good" if value > 50 else "poor"
    return {"value": value, "label": "Maintainability Index", "status": status}

def lines_of_code(code: str) -> dict:
    """
    Count the number of lines of code, excluding empty lines.
    Returns a dict with value, label, and status (good/poor).
    """
    lines = code.split('\n')
    value = len([line for line in lines if line.strip()])
    status = "good" if value < 100 else "poor"
    return {"value": value, "label": "Lines of Code", "status": status}

def comment_lines(code: str) -> int:
    """
    Estimate the number of comment lines.
    """
    lines = code.split('\n')
    comment_count = 0
    for line in lines:
        stripped = line.strip()
        if stripped.startswith('#') or stripped.startswith('//') or stripped.startswith('/*'):
            comment_count += 1
    return comment_count

def detect_code_smells(code: str) -> list:
    """
    Simple detection of common code smells.
    """
    smells = []
    if len(code) > 1000:
        smells.append("Long method/function - consider breaking into smaller functions")
    if cyclomatic_complexity(code)['value'] > 10:
        smells.append("High cyclomatic complexity - consider simplifying logic")
    if 'print(' in code and 'debug' not in code.lower():
        smells.append("Debug print statements left in code")
    if 'TODO' in code.upper():
        smells.append("TODO comments present - unfinished work")
    return smells

def halstead_metrics(code: str) -> dict:
    """
    Calculate basic Halstead complexity metrics.
    """
    # Simple tokenization
    tokens = re.findall(r'\b\w+\b', code.lower())
    unique_operators = set(re.findall(r'[+\-*/=<>!&|%]', code))
    unique_operands = set(tokens) - unique_operators
    n1 = len(unique_operators)
    n2 = len(unique_operands)
    N1 = sum(1 for op in unique_operators for char in code if char in op)
    N2 = len(tokens) - N1
    if n1 + n2 == 0:
        return {"vocabulary": 0, "length": 0, "volume": 0, "difficulty": 0, "effort": 0}
    vocabulary = n1 + n2
    length = N1 + N2
    volume = length * (vocabulary ** 0.5) if vocabulary > 0 else 0
    difficulty = (n1 / 2) * (N2 / n2) if n2 > 0 else 0
    effort = difficulty * volume
    return {
        "vocabulary": vocabulary,
        "length": length,
        "volume": volume,
        "difficulty": difficulty,
        "effort": effort
    }

# Add more utility functions as needed for code analysis
