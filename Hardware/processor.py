"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Hardware/processor.py — Single-cycle 32-bit processor datapath

Computes:  Y = A·B + C'·D
Program:
    and  t4, t0, t1   ; t4 = A & B          (funct=AND)
    and  t6, t5, t3   ; t6 = (~C) & D       (funct=AND-NOT, invert t5=C)
    or   t0, t4, t6   ; t0 = t4 | t6 = Y    (funct=OR)

Each instruction goes through one Fetch → Decode → Execute → Write-back cycle.
The MemoryHierarchy from Task 3 is used as instruction memory: instructions
are pre-loaded into SSD and fetched into L1 cache on first access.
"""

from Hardware.register_file import RegisterFile
from Hardware.alu           import ALU
from Hardware.mux           import Mux2to1
from Hardware.control_unit  import ControlUnit, FUNCT_AND, FUNCT_OR, FUNCT_AND_NOT
from Hardware.memory_hierarchy import MemoryHierarchy
from Hardware.logic_check   import evaluate


# ── Register number constants ─────────────────────────────────────────────────
T0, T1, T2, T3, T4, T5, T6 = 8, 9, 10, 11, 12, 13, 14

_REG_NAME: dict[int, str] = {
    T0: "t0", T1: "t1", T2: "t2", T3: "t3",
    T4: "t4", T5: "t5", T6: "t6",
}


# ── Instruction encoding helpers ──────────────────────────────────────────────

def _encode_rtype(rs: int, rt: int, rd: int, funct: int) -> int:
    """Pack an R-type instruction into a 32-bit word (opcode=0, shamt=0)."""
    return (rs & 0x1F) << 21 | (rt & 0x1F) << 16 | (rd & 0x1F) << 11 | (funct & 0x3F)


def _build_program() -> list[int]:
    """Return the three 32-bit instruction words for Y = A·B + C'·D."""
    return [
        _encode_rtype(rs=T0, rt=T1, rd=T4, funct=FUNCT_AND),      # and t4, t0, t1
        _encode_rtype(rs=T5, rt=T3, rd=T6, funct=FUNCT_AND_NOT),   # and t6, t5, t3 (~C & D)
        _encode_rtype(rs=T4, rt=T6, rd=T0, funct=FUNCT_OR),        # or  t0, t4, t6
    ]


_INSTR_COMMENTS = [
    "and  t4, t0, t1   ; t4 = A & B",
    "and  t6, t5, t3   ; t6 = (~C) & D   [invert flag set in funct=100110]",
    "or   t0, t4, t6   ; t0 = t4 | t6 = Y",
]


# ── Single-cycle processor ────────────────────────────────────────────────────

