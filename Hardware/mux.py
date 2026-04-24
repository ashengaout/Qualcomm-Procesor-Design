"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Hardware/mux.py — Multiplexer components for single-cycle datapath
"""


class Mux2to1:
    """2-to-1 multiplexer.

    sel=0 → output is input_0
    sel=1 → output is input_1
    """

    def select(self, input_0: int, input_1: int, sel: int) -> int:
        return input_1 if sel else input_0
