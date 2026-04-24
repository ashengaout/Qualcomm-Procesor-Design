"""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
Hardware/alu.py — Arithmetic Logic Unit (AND / OR with optional input inversion)
"""


class ALU:
    """32-bit ALU supporting AND and OR operations.

    The *invert_a* flag implements NOT without a separate instruction:
    when set, the first operand is bitwise-inverted before the operation.
    This flag is driven by the control unit via the function field (funct[1]).
    """

    OP_AND = "AND"
    OP_OR  = "OR"

    def execute(
        self,
        op: str,
        input_a: int,
        input_b: int,
        invert_a: bool = False,
    ) -> tuple[int, dict]:
        """Perform *op* on *input_a* and *input_b*.

        Returns (result, internals) where internals carries the pre/post
        inversion values for trace output.
        """
        raw_a = input_a & 0xFFFFFFFF
        raw_b = input_b & 0xFFFFFFFF

        effective_a = ((~raw_a) & 0xFFFFFFFF) if invert_a else raw_a

        if op == self.OP_AND:
            result = effective_a & raw_b
        elif op == self.OP_OR:
            result = effective_a | raw_b
        else:
            raise ValueError(f"Unsupported ALU operation: '{op}'. Use AND or OR.")

        internals = {
            "raw_a":      raw_a,
            "raw_b":      raw_b,
            "invert_a":   invert_a,
            "effective_a": effective_a,
            "op":         op,
            "result":     result & 0xFFFFFFFF,
        }
        return result & 0xFFFFFFFF, internals