class SingleCycleProcessor:
    """Single-cycle 32-bit processor implementing AND / OR / AND-NOT.

    Datapath components (each in its own file, per spec Section 2.2):
      - RegisterFile  (Hardware/register_file.py)
      - ALU           (Hardware/alu.py)
      - Mux2to1       (Hardware/mux.py)
      - ControlUnit   (Hardware/control_unit.py)
      - MemoryHierarchy (Hardware/memory_hierarchy.py) ← instruction memory

    Execution model: Fetch → Decode → Execute → Write-back in one logical cycle.
    """

    # Instruction memory is a small MemoryHierarchy (SSD→L1) sized for 3 instructions
    _IM_CONFIG = dict(
        ssd_size=16, dram_size=8, l3_size=6, l2_size=4, l1_size=3,
    )

    def __init__(self):
        self._reg_file = RegisterFile()
        self._alu      = ALU()
        self._mux      = Mux2to1()
        self._cu       = ControlUnit()
        self._imem     = MemoryHierarchy(**self._IM_CONFIG)
        self._program: list[int] = []
        self._pc: int = 0

    # ── Public API ────────────────────────────────────────────────────────────

    def run(self, A: int, B: int, C: int, D: int) -> int:
        """Execute the program Y = A·B + C'·D and return the result in t0."""
        self._reset(A, B, C, D)
        self._print_header(A, B, C, D)
        self._print_reg_state("Initial register state")

        for cycle, instr_word in enumerate(self._program, start=1):
            self._execute_cycle(cycle, instr_word)

        Y, _ = self._reg_file.read(T0, T0)
        self._print_footer(A, B, C, D, Y)
        return Y

    # ── Cycle stages ──────────────────────────────────────────────────────────

    def _execute_cycle(self, cycle: int, instr_word: int) -> None:
        """One full Fetch → Decode → Execute → Write-back cycle."""

        # 1. FETCH — retrieve instruction word from instruction memory (MemoryHierarchy)
        fetched = self._fetch(instr_word)

        # 2. DECODE — control unit extracts fields and generates control signals
        decoded = self._cu.decode(fetched)
        sig     = decoded.signals

        # 3. EXECUTE — read registers, MUX selects ALU input B, ALU operates
        read_data1, read_data2 = self._reg_file.read(decoded.rs, decoded.rt)
        alu_input_b = self._mux.select(read_data2, 0, sel=0)   # sel=0: R-type uses rt
        result, internals = self._alu.execute(sig.alu_op, read_data1, alu_input_b, sig.invert)

        # 4. WRITE-BACK — store result if RegWrite is asserted
        self._reg_file.write(decoded.rd, result, write_enable=sig.reg_write)

        # Trace output
        rs_name = _REG_NAME.get(decoded.rs, f"reg[{decoded.rs}]")
        rt_name = _REG_NAME.get(decoded.rt, f"reg[{decoded.rt}]")
        rd_name = _REG_NAME.get(decoded.rd, f"reg[{decoded.rd}]")

        print(f"\n{'-'*62}")
        print(f"  Cycle {cycle}: {_INSTR_COMMENTS[cycle - 1]}")
        print(f"{'-'*62}")
        print(f"  [FETCH]     instr_word = 0x{fetched:08X}")
        print(f"  [DECODE]    opcode={decoded.opcode:06b}  rs={decoded.rs:05b}({rs_name})"
              f"  rt={decoded.rt:05b}({rt_name})  rd={decoded.rd:05b}({rd_name})"
              f"  funct={decoded.funct:06b}")
        print(f"  [CTRL SIG]  ALU_OP={sig.alu_op:<3}  INVERT={int(sig.invert)}"
              f"  RegWrite={int(sig.reg_write)}"
              f"  ({self._cu.funct_name(decoded.funct)})")
        print(f"  [EXECUTE]   {rs_name}={internals['raw_a']}  {rt_name}={internals['raw_b']}", end="")
        if sig.invert:
            print(f"  -> ~{rs_name}=0x{internals['effective_a']:08X}", end="")
        print(f"  -> ALU({sig.alu_op}) = {result}")
        print(f"  [WRITEBACK] {rd_name} <- {result}")
        self._print_reg_state("Register state after cycle")

    # ── Fetch (uses MemoryHierarchy from Task 3) ──────────────────────────────

    def _fetch(self, instr_word: int) -> int:
        """Fetch instruction from the instruction memory hierarchy.

        On first access the instruction travels SSD → DRAM → L3 → L2 → L1.
        Subsequent accesses to the same word would hit L1 directly.
        """
        self._imem.read(instr_word)
        return instr_word

    # ── Initialisation / reset ────────────────────────────────────────────────

    def _reset(self, A: int, B: int, C: int, D: int) -> None:
        self._reg_file = RegisterFile()
        self._imem     = MemoryHierarchy(**self._IM_CONFIG)
        self._program  = _build_program()
        self._pc       = 0

        # Pre-load instruction memory (SSD) with encoded instruction words
        self._imem.load_ssd(self._program)

        # Initialise registers: t0=A, t1=B, t2=C, t3=D
        # t5 is pre-loaded with C so the AND-NOT instruction can invert it
        self._reg_file.load({
            T0: A, T1: B, T2: C, T3: D, T5: C,
        })

    # ── Pretty printing ───────────────────────────────────────────────────────

    def _print_header(self, A: int, B: int, C: int, D: int) -> None:
        print(f"\n{'='*62}")
        print(f"  Single-Cycle Processor -- Y = A.B + C'.D")
        print(f"  Inputs:  A={A}  B={B}  C={C}  D={D}")
        print(f"{'='*62}")
        prog = _build_program()
        print("  Program (3 instructions):")
        for word, comment in zip(prog, _INSTR_COMMENTS):
            print(f"    0x{word:08X}  {comment}")

    def _print_reg_state(self, label: str) -> None:
        print(f"  [{label}]")
        self._reg_file.display()

    def _print_footer(self, A: int, B: int, C: int, D: int, Y: int) -> None:
        # Expected result via logic_check (reuses Task 2 infrastructure)
        expected = evaluate("F = AB + C'D", {"A": A, "B": B, "C": C, "D": D})
        match    = Y == expected

        t4, t6 = self._reg_file.read(T4, T6)

        print(f"\n{'='*62}")
        print("  Intermediate register values:")
        print(f"    t4 = A & B       = {A} & {B}   = {t4}")
        print(f"    t6 = (~C) & D    = (~{C}) & {D} = {t6}")
        print(f"    t0 = t4 | t6     = {t4} | {t6}   = {Y}  <- Y")
        print(f"\n  Final output:  Y = {Y}")
        print(f"  Expected (A.B + C'.D) = {expected}")
        print(f"  Validation (logic_check): {'PASS' if match else 'FAIL'}")
        print(f"{'='*62}\n")


# ── Convenience function ──────────────────────────────────────────────────────

def run_program(A: int, B: int, C: int, D: int) -> int:
    """Instantiate and run the processor for given boolean inputs."""
    return SingleCycleProcessor().run(A, B, C, D)
