#!/usr/bin/env python3
"""
Written by David Maynor
E: dmaynor@protonmail.com
X: @dave_maynor

Goal:
This tool is designed to enhance the output of the `dmesg` command by adding real-time timestamps to the kernel messages, highlighting kernel panics, and optionally filtering to show only errors, kernel panics, or lines matching a user-provided string. The tool aims to assist system administrators and developers in analyzing kernel messages more effectively by providing more context and better readability.

Design:
1. Permissions Check: Ensure the script is run as root.
2. Get Boot Time: Retrieve the system boot time from `/proc/stat`.
3. Run dmesg: Execute the `dmesg` command and capture its output.
4. Convert Time: Convert relative timestamps in `dmesg` output to real-time timestamps.
5. Replace Times: Replace relative timestamps with real-time timestamps in the `dmesg` output.
6. Highlight Kernel Panics: Highlight kernel panic messages in yellow.
7. Filter Errors: Optionally filter the output to show only errors and kernel panics.
8. Search String: Optionally filter the output to show only lines containing a user-provided string.
9. Count Errors and Panics: Count the number of errors and kernel panics, and display the counts at the end.
10. Logging: Provide logging for important events and errors.
11. Configuration: Use command-line arguments for configuration.
"""

import subprocess
import time
import datetime
import os
import re
import sys
import argparse
import logging

def setup_logging(log_level):
    """
    Set up logging with the specified log level.
    
    Args:
        log_level (str): The logging level.
    """
    logging.basicConfig(level=log_level,
                        format='%(asctime)s - %(levelname)s - %(message)s',
                        handlers=[logging.StreamHandler(sys.stdout)])

def check_permissions():
    """
    Check if the script is run as root. Exit if not.
    """
    if os.geteuid() != 0:
        logging.error("This script must be run as root. Exiting.")
        sys.exit(1)

def get_boot_time():
    """
    Get the system boot time from /proc/stat.
    
    Returns:
        int: The boot time as a Unix timestamp.
        
    Raises:
        RuntimeError: If boot time is not found in /proc/stat.
    """
    try:
        with open('/proc/stat', 'r') as f:
            for line in f:
                if line.startswith('btime'):
                    return int(line.split()[1])
        raise RuntimeError("Boot time not found in /proc/stat")
    except Exception as e:
        logging.error(f"Error getting boot time: {e}")
        sys.exit(1)

def run_dmesg():
    """
    Run the dmesg command and capture its output.
    
    Returns:
        str: The output of the dmesg command.
        
    Raises:
        RuntimeError: If dmesg command fails.
    """
    try:
        result = subprocess.run(['dmesg'], capture_output=True, text=True)
        if result.returncode != 0:
            raise RuntimeError("Failed to run dmesg.")
        return result.stdout
    except Exception as e:
        logging.error(f"Error running dmesg: {e}")
        sys.exit(1)

def convert_time(boot_time, relative_time):
    """
    Convert a relative timestamp to a real-time timestamp.
    
    Args:
        boot_time (int): The boot time as a Unix timestamp.
        relative_time (str): The relative time from dmesg.
        
    Returns:
        str: The real-time timestamp in the format YYYY/MM/DD HH:MM:SS.MMMSSS.
    """
    actual_time = boot_time + float(relative_time)
    return datetime.datetime.fromtimestamp(actual_time).strftime('%Y/%m/%d %H:%M:%S') + f'{int((actual_time % 1) * 1000000):06d}'

def replace_times(dmesg_output, boot_time, show_both_times):
    """
    Replace relative timestamps in dmesg output with real-time timestamps.
    
    Args:
        dmesg_output (str): The output of the dmesg command.
        boot_time (int): The boot time as a Unix timestamp.
        show_both_times (bool): Flag to indicate if both relative and real-time timestamps should be shown.
        
    Returns:
        str: The dmesg output with real-time timestamps.
    """
    relative_time_pattern = re.compile(r'\[\s*(\d+\.\d+)\]')
    def replacer(match):
        original_time = match.group(1)
        converted_time = convert_time(boot_time, original_time)
        if show_both_times:
            return f"\033[31m[{original_time}] [{converted_time}]\033[0m"
        else:
            return f"\033[31m[{converted_time}]\033[0m"
    return relative_time_pattern.sub(replacer, dmesg_output)

