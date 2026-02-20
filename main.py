""""
Amelia Shengaout
CSC 6210 Computer Architecture
Spring 2026
"""

from Hardware.data_system import DataSystem

def run_simulation():
    data_system = DataSystem()

    #user input for testing data system
    print("---Qualcomm IoT Reference Architecture: Task 1---")

    while True:
        try:
            user_input = input("Enter a signed integer value (or 'q' to quit): ")

            if user_input == 'q':
                print("Quitting...")
                break

            user_format = input("Select output format (DEC, HEX, BIN): ").upper()

            result, overflow, saturation = data_system.process_input(int(user_input), user_format)

            print("\n---Processor Output---")
            print(f"Formatted Value: {result}")
            print(f"Overflow: {overflow}")
            print(f"Saturation: {saturation}")
            print("-------------------------")

        except ValueError:
            print("Invalid input: please enter a signed integer value.")
        except Exception as exception:
            print(exception)

if __name__ == "__main__":
    run_simulation()