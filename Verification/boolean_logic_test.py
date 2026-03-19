"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Verification/test_boolean_logic.py — pytest tests for generate_sop / generate_pos
"""

import pytest
from Hardware.truth_table import TruthTable
from Hardware.boolean_logic import generate_sop, generate_pos


@pytest.fixture
def tt_and():
    return TruthTable(2, [0, 0, 0, 1])


@pytest.fixture
def tt_all_ones():
    return TruthTable(2, [1, 1, 1, 1])


@pytest.fixture
def tt_all_zeros():
    return TruthTable(2, [0, 0, 0, 0])


@pytest.fixture
def tt_3var():
    return TruthTable(3, [0, 0, 0, 1, 1, 1, 1, 0])


class TestBooleanLogic:

    def test_sop_contains_f(self, tt_and):
        assert generate_sop(tt_and).startswith("F =")

    def test_sop_and_gate(self, tt_and):
        assert generate_sop(tt_and) == "F = AB"

    def test_sop_all_zeros(self, tt_all_zeros):
        assert generate_sop(tt_all_zeros) == "F = 0"

    def test_sop_all_ones_expands_all_terms(self, tt_all_ones):
        # canonical SOP expands all 4 minterms, no shortcut
        sop = generate_sop(tt_all_ones)
        assert sop.startswith("F =")
        rhs = sop.split("=", 1)[1].strip()
        assert len(rhs.split("+")) == 4

    def test_pos_contains_f(self, tt_and):
        assert generate_pos(tt_and).startswith("F =")

    def test_pos_all_ones(self, tt_all_ones):
        assert generate_pos(tt_all_ones) == "F = 1"

    def test_pos_all_zeros_expands_all_terms(self, tt_all_zeros):
        # canonical POS expands all 4 maxterms, no shortcut
        pos = generate_pos(tt_all_zeros)
        assert pos.startswith("F =")
        rhs = pos.split("=", 1)[1].strip()
        assert len(rhs.split("·")) == 4

    def test_sop_3var_has_four_terms(self, tt_3var):
        sop = generate_sop(tt_3var)
        rhs = sop.split("=", 1)[1].strip()
        assert len(rhs.split("+")) == 4

    def test_pos_3var_has_four_terms(self, tt_3var):
        pos = generate_pos(tt_3var)
        rhs = pos.split("=", 1)[1].strip()
        assert len(rhs.split("·")) == 4
