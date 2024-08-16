"""
MIT License

Copyright (c) 2024 David Maynor

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

Contact: David Maynor (dmaynor@gmail.com) Twitter/X: @dave_maynor
"""

# References:
# 1. OWASP ModSecurity Core Rule Set (CRS) - A widely used set of generic attack detection rules
#    for Web Application Firewalls. Used for stricter SSN pattern matching.
#    Source: https://github.com/coreruleset/coreruleset
#
# 2. OpenDLP - An open-source data loss prevention tool that includes regular expressions and patterns
#    to detect PII, including SSNs.
#    Source: https://github.com/opendlp/opendlp
#
# 3. General regex patterns and practices referenced from SANS Internet Storm Center, 
#    and various open-source security resources.
#    Source: https://isc.sans.edu/
#

import re
import argparse

def is_valid_ssn_format(ssn):
    """Check if the SSN follows a stricter format using advanced patterns from OWASP CRS and OpenDLP."""
    # Enhanced regex patterns
    pattern = re.compile(r'''
        (?!000|666|9\d\d)\d{3}        # Area Number: Exclude 000, 666, 900-999
        ([-\s]?)                      # Optional separator (hyphen or space)
        (?!00)\d{2}                   # Group Number: Exclude 00
        \1                            # Separator must match first separator
        (?!0000)\d{4}                 # Serial Number: Exclude 0000
    ''', re.VERBOSE)

    if not pattern.match(ssn):
        return False, "Malformed SSN: Does not match the strict XXX-XX-XXXX format or contains invalid sequences."
    return True, ""

def is_valid_area_number(ssn):
    """Check if the Area Number (first three digits) is within valid range based on stricter rules."""
    area_number = int(ssn.split('-')[0])
    if area_number == 666 or area_number == 0 or (900 <= area_number <= 999):
        return False, "Invalid SSN: Area Number is out of valid range."
    return True, ""

def is_not_famous_or_fake(ssn):
    """Exclude SSNs that are known to be fake or commonly used in media."""
    fake_ssns = [
        "123-45-6789", "078-05-1120", "000-00-0000", "111-11-1111", "222-22-2222",
        "333-33-3333", "444-44-4444", "555-55-5555", "666-66-6666", "777-77-7777",
        "888-88-8888", "987-65-4320", "987-65-4321", "987-65-4322", "987-65-4323",
        "987-65-4324", "987-65-4325", "987-65-4326", "987-65-4327", "987-65-4328",
        "987-65-4329"
    ]
    if ssn in fake_ssns:
        return False, "Invalid SSN: Commonly used fake or famous SSN."
    return True, ""

def validate_ssn(ssn):
    """Run all checks and return the validation result with reasons."""
    valid_format, format_reason = is_valid_ssn_format(ssn)
    if not valid_format:
        return f"{ssn}: {format_reason}"
    
    valid_area, area_reason = is_valid_area_number(ssn)
    if not valid_area:
        return f"{ssn}: {area_reason}"

    not_fake, fake_reason = is_not_famous_or_fake(ssn)
    if not not_fake:
        return f"{ssn}: {fake_reason}"

    return f"{ssn}: SSN is valid."

def process_file(file_path):
    """Process a file containing SSNs, one per line."""
    try:
        with open(file_path, 'r') as file:
            ssns = file.readlines()
        for ssn in ssns:
            ssn = ssn.strip()
            if ssn:
                print(validate_ssn(ssn))
    except FileNotFoundError:
        print(f"File {file_path} not found.")

def main():
    parser = argparse.ArgumentParser(description="Validate Social Security Numbers (SSNs).")
    parser.add_argument("-s", "--ssn", type=str, help="A single SSN to validate.")
    parser.add_argument("-f", "--file", type=str, help="A file containing SSNs to validate, one per line.")

    args = parser.parse_args()

    if args.ssn:
        print(validate_ssn(args.ssn))
    elif args.file:
        process_file(args.file)
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
