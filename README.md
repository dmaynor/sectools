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

mattermost_automated_deploy.py
------------------------------
sets up a docker pull of a given mattermost server version.

usage: ./mattermost_automated_deploy.py 

crash_hex_to_asm.py
-------------------
takes a space seprated string of hex from a crash dump and attemtps to decode what the the instructions were.
if a significant point is marked in the string with < and > enclosing an instruction it will point out
where that opcode is in the instructions. 

Please provide a file or use the -i flag for interactive mode.
usage: crash_hex_to_asm.py [-h] [-i] [file]

Disassemble hex code to assembly instructions.

positional arguments:
  file               File containing hex code to disassemble

options:
  -h, --help         show this help message and exit
  -i, --interactive  Interactive mode

