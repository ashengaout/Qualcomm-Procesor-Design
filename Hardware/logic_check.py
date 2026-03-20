"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Hardware/logic_check.py — Re-evaluate simplified expression and compare with truth table
"""

from Hardware.truth_table import TruthTable

"""
    Evaluate a single literal like "A" or "B'".
    Returns the literal's value (0 or 1) given the variable assignment.
    """

def eval_literal(literal: str, assignment: dict[str, int]) -> int:
    var = literal[0]
    complemented = len(literal) > 1 and literal[1] =="'"
    val = assignment[var]
    return (1 - val) if complemented else val

"""
    Evaluate the RHS of a SOP expression (e.g. "AC' + B").
    OR across all product terms — returns 1 if any term is fully satisfied.
    """
def eval_sop(rhs: str, assignment: dict[str, int]) -> int:
    for product_term in rhs.split("+"):
        product_term = product_term.strip()
        literals = []
        i = 0
        while i < len(product_term):
            if i + 1 < len(product_term) and product_term[i + 1] == "'":
                literals.append(product_term[i:i + 2])
                i += 2
            else:
                literals.append(product_term[i])
                i += 1
        if all(eval_literal(lit, assignment) == 1 for lit in literals):
            return 1
    return 0

"""
    Evaluate the RHS of a POS expression (e.g. "(A + B') · (A' + B)").
    AND across all sum terms — returns 0 if any term is unsatisfied.
    """

def eval_pos(rhs: str, assignment: dict[str, int]) -> int:
    for sum_term in rhs.split("*"):
        sum_term = sum_term.strip().strip("()")
        literals = [lit.strip() for lit in sum_term.split("+")]
        if not any(eval_literal(lit, assignment) == 1 for lit in literals):
            return 0
    return 1

"""
    Parse and evaluate a full Boolean expression (e.g. "F = AC' + B").
    Auto-detects SOP vs POS from the RHS format.
    """
def evaluate(exp: str, assignment: dict[str, int]) -> int:
    rhs = exp.split("=", 1)[1].strip()
    if rhs == "0":
        return 0
    if rhs == "1":
        return 1
    if "*" in rhs or rhs.startswith("("):
        return eval_pos(rhs, assignment)
    return eval_sop(rhs, assignment)

"""
    Validate a Boolean expression against a truth table.
    Evaluates the expression for every input combination and compares
    against the original output. Prints a comparison table and returns
    True (PASS) or False (FAIL).
    """

def validate(tt: TruthTable, exp: str) -> bool:
    n = tt.n
    mismatches = []

    print("\n--- Validation ---")
    header = " | ".join(tt.var_names) + " | F(orig) | F(simplified)"
    print(header)
    print("-" * len(header))

    for i, expected in enumerate(tt.outputs):
        bits = format(i, f'0{n}b')
        assignment = {tt.var_names[j]: int(bits[j]) for j in range(n)}
        computed = evaluate(exp, assignment)
        print(" | ".join(bits) + f" |    {expected}    |      {computed}")
        if computed != expected:
            mismatches.append(i)

    print()
    if mismatches:
        print(f"RESULT: *** FAIL *** — mismatch at rows: {mismatches}")
        return False
    print("RESULT: PASS — simplified expression matches truth table for all inputs.")
    return True
