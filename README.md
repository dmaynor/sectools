
# sectools
Repo for random tools

## crash_grab.py

Used for copying the crash logs out of a file. These are the contents between 
`------------[ cut here ]------------` and `---[ end trace 0000000000000000 ]---`.

```
usage: crash_grab.py [-h] [-o OUTPUT] [--separate] [--pattern PATTERN] input

Extract UBSAN call traces from syslog

positional arguments:
  input                 Path to the syslog file

options:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Path to the output file or directory
  --separate            Save each trace to a separate file
  --pattern PATTERN     Pattern for naming separate files (default: trace)
```

## mattermost_automated_deploy.py

Sets up a docker pull of a given Mattermost server version.
```
usage: ./mattermost_automated_deploy.py
```

## crash_hex_to_asm.py

Takes a space-separated string of hex from a crash dump and attempts to decode what the instructions were.
If a significant point is marked in the string with < and > enclosing an instruction, it will point out
where that opcode is in the instructions. 

Please provide a file or use the -i flag for interactive mode.
```
usage: crash_hex_to_asm.py [-h] [-i] [file]

Disassemble hex code to assembly instructions.

positional arguments:
  file               File containing hex code to disassemble
```

## dmesg_analysis.py

Enhances the output of the `dmesg` command by adding real-time timestamps, highlighting critical messages like kernel panics, and offering filtering options for improved readability and analysis.

```
usage: dmesg_analysis.py [-h] [-b] [-e] [-s STRING] [-l LOG_LEVEL]

Enhanced dmesg output with real-time timestamps and filtering.

options:
  -h, --help            show this help message and exit
  -b, --show-both-times Show both relative and real-time timestamps.
  -e, --show-kernel-errors
                        Show only kernel errors or panics.
  -s STRING, --check-string STRING
                        Show only lines containing the specified string.
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        Set the logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL).
```

## validate_ssn.py

This Python script is designed to validate Social Security Numbers (SSNs) using a series of checks based on common security patterns and standards. It can process either a single SSN or a list of SSNs from a file, providing detailed feedback on whether each SSN is valid or not.

### Key Features:

#### SSN Format Validation:

The script checks if an SSN follows the standard format (XXX-XX-XXXX) using enhanced regular expressions derived from well-known security rules, including the OWASP ModSecurity Core Rule Set (CRS) and OpenDLP.
It ensures that invalid sequences, such as all zeros in any segment, are correctly flagged.

#### Area Number Validation:

The script verifies that the Area Number (the first three digits of the SSN) falls within the valid range, excluding numbers that are known to be invalid, such as 000, 666, and numbers in the 900-999 range.

#### Exclusion of Fake or Commonly Used SSNs:

It includes a list of SSNs that are known to be fake or commonly used in media (e.g., 123-45-6789) and excludes them from being considered valid.

### Command-Line Interface (CLI):

The script can be run from the command line with options to validate either a single SSN (-s) or a file containing multiple SSNs (-f). It provides clear feedback on the validity of each SSN and explains why an SSN is invalid if it fails the checks.

```
python3 validate_ssn.py -s 123-45-6789
```

This command will validate the SSN 123-45-6789 and return whether it is valid or not, along with a reason if it is invalid.

```
python3 validate_ssn.py -f ssn_list.txt
```

This command will validate each SSN in the file ssn_list.txt, printing the results for each one.

### Help Option:

```
python3 validate_ssn.py -h
```

This command displays help information, including how to use the script and author contact details.
