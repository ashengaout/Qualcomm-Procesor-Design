Readme · MD
Copy

# 🔌 Qualcomm IoT Processor Prototype: Architecture Simulation
 
🚧 **Project Status:** Active Development (Task 3: Memory Hierarchy Simulation)
 
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
 
---

## ✅ Task 3: Memory Hierarchy Simulation

The objective of this phase is to model the full memory subsystem of the processor datapath. Instructions travel through the hierarchy from SSD all the way to L1 cache, without bypassing any intermediate level.

### Functional Requirements Implemented
1. **Memory Levels:** SSD (largest), DRAM (intermediate), and a three-level cache hierarchy (L3, L2, L1).
2. **Enforced Data Flow:** Data must move SSD → DRAM → L3 → L2 → L1 → CPU. Direct access or bypassing is not permitted.
3. **32-bit Instructions:** All data is treated as 32-bit integer instructions.
4. **Configurable Sizes:** Each level's capacity (in number of instructions) is user-configurable at startup. The hierarchy constraint SSD > DRAM > L3 > L2 > L1 is enforced and raises an error if violated.
5. **Clock-Driven Simulation:** Transfers take multiple clock cycles (student-defined latency per level). The clock advances until all in-flight transfers complete.
6. **Read Operation:** Checks L1 → L2 → L3 → DRAM → SSD. On a miss, the instruction is promoted step-by-step up through every level into L1.
7. **Write Operation:** Writes into L1 immediately, then write-back propagates L1 → L2 → L3 → DRAM → SSD (no bypassing).
8. **FIFO Cache Replacement:** When a cache level is full, the oldest instruction (first-in, first-out) is evicted and written back to the level below.
9. **Cache Hit / Miss Tracking:** Hits and misses are counted per cache level (L1, L2, L3) and reported with hit rates.

### Default Latencies

| Transfer   | Cycles |
|------------|--------|
| SSD → DRAM | 100    |
| DRAM → L3  | 20     |
| L3 → L2    | 5      |
| L2 → L1    | 2      |

### How to Run

```bash
python main.py
```

Select **Task 3** from the menu. You will be prompted to configure memory sizes (press Enter to accept defaults), then use the interactive command loop:

```
read <hex>    — fetch an instruction (e.g. read 0x00000001)
write <hex>   — write an instruction (e.g. write 0xDEADBEEF)
state         — print current contents of all memory levels
stats         — print cache hit/miss statistics
q             — quit and display the full final report
```

### Example Output
```
============================================================
  Memory Hierarchy Configuration
============================================================
  Level            Capacity     Latency
  -------------- ----------  ----------
  SSD               1024 instrs    100 cycles
  DRAM               256 instrs     20 cycles
  L3 (cache)          64 instrs      5 cycles
  L2 (cache)          16 instrs      2 cycles
  L1 (cache)           4 instrs      1 cycles

  Hierarchy: SSD > DRAM > L3 > L2 > L1 (enforced)
  Replacement policy : FIFO (cache levels L1/L2/L3)
  Instruction width  : 32-bit
============================================================

[Init] SSD loaded with 1024 instructions.
[Cycle 0] READ 0x00000001 -- MISS (all caches) -- found at SSD, promoting...
  [Cycle 2] Transfer complete: 0x00000001  L2 -> L1
  [Cycle 5] Transfer complete: 0x00000001  L3 -> L2
  [Cycle 20] Transfer complete: 0x00000001  DRAM -> L3
  [Cycle 100] Transfer complete: 0x00000001  SSD -> DRAM
[Cycle 100] READ 0x00000001 -- HIT at L1

============================================================
  Cache Hit / Miss Statistics
============================================================
  Level      Hits   Misses   Hit Rate
  ------ -------- -------- ----------
  L1            1        1      50.0%
  L2            0        1       0.0%
  L3            0        1       0.0%
```

---

## Module Structure
```
Qualcomm-Procesor-Design/
├── Hardware/
│   ├── data_system.py          # Task 1: 32-bit conversion and saturation logic
│   ├── truth_table.py          # Task 2: truth table input and validation
│   ├── boolean_logic.py        # Task 2: canonical SOP/POS generation
│   ├── Kmap.py                 # Task 2: K-Map display and greedy simplification
│   ├── logic_check.py          # Task 2: expression evaluation and PASS/FAIL
│   └── memory_hierarchy.py     # Task 3: memory hierarchy simulation
├── Verification/
│   ├── data_system_test.py
│   ├── truth_table_test.py
│   ├── boolean_logic_test.py
│   ├── kmap_test.py
│   ├── logic_check_test.py
│   └── memory_hierarchy_test.py
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
- ✅ Task 3: Memory Hierarchy Simulation (SSD → DRAM → L3 → L2 → L1)
