"""

AOPM Compiler
Version: 1.0.0
Made by: GusDev

"""
# libs
import os
import subprocess as sub
from pathlib import Path as p
import sys

# print defs
def info(msg: str = "message"):
    print(f"\033[36m[INFO]\033[0m: {msg}")

def success(msg: str = "mesasge"):
    print(f"\033[32m[SUCCESS]\033[0m: {msg}")

def warn(msg: str = "message"):
    print(f"\033[33m[WARNING]\033[0m: {msg}")

def error(msg: str = "message", exit_: bool = False):
    print(f"\033[31m[ERROR]\033[0m: {msg}")
    if exit_:
        sys.exit(1)

# simplify arguments
argc = len(sys.argv)
argv = sys.argv

if argc < 2:
    error("Too few arguments :(", True)

config_path = argv[1]
if p(config_path).is_file():
    pass
else:
    error("The specified .config file is a directory or does not exist :(", True)

info("Opening: '.config'...")
config_content = None
with open(config_path, "r") as f:
    config_content = f.read()

if config_content:
    success("'.config' opened!")
else:
    error("Cant open '.config' file :(", True)

info("Compiling AOPM API...")
api_try = sub.run(["python3", "-m", "build", "src/lib/api/aopmAPI", "--outdir", "compile"], stdout=sub.DEVNULL, stderr=sub.DEVNULL)
if api_try.returncode == 0:
    success("AOPM API compiled!")
else:
    error(f"Something went wrong :(. Exit code: {api_try.returncode}.", True)

info("Generating 'aopm' shortcut...")
shortcut_content = """#!/usr/bin/env bash
python3 /usr/share/aopm/core.py "$@"
"""
with open("compile/aopm", "w") as f:
    f.write(shortcut_content)

for line in config_content.splitlines():
    if line.startswith("with-aopkg"):
        aopkg_line = line.split("=")
        match aopkg_line[1].strip().lower():
            case "true":
                info("Generating 'aopkg' shortcut...")
                shortcut_content = """#!/usr/bin/env bash
python3 /usr/share/aopm/aopkg.py "$@"
"""
                with open("compile/aopkg", "w") as f:
                    f.write(shortcut_content)
                success("'aopkg' shortcut generated!")
            case "false":
                info("Skipping 'aopkg' shortcut generation...")
            case _:
                error("Invalid value for 'with-aopkg' in .config file :(", True)

aopm_conf_content = None
with open("configs/aopm.conf", "r") as f:
    lines_to_write = []
    for line in f.read().splitlines():
        if line == "[Paths]":
            pass
        else:
            lines_to_write.append(line)
    aopm_conf_content = "\n".join(lines_to_write)

if aopm_conf_content:
    info("Writing 'install.config'...")
    with open("install.config", "w") as f:
        f.write(aopm_conf_content)
        success("'install.config' created!")
else:
    error("Cant open: 'configs/aopm.conf' :(", True)

success("Everything looks done!")
info("For install AOPM use 'make install' or 'python3 install.py install.config'")
sys.exit(0)