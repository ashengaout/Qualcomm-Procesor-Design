"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Verification/test_truth_table.py — pytest tests for TruthTable
"""

import pytest
from Hardware.truth_table import TruthTable


@pytest.fixture
def tt_and():
    """2-variable AND gate: F = AB, minterm 3 only."""
    return TruthTable(2, [0, 0, 0, 1])


@pytest.fixture
def tt_or():
    """2-variable OR gate: F = A + B, minterms 1,2,3."""
    return TruthTable(2, [0, 1, 1, 1])


@pytest.fixture
def tt_3var():
    """3-variable function with minterms 3,4,5,6."""
    return TruthTable(3, [0, 0, 0, 1, 1, 1, 1, 0])


@pytest.fixture
def tt_all_ones():
    """2-variable always-true function: F = 1."""
    return TruthTable(2, [1, 1, 1, 1])


@pytest.fixture
def tt_all_zeros():
    """2-variable always-false function: F = 0."""
    return TruthTable(2, [0, 0, 0, 0])


@pytest.fixture
def tt_4var():
    """4-variable checkerboard function."""
    return TruthTable(4, [1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1])


class TestTruthTable:

    def test_minterms_and(self, tt_and):
        assert tt_and.minterms == [3]

    def test_maxterms_and(self, tt_and):
        assert tt_and.maxterms == [0, 1, 2]

    def test_minterms_or(self, tt_or):
        assert tt_or.minterms == [1, 2, 3]

    def test_minterms_3var(self, tt_3var):
        assert tt_3var.minterms == [3, 4, 5, 6]

    def test_maxterms_3var(self, tt_3var):
        assert tt_3var.maxterms == [0, 1, 2, 7]

    def test_var_names_2var(self, tt_and):
        assert tt_and.var_names == ['A', 'B']

    def test_var_names_3var(self, tt_3var):
        assert tt_3var.var_names == ['A', 'B', 'C']

    def test_var_names_4var(self, tt_4var):
        assert tt_4var.var_names == ['A', 'B', 'C', 'D']

    def test_all_ones_minterms(self, tt_all_ones):
        assert tt_all_ones.minterms == [0, 1, 2, 3]

    def test_all_zeros_minterms(self, tt_all_zeros):
        assert tt_all_zeros.minterms == []

    def test_all_zeros_maxterms(self, tt_all_zeros):
        assert tt_all_zeros.maxterms == [0, 1, 2, 3]
