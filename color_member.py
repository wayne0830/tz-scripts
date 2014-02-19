#!/usr/bin/python
import sys
import re

while True:
    line = sys.stdin.readline()
    if line:
        print re.sub(r"(member|CONFLICT)",r"\033[031m\1\033[0m",line,flags=re.IGNORECASE),
    else:
        break;
