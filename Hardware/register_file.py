"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Hardware/register_file.py — 32-register file for single-cycle processor
"""

from Hardware.data_system import DataSystem


class RegisterFile:
    """32-entry general-purpose register file (32-bit each).

    reg[0] ($zero) is hardwired to 0 and ignores writes.
    Integrates DataSystem for binary/hex display of register contents.
    """

    NUM_REGISTERS = 32

    # Human-readable aliases used in the program
    REG_ALIAS: dict[int, str] = {
        8:  "t0", 9:  "t1", 10: "t2", 11: "t3",
        12: "t4", 13: "t5", 14: "t6",
    }

    def __init__(self):
        self._ds = DataSystem()
        self._regs: list[int] = [0] * self.NUM_REGISTERS

    # ── Read ──────────────────────────────────────────────────────────────────

    def read(self, reg1: int, reg2: int) -> tuple[int, int]:
        self._validate(reg1)
        self._validate(reg2)
        return self._regs[reg1], self._regs[reg2]

    # ── Write ─────────────────────────────────────────────────────────────────

    def write(self, reg_num: int, value: int, write_enable: bool = True) -> None:
        if not write_enable or reg_num == 0:
            return
        self._validate(reg_num)
        self._regs[reg_num] = value & 0xFFFFFFFF   # keep within 32 bits

    # ── Bulk load ─────────────────────────────────────────────────────────────

    def load(self, values: dict[int, int]) -> None:
        """Pre-load a mapping of {reg_num: value} into the register file."""
        for reg_num, val in values.items():
            self.write(reg_num, val)

    # ── Display ───────────────────────────────────────────────────────────────

    def display(self, highlight: set[int] | None = None) -> None:
        """Print the state of all named (non-zero or aliased) registers."""
        shown = set(self.REG_ALIAS) | (highlight or set())
        for reg_num in sorted(shown):
            val  = self._regs[reg_num]
            name = self.REG_ALIAS.get(reg_num, f"reg[{reg_num}]")
            bits = self._ds.decimal_to_binary(val)
            print(f"    {name} (reg[{reg_num:2d}]) = {val}  "
                  f"| 0b{bits[-8:]}  | 0x{val & 0xFFFFFFFF:08X}")

    # ── Internal ──────────────────────────────────────────────────────────────

    def _validate(self, reg_num: int) -> None:
        if not 0 <= reg_num < self.NUM_REGISTERS:
            raise ValueError(f"Register index {reg_num} out of range [0, 31].")
