"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Hardware/kmap.py — K-Map construction, greedy grouping, and simplification (2–4 variables)
"""

from itertools import combinations
from Hardware.truth_table import TruthTable

GRAY_2 = [0, 1]  # 1-bit axis  (2-var map: 2x2)
GRAY_4 = [0, 1, 3, 2]  # 2-bit axis  (3-var map: 2x4, 4-var map: 4x4)


def _axes(n: int):
    if n == 2:
        return GRAY_2, GRAY_2  # 2 rows × 2 cols
    elif n == 3:
        return GRAY_2, GRAY_4  # 2 rows × 4 cols
    elif n == 4:
        return GRAY_4, GRAY_4  # 4 rows × 4 cols
    else:
        raise ValueError("K-Map only supported for 2–4 variables.")


def cell_minterm(row_code: int, col_code: int, n: int) -> int:
    if n == 2:
        return (row_code << 1) | col_code
    elif n == 3:
        return (row_code << 2) | col_code
    elif n == 4:
        return (row_code << 2) | col_code


# -----Display Functions------------------------------------

def _var_labels(n: int) -> tuple[str, str]:
    """Return (row_label, col_label) for the K-Map header."""
    if n == 2:
        return "A", "B"
    elif n == 3:
        return "A", "BC"
    elif n == 4:
        return "AB", "CD"


def display_kmap(tt: TruthTable):
    n = tt.n
    if n > 4:
        print("K-Map display not supported for n > 4.")
        return

    rows, cols = _axes(n)
    row_label, col_label = _var_labels(n)

    label_pad = max(len(row_label), 2)
    print("\n--- K-Map ---")
    print(f"{'':>{label_pad}} \\ {col_label}")
    print(f"{'':>{label_pad}}   " + "  ".join(
        format(c, f'0{n - (1 if n == 3 else 2)}b') if n >= 3 else str(c)
        for c in cols
    ))
    divider = f"{'':>{label_pad}}  +" + ("----" * len(cols)) + "-"
    print(divider)

    for r in rows:
        row_label_str = format(r, f'0{1 if n <= 3 else 2}b')
        cells = [f" {tt.outputs[cell_minterm(r, c, n)]} " for c in cols]
        print(f"{row_label_str:>{label_pad}}  |" + "|".join(cells) + "|")

    print(divider)
    print()


# ---Greedy Grouping----------------------------

def _is_power_of_two(x: int) -> bool:
    return x > 0 and (x & (x - 1)) == 0


"""
    A valid K-Map group must be a power-of-two size AND all cells must
    differ by exactly the bits that are 'don't care' (i.e., form a
    hypercube in the n-dimensional Boolean space).
    """


def is_valid(minterms_in_group: list[int], n: int) -> bool:
    size = len(minterms_in_group)
    if not _is_power_of_two(size):
        return False

    # XOR every pair — all differences must be covered by a single mask
    xor_acc = 0
    for a, b in combinations(minterms_in_group, 2):
        xor_acc |= (a ^ b)

    # xor_accumulate must itself be a power-of-two - 1  (i.e. 0b0..01..1)
    mask = xor_acc
    if mask == 0 and size == 1:
        return True

    if not _is_power_of_two(mask + 1):
        return False

    # Verify every minterm in the group is reachable via the mask from the first
    base = minterms_in_group[0]
    exp = set()
    for combo in range(mask + 1):
        if (combo & ~mask) == 0:
            exp.add(base | combo)
    return set(minterms_in_group) == exp


# Derive the simplified product term that represents a group of minterms.
def prod_term_from_group(group: list[int], var_names: list[str]) -> str:
    n = len(var_names)
    xor_mask = 0
    for a, b in combinations(group, 2):
        xor_mask |= (a ^ b)

    base = group[0]
    term_parts = []
    for i, var in enumerate(var_names):
        bit_pos = n - 1 - i
        if (xor_mask >> bit_pos) & 1:
            continue  # variable eliminated
        term_parts.append(var if (base >> bit_pos) & 1 else f"{var}'")

    return "".join(term_parts) if term_parts else "1"

# Derive simplified sum term that represents a group of maxterms
def sum_term_from_group(group: list[int], var_names: list[str]) -> str:
    n = len(var_names)
    xor_mask = 0
    for a, b in combinations(group, 2):
        xor_mask |= (a ^ b)

    base = group[0]
    literals = []
    for i, var in enumerate(var_names):
        bit_pos = n - 1 - i
        if (xor_mask >> bit_pos) & 1:
            continue  # variable eliminated
        # POS: 0-bit → uncomplimented, 1-bit → complemented
        literals.append(var if not (base >> bit_pos) & 1 else f"{var}'")

    return "(" + " + ".join(literals) + ")" if literals else "0"

def greedy_cover(targets: list[int], n: int) -> list[list[int]]:
    candidates = []
    for size in [8, 4, 2, 1]:
        if size > len(targets):
            continue
        for group in combinations(targets, size):
            group = list(group)
            if is_valid(group, n):
                candidates.append(group)

    candidates.sort(key=lambda g: (-len(g), g[0]))

    covered = set()
    groups_used = []
    for group in candidates:
        if any(m not in covered for m in group):
            groups_used.append(group)
            covered.update(group)
        if covered == set(targets):
            break

    return groups_used


"""
    Greedy K-Map simplification for 2–4 variables (SOP).

    Strategy:
      1. Generate all valid groups (powers of 2, hypercube-shaped).
      2. Sort largest-first (prefer bigger groups = fewer literals).
      3. Greedily pick groups that cover at least one uncovered minterm.
      4. Return simplified expression + list of (group, term) pairs for display.

    Returns:
        simplified_expr : string like "F = AC' + B"
        groups_used     : list of (minterm_list, term_string)
    """

def simplify_kmap(tt:TruthTable, form: str = "SOP") -> tuple[str, list[tuple[list[int], str]]]:
    form = form.upper()

    if form == "SOP":
        targets = tt.minterms
        if not targets:
            return "F = 0", []
        if len(targets) == 2 ** tt.n:
            return "F = 1", []
        groups = greedy_cover(targets, tt.n)
        terms = [prod_term_from_group(g, tt.var_names) for g in groups]
        expr = "F = " + " + ".join(terms)
        return expr, list(zip(groups, terms))

    else:  # POS
        targets = tt.maxterms
        if not targets:
            return "F = 1", []
        if len(targets) == 2 ** tt.n:
            return "F = 0", []
        groups = greedy_cover(targets, tt.n)
        terms = [sum_term_from_group(g, tt.var_names) for g in groups]
        expr = "F = " + " * ".join(terms)
        return expr, list(zip(groups, terms))
