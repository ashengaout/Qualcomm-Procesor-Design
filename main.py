""""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
"""

from Hardware.data_system import DataSystem
from Hardware.truth_table import get_num_vars, get_truth_table
from Hardware.boolean_logic import display_canonical, generate_sop, generate_pos
from Hardware.Kmap import display_kmap, simplify_kmap
from Hardware.logic_check import validate
from Hardware.memory_hierarchy import MemoryHierarchy


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
        simplified, groups = simplify_kmap(tt, form)

        print("--- K-Map Groups (Greedy) ---")
        if groups:
            for group, term in groups:
                print(f"  Group {sorted(group)} → term: {term}")
        else:
            print("  (no grouping needed — function is trivially 0 or 1)")

        print(f"\n--- Simplified Boolean Expression ---")
        print(f"  {simplified}")
        expr_to_validate = simplified
    else:
        print("\n(K-Map simplification not performed for n > 4 variables.)")
        print("Validating canonical expression instead.\n")
        expr_to_validate = generate_sop(tt) if form == "SOP" else generate_pos(tt)

    # ── Section 3: Validation — always runs ───────────────────
    validate(tt, expr_to_validate)

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

def run_task3():
    print("=" * 60)
    print("  CSC 6210 — Task 3: Memory Hierarchy Simulation")
    print("=" * 60)

    #prompt for sizes or use defaults
    print("\nConfigure memory sizes (number of 32-bit instructions).")
    print("Press Enter to accept the default value shown in brackets.\n")

    def get_size(prompt, default):
        while True:
            try:
                raw = input(f"  {prompt} [{default}]: ").strip()
                return int(raw) if raw else default
            except ValueError:
                print("    Error: please enter a valid integer.")

    ssd_size  = get_size("SSD capacity",  1024)
    dram_size = get_size("DRAM capacity",  256)
    l3_size   = get_size("L3 cache size",   64)
    l2_size   = get_size("L2 cache size",   16)
    l1_size   = get_size("L1 cache size",    4)

    try:
        mh = MemoryHierarchy(ssd_size, dram_size, l3_size, l2_size, l1_size)
    except ValueError as e:
        print(f"\nError: {e}")
        return

    mh.print_config()

    #pre-load SSD with half-capacity sequential 32-bit instructions, leaving room for writes
    instructions = [i + 1 for i in range(ssd_size // 2)]
    mh.load_ssd(instructions)

    print("\nEnter commands to interact with the memory hierarchy.")
    print("  read <hex>       — fetch an instruction (e.g. read 0x00000001)")
    print("  write <hex>      — write an instruction (e.g. write 0xDEADBEEF)")
    print("  state            — print current state of all levels")
    print("  stats            — print cache hit/miss statistics")
    print("  q                — quit and show final report\n")

    while True:
        try:
            raw = input("Command: ").strip()
        except (EOFError, KeyboardInterrupt):
            break

        if not raw:
            continue

        parts = raw.split()
        cmd = parts[0].lower()

        if cmd == "q":
            break

        elif cmd == "read" and len(parts) == 2:
            try:
                instr = int(parts[1], 0)    # accepts 0x... or decimal
                mh.read(instr)
            except ValueError:
                print("  Error: invalid instruction value.")

        elif cmd == "write" and len(parts) == 2:
            try:
                instr = int(parts[1], 0)
                mh.write(instr)
            except ValueError:
                print("  Error: invalid instruction value.")

        elif cmd == "state":
            mh.print_final_state()

        elif cmd == "stats":
            mh.print_stats()

        else:
            print("  Unknown command. Use: read <hex>, write <hex>, state, stats, q")

    #final report
    mh.print_trace()
    mh.print_stats()
    mh.print_final_state()
    print("\nDone.")


if __name__ == "__main__":
    choice = input("Run Task 1 (data system), Task 2 (K-Map), or Task 3 (Memory Hierarchy)? Enter 1, 2, or 3: ")
    if choice == "1":
        run_task1()
    elif choice == "2":
        run_task2()
    elif choice == "3":
        run_task3()