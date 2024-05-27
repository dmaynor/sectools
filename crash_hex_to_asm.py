#!/usr/bin/env python3

import capstone
import sys
import argparse

# Initialize the Capstone disassembler for x86_64 architecture
md = capstone.Cs(capstone.CS_ARCH_X86, capstone.CS_MODE_64)

def decode_hex_to_asm(hex_code):
    try:
        # Find if there are markers in the hex code
        marker_start = hex_code.find('<')
        marker_end = hex_code.find('>')
        marked_address = None

        if marker_start != -1 and marker_end != -1 and marker_start < marker_end:
            # Extract the marked byte and clean up the hex code
            marked_byte = hex_code[marker_start + 1:marker_end]
            hex_code = hex_code[:marker_start] + hex_code[marker_end + 1:]
            # Calculate the marked address offset
            marked_address = len(bytes.fromhex(hex_code[:marker_start].replace(' ', ''))) + 0x1000

        code_bytes = bytes.fromhex(hex_code.replace(' ', ''))
        instructions = []
        for instruction in md.disasm(code_bytes, 0x1000):
            instr_str = f"0x{instruction.address:x}:\t{instruction.mnemonic}\t{instruction.op_str}"
            # Highlight the instruction that was marked
            if marked_address and instruction.address == marked_address:
                instr_str += "  <-- Marked instruction"
            instructions.append(instr_str)
        return instructions
    except ValueError:
        return ["Invalid hex string"]

def process_file(file_path):
    with open(file_path, 'r') as file:
        hex_code = file.read().strip()
        instructions = decode_hex_to_asm(hex_code)
        print(f"Decoded instructions from file '{file_path}':")
        for instruction in instructions:
            print(instruction)
        print("\n")

def interactive_mode():
    while True:
        user_input = input("Enter hex code to decode (or type 'exit' to quit): ").strip()
        if user_input.lower() == "exit":
            break
        instructions = decode_hex_to_asm(user_input)
        for instruction in instructions:
            print(instruction)
        print("\n")

def main():
    parser = argparse.ArgumentParser(description="Disassemble hex code to assembly instructions.")
    parser.add_argument('file', nargs='?', help="File containing hex code to disassemble")
    parser.add_argument('-i', '--interactive', action='store_true', help="Interactive mode")
    args = parser.parse_args()

    if args.interactive:
        interactive_mode()
    elif args.file:
        process_file(args.file)
    else:
        print("Please provide a file or use the -i flag for interactive mode.")
        parser.print_help()

if __name__ == "__main__":
    main()

