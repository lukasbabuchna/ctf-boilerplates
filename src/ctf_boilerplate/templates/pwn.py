#!/usr/bin/env python3
import os
import re
import struct
import sys
import time
from pwn import *

HOST = "challenge.example.com"   # remote host, leave empty for local
PORT = 1337                      # remote port
BINARY = "./chal"                # local binary, used when HOST is empty

context.log_level = "debug"


def conn():
    return remote(HOST, PORT) if HOST else process(BINARY)


p = conn()

if os.path.exists(BINARY):
    elf = context.binary = ELF(BINARY, checksec=False)
