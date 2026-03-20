Readme · MD
Copy

# 🔌 Qualcomm IoT Processor Prototype: Architecture Simulation
 
🚧 **Project Status:** Active Development (Task 2: Boolean Logic & K-Map Simplification)
 
This repository contains the design and implementation of a 32-bit reference architecture for IoT applications. This project is developed for the CSC 6210 Computer Architecture course at Georgia State University.
 
---
 
## ✅ Task 1: Data Systems
 
The objective of this phase was to implement the core conversion logic and data constraints for the entire processor system. This module ensures the processor can interface between human-readable decimal inputs and the machine-native Two's Complement binary representation.
 
### Functional Requirements Implemented
1. **32-bit Signed Integer Machine:** Operates on a standard 32-bit width with internal Two's Complement representation.
2. **Range Validation:** Supports a valid representable range from -2,147,483,648 to 2,147,483,647.
3. **Overflow Detection:** Hardware-level flags identify when input values fall outside the 32-bit signed boundaries.
4. **Saturation Logic:** Instead of wrap-around, the system implements Saturation (Clamping) to prevent system instability.
5. **Multi-Format Output Selection:** Configurable formatting for Decimal (DEC), 32-bit Binary string (BIN), or 8-digit Hexadecimal (HEX).
 
---
 
## ✅ Task 2: Boolean Logic & K-Map Simplification
 
The objective of this phase is to implement combinational logic design as part of the processor datapath. The system accepts a user-defined truth table, converts it into a canonical Boolean equation, simplifies it using a Karnaugh Map, and validates the result.
 
### Functional Requirements Implemented
1. **Truth Table Input:** Interactively collects 2ⁿ output values from the user for n ≥ 2 input variables.
2. **Truth Table Validation:** Ensures the correct number of rows, unique input combinations, and binary output values.
3. **Canonical Equation Generation:** Produces either SOP (Sum of Products) or POS (Product of Sums) form based on user selection, along with the corresponding minterm or maxterm list.
4. **K-Map Construction:** Displays an ASCII Karnaugh Map for functions with 2–4 variables.
5. **Greedy Simplification:** Groups 1s (SOP) or 0s (POS) using a greedy largest-group-first strategy to derive a simplified Boolean expression.
6. **Validation:** Re-evaluates the simplified expression against every row of the original truth table and reports PASS or FAIL.
 
### How to Run
 
```bash
python main.py
```
 
Select **Task 2** from the menu, then follow the interactive prompts:
1. Enter the number of input variables (n ≥ 2)
2. Enter the output value (0 or 1) for each row
3. Select canonical form: `SOP` or `POS`
 
### Example Output
```
--- Truth Table ---
A | B | C | F
-------------
0 | 0 | 0 | 0
0 | 0 | 1 | 0
0 | 1 | 0 | 0
0 | 1 | 1 | 1
1 | 0 | 0 | 1
1 | 0 | 1 | 1
1 | 1 | 0 | 1
1 | 1 | 1 | 0
 
--- Canonical SOP Expression ---
F = A'BC + AB'C' + AB'C + ABC'
Minterms: m(3, 4, 5, 6)
 
--- K-Map ---
   \ BC
     00  01  11  10
    +-----------------
 0  | 0 | 0 | 1 | 0 |
 1  | 1 | 1 | 0 | 1 |
    +-----------------
 
--- K-Map Groups (Greedy) ---
  Group [4, 5] → term: AB'
  Group [3] → term: A'BC
  Group [6] → term: ABC'
 
--- Simplified Boolean Expression ---
  F = AB' + A'BC + ABC'
 
RESULT: PASS — simplified expression matches truth table for all inputs.
```
 
### Module Structure
```
Qualcomm-Procesor-Design/
├── Hardware/
│   ├── data_system.py       # Task 1: 32-bit conversion and saturation logic
│   ├── truth_table.py       # Task 2: truth table input and validation
│   ├── boolean_logic.py     # Task 2: canonical SOP/POS generation
│   ├── kmap.py              # Task 2: K-Map display and greedy simplification
│   └── validator.py         # Task 2: expression evaluation and PASS/FAIL
├── Verification/
│   ├── test_truth_table.py
│   ├── test_boolean_logic.py
│   ├── test_kmap.py
│   └── test_validator.py
├── main.py
└── README.md
```
 
### Running Tests
 
```bash
python -m pytest Verification/ -v
```
 
---
 
## 🛠️ Tech Stack & Verification
- **Language:** Python
- **IDE:** PyCharm
- **Verification Suite:** Automated unit testing via Pytest
 
## 📂 Project Roadmap
- ✅ Task 1: Data Systems, Conversion Logic, and Saturation
- ✅ Task 2: Truth Table → Boolean Equation → K-Map Simplification
- 🔲 Task 3: Pending further requirements
