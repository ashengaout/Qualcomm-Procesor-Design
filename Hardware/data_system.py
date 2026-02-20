""""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
"""

class DataSystem:
    def __init__(self):
        self.min_integer = -2 ** 31
        self.max_integer = 2 ** 31 - 1

    #input is the decimal integer, and the output value is a 32bit binary value using the two's compliment system
    def decimal_to_binary(self, input_val):
        # Coversion using two's compliment
        if input_val >= 0:
            return "".join(format(input_val, '032b'))

        # two's compliment finds the binary rep of the positive input val, inverts the bits, and then returns the inverted bits + 1
        pos_val = format(abs(input_val), '032b')
        inverted_val = "".join('1' if bit == '0' else '0' for bit in pos_val)
        twos_compliment_val = int(inverted_val, 2) + 1

        return "".join(format(twos_compliment_val & 0xFFFFFFFF, '032b'))

    #method input is the binary value and a decimal value is returned
    def binary_to_decimal(self, bin_val):
        # most significant bit will also double as sign bit
        if bin_val[0] == '1':
            return str(int(bin_val, 2) - 2 ** 32)
        return str((int(bin_val, 2)))

    #method converts the binary value to a hexadecimal
    def binary_to_hex(self, bin_val):
        int_val = int(bin_val, 2)
        hex_val = format(int_val, '08x')

        return '0x' + hex_val

    #method is responsible for calling proper formatting methods (HEX, DEC, BIN) and flagging overflow/saturation
    def process_input(self, input_val, format_type):
        overflow, saturation = 0, 0

        # check for overflow
        if input_val > self.max_integer:
            input_val = self.max_integer
            overflow, saturation = 1, 1

        elif input_val < self.min_integer:
            input_val = self.min_integer
            overflow, saturation = 1, 1

        binary_value = self.decimal_to_binary(input_val)

        if format_type == "BIN":
            output_val = str(binary_value)
        elif format_type == "DEC":
            output_val = str(self.binary_to_decimal(binary_value))
        elif format_type == "HEX":
            output_val = str(self.binary_to_hex(binary_value))
        else:
            output_val = "Invalid Format"
        return output_val, overflow, saturation