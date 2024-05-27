# sectools
repo for random tools

crash_grab.py
-------------
Used for copying the crash logs out of a file. These are the contents between 
------------[ cut here ]------------ and ---[ end trace 0000000000000000 ]---

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


