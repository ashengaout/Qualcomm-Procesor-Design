"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Verification/test_validator.py — pytest tests for validator.py
"""

import pytest
from Hardware.truth_table import TruthTable
from Hardware.Kmap import simplify_kmap
from Hardware.logic_check import validate, evaluate, eval_sop, eval_pos


@pytest.fixture
def tt_and():
    return TruthTable(2, [0, 0, 0, 1])


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


class TestValidator:

    # --- SOP evaluation ---
    def test_sop_all_literals_true(self):
        assert eval_sop("AB", {'A': 1, 'B': 1}) == 1

    def test_sop_one_literal_false(self):
        assert eval_sop("AB", {'A': 1, 'B': 0}) == 0

    def test_sop_complement_satisfied(self):
        assert eval_sop("A'B", {'A': 0, 'B': 1}) == 1

    def test_sop_complement_unsatisfied(self):
        assert eval_sop("A'B", {'A': 1, 'B': 1}) == 0

    def test_sop_second_term_satisfies(self):
        # first term AB fails, second term A'B' succeeds
        assert eval_sop("AB + A'B'", {'A': 0, 'B': 0}) == 1

    # --- POS evaluation ---
    def test_pos_all_terms_satisfied(self):
        assert eval_pos("(A + B) · (A' + B')", {'A': 1, 'B': 0}) == 1

    def test_pos_one_term_unsatisfied(self):
        # second term A' + B' fails when A=1, B=1
        assert eval_pos("(A + B) · (A' + B')", {'A': 1, 'B': 1}) == 0

    def test_pos_complement_in_term(self):
        assert eval_pos("(A + B')", {'A': 0, 'B': 0}) == 1

    # --- Auto-detect via _evaluate ---
    def test_evaluate_detects_sop(self):
        assert evaluate("F = AB", {'A': 1, 'B': 1}) == 1

    def test_evaluate_detects_pos(self):
        assert evaluate("F = (A + B)", {'A': 0, 'B': 1}) == 1

    def test_evaluate_constant_zero(self):
        assert evaluate("F = 0", {'A': 1, 'B': 1}) == 0

    def test_evaluate_constant_one(self):
        assert evaluate("F = 1", {'A': 0, 'B': 0}) == 1

    # --- validate() ---
    def test_validate_pass_sop(self, tt_and):
        assert validate(tt_and, "F = AB") is True

    def test_validate_fail_sop(self, tt_and):
        assert validate(tt_and, "F = A'B") is False

    def test_validate_pass_pos(self, tt_and):
        assert validate(tt_and, "F = (A + B) · (A + B') · (A' + B)") is True

    def test_validate_fail_pos(self, tt_and):
        assert validate(tt_and, "F = (A + B)") is False

    def test_validate_constant_zero(self, tt_all_zeros):
        assert validate(tt_all_zeros, "F = 0") is True

    def test_validate_constant_one(self, tt_all_ones):
        assert validate(tt_all_ones, "F = 1") is True

    def test_validate_3var_simplified(self, tt_3var):
        simplified, _ = simplify_kmap(tt_3var)
        assert validate(tt_3var, simplified) is True

    def test_validate_4var_simplified(self, tt_4var):
        simplified, _ = simplify_kmap(tt_4var)
        assert validate(tt_4var, simplified) is True