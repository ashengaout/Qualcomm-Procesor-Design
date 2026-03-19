"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Verification/test_kmap.py — pytest tests for K-Map grouping and simplification
"""

import pytest
from Hardware.truth_table import TruthTable
from Hardware.Kmap import simplify_kmap, is_valid, term_from_group


@pytest.fixture
def tt_and():
    return TruthTable(2, [0, 0, 0, 1])


@pytest.fixture
def tt_or():
    return TruthTable(2, [0, 1, 1, 1])


@pytest.fixture
def tt_3var():
    return TruthTable(3, [0, 0, 0, 1, 1, 1, 1, 0])


@pytest.fixture
def tt_all_ones():
    return TruthTable(2, [1, 1, 1, 1])


@pytest.fixture
def tt_all_zeros():
    return TruthTable(2, [0, 0, 0, 0])


@pytest.fixture
def tt_4var():
    return TruthTable(4, [1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 1])


class TestKMap:

    def test_group_valid_pair(self):
        assert is_valid([0, 1], 2) is True

    def test_group_valid_quad(self):
        assert is_valid([0, 1, 2, 3], 2) is True

    def test_group_invalid_three(self):
        assert is_valid([0, 1, 2], 2) is False

    def test_group_invalid_non_hypercube(self):
        assert is_valid([0, 1, 3], 2) is False

    def test_term_from_single_minterm(self):
        term = term_from_group([3], ['A', 'B'])
        assert term == "AB"

    def test_term_eliminates_variable(self):
        # group [0,1]: A=0 constant, B varies → A'
        term = term_from_group([0, 1], ['A', 'B'])
        assert term == "A'"

    def test_simplify_and_gate(self, tt_and):
        simplified, groups = simplify_kmap(tt_and)
        assert simplified == "F = AB"
        assert len(groups) == 1

    def test_simplify_all_zeros(self, tt_all_zeros):
        simplified, groups = simplify_kmap(tt_all_zeros)
        assert simplified == "F = 0"
        assert groups == []

    def test_simplify_all_ones(self, tt_all_ones):
        simplified, groups = simplify_kmap(tt_all_ones)
        assert simplified == "F = 1"
        assert groups == []

    def test_simplify_or_gate(self, tt_or):
        simplified, _ = simplify_kmap(tt_or)
        assert simplified.startswith("F =")
        assert simplified != "F = 0"

    def test_simplify_3var_returns_expression(self, tt_3var):
        simplified, groups = simplify_kmap(tt_3var)
        assert simplified.startswith("F =")
        assert len(groups) >= 1

    def test_simplify_4var_returns_expression(self, tt_4var):
        simplified, groups = simplify_kmap(tt_4var)
        assert simplified.startswith("F =")