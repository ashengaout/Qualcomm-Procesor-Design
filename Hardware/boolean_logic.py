"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Hardware/boolean_logic.py — Canonical SOP / POS generation
"""

from Hardware.truth_table import TruthTable

#returns single product term for given minterm index
def minterm_prod(minterm_inx: int, var_names: list[str]) -> str:
    n = len(var_names)
    bits = format(minterm_inx, f'0{n}b')
    term = ""
    for var, bit in zip(var_names, bits):
        term += var if bit == '1' else f"{var}'"
    return term

#returns a single sum term for given maxterm index
def maxterm_sum(maxterm_inx: int, var_names: list[str]) -> str:
    n = len(var_names)
    bits = format(maxterm_inx, f'0{n}b')
    literals = []
    for var, bit in zip(var_names, bits):
        literals.append(var if bit == '0' else f"{var}'")
    return "(" + " + ".join(literals) + ")"


def generate_sop(tt: TruthTable) -> str:
    if not tt.minterms:
        return "F = 0"
    terms = [minterm_prod(m, tt.var_names) for m in tt.minterms]
    return "F = " + " + ".join(terms)

def generate_pos(tt: TruthTable) -> str:
    if not tt.maxterms:
        return "F = 1"
    terms = [maxterm_sum(m, tt.var_names) for m in tt.maxterms]
    return "F = " + " * ".join(terms)


def display_canonical(tt: TruthTable, form: str):
    form = form.upper()
    print(f"\n--- Canonical {form} Expression ---")
    if form == "SOP":
        print(generate_sop(tt))
        print(f"Minterms: m({', '.join(str(m) for m in tt.minterms)})")
    else:
        print(generate_pos(tt))
        print(f"Maxterms: M({', '.join(str(m) for m in tt.maxterms)})")
    print()