def highlight_kernel_panic(line):
    """
    Highlight kernel panic messages in yellow.
    
    Args:
        line (str): A line from the dmesg output.
        
    Returns:
        str: The line with kernel panic messages highlighted.
    """
    if "Kernel panic" in line or "Oops" in line:
        return f"\033[33m{line}\033[0m"  # Yellow color for kernel panic
    return line

def filter_errors(lines):
    """
    Filter lines to show only those containing errors or kernel panics.
    
    Args:
        lines (list): A list of lines from the dmesg output.
        
    Returns:
        list: A list of filtered lines containing errors or kernel panics.
    """
    error_keywords = ["error", "fail", "fatal", "panic", "oops"]
    filtered_lines = []
    for line in lines:
        if any(keyword in line.lower() for keyword in error_keywords):
            filtered_lines.append(line)
    return filtered_lines

def count_errors_and_panics(lines):
    """
    Count the number of errors and kernel panics in the lines.
    
    Args:
        lines (list): A list of lines from the dmesg output.
        
    Returns:
        tuple: A tuple containing the count of errors and kernel panics.
    """
    error_keywords = ["error", "fail", "fatal", "panic", "oops"]
    error_count = 0
    kernel_panic_count = 0
    in_kernel_panic = False

    for line in lines:
        if "Kernel panic" in line or "Oops" in line:
            kernel_panic_count += 1
            in_kernel_panic = True
        elif "---[ end trace" in line:
            in_kernel_panic = False
        elif in_kernel_panic:
            continue  # Errors in kernel panic are already counted
        elif any(keyword in line.lower() for keyword in error_keywords):
            error_count += 1

    return error_count, kernel_panic_count

def filter_by_string(lines, search_string):
    """
    Filter lines to show only those containing a specific search string.
    
    Args:
        lines (list): A list of lines from the dmesg output.
        search_string (str): The string to search for in the dmesg output.
        
    Returns:
        list: A list of filtered lines containing the search string.
    """
    return [line for line in lines if search_string.lower() in line.lower()]

def main(show_both_times, show_kernel_errors, search_string, log_level):
    """
    Main function to enhance and analyze dmesg output.
    
    Args:
        show_both_times (bool): Flag to indicate if both relative and real-time timestamps should be shown.
        show_kernel_errors (bool): Flag to indicate if only kernel errors and panics should be shown.
        search_string (str): String to search for in the dmesg output.
        log_level (str): The logging level.
    """
    setup_logging(log_level)
    check_permissions()
    boot_time = get_boot_time()
    
    dmesg_output = run_dmesg()
    modified_dmesg_output = replace_times(dmesg_output, boot_time, show_both_times)
    
    lines = modified_dmesg_output.split('\n')
    
    if show_kernel_errors:
        lines = filter_errors(lines)
    
    if search_string:
        lines = filter_by_string(lines, search_string)
    
    if show_kernel_errors or search_string:
        error_count, kernel_panic_count = count_errors_and_panics(lines)
    
    for line in lines:
        if line.strip():
            print(highlight_kernel_panic(line))
    
    if show_kernel_errors:
        logging.info(f"Error count: {error_count} errors, {kernel_panic_count} kernel panics")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Enhanced dmesg output with real-time timestamps.")
    parser.add_argument('-b', '--show-both-times', action='store_true', help="Show both relative and concrete times.")
    parser.add_argument('-e', '--show-kernel-errors', action='store_true', help="Show only kernel errors or panics.")
    parser.add_argument('-s', '--check-string', help="Show only lines containing the specified string.")
    parser.add_argument('-l', '--log-level', default='INFO', help="Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).")
    args = parser.parse_args()
    
    log_level = getattr(logging, args.log_level.upper(), logging.INFO)
    
    main(args.show_both_times, args.show_kernel_errors, args.check_string, log_level)

