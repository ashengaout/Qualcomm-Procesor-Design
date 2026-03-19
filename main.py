""""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
"""

from Hardware.data_system import DataSystem
from Hardware.truth_table import get_num_vars, get_truth_table
from Hardware.boolean_logic import display_canonical
from Hardware.Kmap import display_kmap, simplify_kmap
from Hardware.logic_check import validate


def get_form_choice() -> str:
    """Prompt user to select SOP or POS."""
    while True:
        choice = input("Select canonical form — enter SOP or POS: ").strip().upper()
        if choice in ("SOP", "POS"):
            return choice
        print("  Error: please enter SOP or POS.")


def run_task2():
    print("=" * 55)
    print("  CSC 6210 — Task 2: Truth Table → K-Map Simplification")
    print("=" * 55)

    # ── Section 1: Input ──────────────────────────────────────
    n = get_num_vars()
    tt = get_truth_table(n)

    # ── Display truth table ───────────────────────────────────
    tt.display()

    # ── Section 2: Canonical equation ────────────────────────
    form = get_form_choice()
    display_canonical(tt, form)

    # ── Section 2: K-Map + simplification ────────────────────
    if n <= 4:
        display_kmap(tt)
        simplified, groups = simplify_kmap(tt)

        print("--- K-Map Groups (Greedy) ---")
        if groups:
            for group, term in groups:
                print(f"  Group {sorted(group)} → term: {term}")
        else:
            print("  (no grouping needed — function is trivially 0 or 1)")

        print(f"\n--- Simplified Boolean Expression ---")
        print(f"  {simplified}")
    else:
        # For n > 4 the assignment only requires canonical form
        simplified = None
        print("\n(K-Map simplification not performed for n > 4 variables.)")

    # ── Section 3: Validation ─────────────────────────────────
    if simplified is not None:
        validate(tt, simplified)

    print("\nDone.")


def run_task1():
    data_system = DataSystem()

    #user input for testing data system
    print("---Qualcomm IoT Reference Architecture: Task 1---")

    while True:
        try:
            user_input = input("Enter a signed integer value (or 'q' to quit): ")

            if user_input == 'q':
                print("Quitting...")
                break

            user_format = input("Select output format (DEC, HEX, BIN): ").upper()

            result, overflow, saturation = data_system.process_input(int(user_input), user_format)

            print("\n---Processor Output---")
            print(f"Formatted Value: {result}")
            print(f"Overflow: {overflow}")
            print(f"Saturation: {saturation}")
            print("-------------------------")

        except ValueError:
            print("Invalid input: please enter a signed integer value.")
        except Exception as exception:
            print(exception)

if __name__ == "__main__":
    choice = input("Run Task 1 (data system) or Task 2 (K-Map)? Enter 1 or 2: ")
    if choice == "1":
        run_task1()
    elif choice == "2":
        run_task2()