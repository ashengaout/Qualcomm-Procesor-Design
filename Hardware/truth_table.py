"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Hardware/truth_table.py — Truth Table input, validation, and minterm/maxterm extraction
"""


class TruthTable():
    """
    num_vars - number of input variables where n >= 2
    output_vals - output bits size 2^n indexed by minterm

    """

    def __init__(self, num_vars: int, output_vals: list[int]):
        self.n = num_vars
        self.outputs = output_vals
        self.var_names = [chr(ord('A') + i) for i in range(num_vars)]

    @property
    def minterms(self) -> list[int]:
        return [i for i, v in enumerate(self.outputs) if v == 1]

    @property
    def maxterms(self):
        return [i for i, v in enumerate(self.outputs) if v == 0]

    def display(self):
        header = " | ".join(self.var_names) + " | F"
        separator = "-" * len(header)
        print("\n--- Truth Table ---")
        print(header)
        print(separator)
        for i, out in enumerate(self.outputs):
            bits = format(i, f'0{self.n}b')
            row = " | ".join(bits) + f" | {out}"
            print(row)
        print()

# ---- Validation of input and helper functions---------------------------

def get_num_vars() -> int:
    while True:
        try:
            n = int(input("Enter the number of input variables (n >= 2): "))
            if n < 2:
                print("Error: number of input variables must be greater than or equal to 2")
            else:
                return n
        except ValueError:
            print("Please enter a valid integer")

def get_truth_table(n: int) -> TruthTable:
    num_rows = 2 ** n
    print(f"\nEnter the {num_rows} output values (F) for each row, in order from row 0 to {num_rows - 1}:")
    outputs = []
    for i in range(num_rows):
        bits = format(i, f'0{n}b')
        while True:
            try:
                val = int(input(f"  Row {i:>2} ({bits}) F = "))
                if val not in (0, 1):
                    print("    Error: must be 0 or 1.")
                    continue
                outputs.append(val)
                break
            except ValueError:
                print("    Error: enter 0 or 1.")
    return TruthTable(n, outputs)


