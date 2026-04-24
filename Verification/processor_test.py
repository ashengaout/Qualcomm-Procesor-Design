"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Verification/processor_test.py — Tests for Task 4 single-cycle processor
"""

import pytest
from Hardware.register_file  import RegisterFile
from Hardware.alu             import ALU
from Hardware.mux             import Mux2to1
from Hardware.control_unit    import ControlUnit, FUNCT_AND, FUNCT_OR, FUNCT_AND_NOT
from Hardware.processor       import SingleCycleProcessor, _encode_rtype, T0, T1, T3, T4, T5, T6


# ── RegisterFile ──────────────────────────────────────────────────────────────

class TestRegisterFile:
    def test_initial_all_zero(self):
        rf = RegisterFile()
        for i in range(32):
            assert rf.read(i) == 0

    def test_write_and_read(self):
        rf = RegisterFile()
        rf.write(8, 1)
        assert rf.read(8) == 1

    def test_zero_register_hardwired(self):
        rf = RegisterFile()
        rf.write(0, 99)
        assert rf.read(0) == 0

    def test_write_enable_false(self):
        rf = RegisterFile()
        rf.write(9, 42, write_enable=False)
        assert rf.read(9) == 0

    def test_32bit_mask(self):
        rf = RegisterFile()
        rf.write(10, 0xFFFFFFFF + 1)   # overflows 32 bits → 0
        assert rf.read(10) == 0

    def test_load_bulk(self):
        rf = RegisterFile()
        rf.load({8: 1, 9: 0, 10: 1, 11: 1})
        assert rf.read(8)  == 1
        assert rf.read(11) == 1

    def test_invalid_register(self):
        rf = RegisterFile()
        with pytest.raises(ValueError):
            rf.read(32)
        with pytest.raises(ValueError):
            rf.write(32, 1)


# ── ALU ───────────────────────────────────────────────────────────────────────

class TestALU:
    def setup_method(self):
        self.alu = ALU()

    def test_and_basic(self):
        result, _ = self.alu.execute("AND", 1, 1)
        assert result == 1

    def test_and_zero(self):
        result, _ = self.alu.execute("AND", 1, 0)
        assert result == 0

    def test_or_basic(self):
        result, _ = self.alu.execute("OR", 0, 1)
        assert result == 1

    def test_or_zero(self):
        result, _ = self.alu.execute("OR", 0, 0)
        assert result == 0

    def test_invert_a_and_not(self):
        # ~1 & 1 = 0xFFFFFFFE & 1 = 0
        result, _ = self.alu.execute("AND", 1, 1, invert_a=True)
        assert result == 0

    def test_invert_zero_and_d(self):
        # ~0 & 1 = 0xFFFFFFFF & 1 = 1
        result, _ = self.alu.execute("AND", 0, 1, invert_a=True)
        assert result == 1

    def test_internals_returned(self):
        _, info = self.alu.execute("AND", 1, 0, invert_a=True)
        assert info["invert_a"] is True
        assert info["effective_a"] == 0xFFFFFFFE

    def test_invalid_op(self):
        with pytest.raises(ValueError):
            self.alu.execute("XOR", 1, 1)

    def test_result_masked_32bit(self):
        result, _ = self.alu.execute("OR", 0xFFFFFFFF, 0xFFFFFFFF)
        assert result == 0xFFFFFFFF


# ── Mux2to1 ───────────────────────────────────────────────────────────────────

class TestMux:
    def test_sel_zero(self):
        assert Mux2to1().select(10, 20, sel=0) == 10

    def test_sel_one(self):
        assert Mux2to1().select(10, 20, sel=1) == 20


# ── ControlUnit ───────────────────────────────────────────────────────────────

class TestControlUnit:
    def setup_method(self):
        self.cu = ControlUnit()

    def _instr(self, rs, rt, rd, funct):
        return _encode_rtype(rs, rt, rd, funct)

    def test_and_signals(self):
        dec = self.cu.decode(self._instr(8, 9, 12, FUNCT_AND))
        assert dec.signals.alu_op == "AND"
        assert dec.signals.invert is False
        assert dec.signals.reg_write is True

    def test_or_signals(self):
        dec = self.cu.decode(self._instr(12, 14, 8, FUNCT_OR))
        assert dec.signals.alu_op == "OR"
        assert dec.signals.invert is False

    def test_and_not_signals(self):
        dec = self.cu.decode(self._instr(13, 11, 14, FUNCT_AND_NOT))
        assert dec.signals.alu_op == "AND"
        assert dec.signals.invert is True
        assert dec.signals.reg_write is True

    def test_field_extraction(self):
        dec = self.cu.decode(self._instr(rs=8, rt=9, rd=12, funct=FUNCT_AND))
        assert dec.rs == 8
        assert dec.rt == 9
        assert dec.rd == 12
        assert dec.funct == FUNCT_AND

    def test_bad_opcode(self):
        # non-zero opcode → ValueError
        with pytest.raises(ValueError):
            self.cu.decode(0xAC000000)   # lw opcode = 0b100011

    def test_bad_funct(self):
        with pytest.raises(ValueError):
            self.cu.decode(self._instr(0, 0, 0, 0b111111))


# ── SingleCycleProcessor — full program execution ─────────────────────────────

class TestProcessor:
    """Exhaustive truth-table test: all 16 combinations of A, B, C, D."""

    @pytest.mark.parametrize("A,B,C,D", [
        (a, b, c, d)
        for a in (0, 1) for b in (0, 1)
        for c in (0, 1) for d in (0, 1)
    ])
    def test_all_input_combinations(self, A, B, C, D, capsys):
        expected = (A & B) | ((~C & 1) & D)
        Y = SingleCycleProcessor().run(A, B, C, D)
        assert Y == expected, (
            f"A={A} B={B} C={C} D={D}: got Y={Y}, expected {expected}"
        )

    def test_intermediate_t4(self):
        proc = SingleCycleProcessor()
        proc.run(1, 1, 0, 1)
        assert proc._reg_file.read(T4) == 1

    def test_intermediate_t6(self):
        proc = SingleCycleProcessor()
        proc.run(1, 1, 0, 1)   # ~C=~0=1, D=1 → t6=1
        assert proc._reg_file.read(T6) == 1

    def test_no_inversion_result(self):
        # A=1,B=1,C=1,D=0 → AB=1, ~C&D=0 → Y=1
        Y = SingleCycleProcessor().run(1, 1, 1, 0)
        assert Y == 1

    def test_all_zero(self):
        Y = SingleCycleProcessor().run(0, 0, 1, 0)
        assert Y == 0
