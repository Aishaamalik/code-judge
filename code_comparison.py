import difflib
from main import create_analysis_chain
from utils import (
    flesch_kincaid_grade_level, cyclomatic_complexity, calculate_maintainability_index,
    lines_of_code, comment_lines, detect_code_smells, halstead_metrics,
    nesting_depth, function_count, variable_count, code_duplication_percentage
)

def compare_codes(code1: str, code2: str):
    """
    Compare two code snippets: generate diff, analyze both, and compare metrics.
    Returns a dict with diff, analysis1, analysis2, metrics1, metrics2, comparison.
    """
    chain = create_analysis_chain()

    # Generate unified diff
    diff = difflib.unified_diff(
        code1.splitlines(keepends=True),
        code2.splitlines(keepends=True),
        fromfile='Code 1',
        tofile='Code 2',
        lineterm=''
    )
    diff_text = ''.join(diff)

    # Analyze both codes
    analysis1 = chain.invoke({"code": code1}).content
    analysis2 = chain.invoke({"code": code2}).content

    # Calculate metrics for both
    loc1 = lines_of_code(code1)
    loc2 = lines_of_code(code2)
    cc1 = cyclomatic_complexity(code1)
    cc2 = cyclomatic_complexity(code2)
    mi1 = calculate_maintainability_index(code1, loc1['value'], comment_lines(code1))
    mi2 = calculate_maintainability_index(code2, loc2['value'], comment_lines(code2))
    fk1 = flesch_kincaid_grade_level(code1)
    fk2 = flesch_kincaid_grade_level(code2)
    nd1 = nesting_depth(code1)
    nd2 = nesting_depth(code2)
    fc1 = function_count(code1)
    fc2 = function_count(code2)
    vc1 = variable_count(code1)
    vc2 = variable_count(code2)
    dup1 = code_duplication_percentage(code1)
    dup2 = code_duplication_percentage(code2)

    metrics1 = {
        "loc": loc1, "cc": cc1, "mi": mi1, "fk": fk1,
        "nd": nd1, "fc": fc1, "vc": vc1, "dup": dup1
    }
    metrics2 = {
        "loc": loc2, "cc": cc2, "mi": mi2, "fk": fk2,
        "nd": nd2, "fc": fc2, "vc": vc2, "dup": dup2
    }

    # Simple comparison
    comparison = {}
    for key in metrics1:
        val1 = metrics1[key]['value']
        val2 = metrics2[key]['value']
        if val1 > val2:
            comparison[key] = "Code 1 higher"
        elif val1 < val2:
            comparison[key] = "Code 2 higher"
        else:
            comparison[key] = "Equal"

    return {
        "diff": diff_text,
        "analysis1": analysis1,
        "analysis2": analysis2,
        "metrics1": metrics1,
        "metrics2": metrics2,
        "comparison": comparison
    }
