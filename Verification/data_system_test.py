""""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
"""

import pytest
from Hardware.data_system import DataSystem

@pytest.mark.parametrize("input_val, format_type, expected_out, expected_overflow", [
    ("123", "DEC", "123", 0),  #positive
    ("0", "BIN", "0" * 32, 0),  #zero
    ("-123", "HEX", "0xffffff85", 0),  #negative
    ("2147483647", "DEC", "2147483647", 0),  #max integer
    ("-2147483648", "DEC", "-2147483648", 0),  #min integer
    ("2147483648", "DEC", "2147483647", 1),  #overflow
    ("-2147483649", "DEC", "-2147483648", 1)  #overflow
])
def test_processor_data_system(input_val, format_type, expected_out, expected_overflow):
    processor = DataSystem()
    result, overflow, saturated = processor.process_input(int(input_val), format_type)

    assert result == expected_out
    assert overflow == expected_overflow
    assert saturated == expected_overflow