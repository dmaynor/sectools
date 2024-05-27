#!/usr/bin/env python3

import re
import os
import argparse

def extract_call_traces(log_file_path):
    with open(log_file_path, 'r') as file:
        log_data = file.readlines()
    
    ubsan_errors = []
    pattern_start = re.compile(r'.*------------\[ cut here \]------------.*')
    pattern_end = re.compile(r'.*---\[ end trace .* \]---.*')
    
    capture = False
    call_trace = []
    
    for line in log_data:
        if pattern_start.match(line):
            capture = True
        
        if capture:
            call_trace.append(line)
        
        if pattern_end.match(line):
            capture = False
            ubsan_errors.append(''.join(call_trace))
            call_trace = []
    
    return ubsan_errors

def save_call_traces_to_files(call_traces, output_dir, pattern="trace"):
    os.makedirs(output_dir, exist_ok=True)
    for i, trace in enumerate(call_traces):
        filename = f"{pattern}{i}.txt"
        file_path = os.path.join(output_dir, filename)
        with open(file_path, 'w') as file:
            file.write(trace + "\n")
    print(f"Saved {len(call_traces)} UBSAN call traces to separate files in directory {output_dir}")

def save_call_traces_to_file(call_traces, output_file_path):
    with open(output_file_path, 'w') as file:
        for trace in call_traces:
            file.write(trace + "\n")
    print(f"Saved {len(call_traces)} UBSAN call traces to {output_file_path}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Extract UBSAN call traces from syslog")
    parser.add_argument("input", help="Path to the syslog file")
    parser.add_argument("-o", "--output", help="Path to the output file or directory")
    parser.add_argument("--separate", action="store_true", help="Save each trace to a separate file")
    parser.add_argument("--pattern", default="trace", help="Pattern for naming separate files (default: trace)")

    args = parser.parse_args()
    
    call_traces = extract_call_traces(args.input)
    
    if args.separate:
        output_dir = args.output if args.output else "traces"
        save_call_traces_to_files(call_traces, output_dir, args.pattern)
    else:
        output_file = args.output if args.output else "traces.log"
        save_call_traces_to_file(call_traces, output_file)

