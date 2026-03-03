## 🔌**Qualcomm IoT Processor Prototype: Architecture Simulation**

### 🚧 **Project Status: Active Development (Task 1: Data Systems)**

This repository contains the design and implementation of a 32-bit reference architecture for IoT applications. This project is developed for the CSC 6210 Computer Architecture course at Georgia State University.

### 🎯 **Milestone 1: Data Systems**

The objective of this phase is to implement the core conversion logic and data constraints for the entire processor system. This module ensures the processor can interface between human-readable decimal inputs and the machine-native Two's Complement binary representation.

✅ **Functional Requirements Implemented**

1. 32-bit Signed Integer Machine: Operates on a standard 32-bit width with internal Two's Complement representation.

2. Range Validation: Supports a valid representable range from -2,147,483,648 to 2,147,483,647.

3. Overflow Detection: Hardware-level flags identify when input values fall outside the 32-bit signed boundaries.

4. Saturation Logic: Instead of wrap-around, the system implements Saturation (Clamping) to prevent system instability.

5. Multi-Format Output Selection: Configurable formatting for Decimal (DEC), 32-bit Binary string (BIN), or 8-digit Hexadecimal (HEX).

### 🛠️ **Tech Stack & Verification**

Language: Python.

IDE: PyCharm.

Verification Suite: Automated unit testing via Pytest

### 📂 **Project Roadmap**

Task 1 (Current): Data Systems, Conversion Logic, and Saturation.

Task 2 (Upcoming): pending further requirements.
