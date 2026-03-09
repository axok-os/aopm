"""

AOPM install Module
Version: 1.0.0
Made by: GusDev

"""

# libs
# -----
#    All the libs that the module will use

import subprocess
import tarfile
import tempfile
import os
from pathlib import Path as p
import aopmAPI as aopm

# The API Header

header = {
    "name": "install",
    "version": "1.0.0",
    "description": "Install packages.",
    "author": "GusDev",
    "author_email": "axok.os.team@gmail.com",
    "api_version": "1.0.0"
}

def get_header() -> dict:
    """
    Return the API Header.

    :return dict:
    """

    return header

def run(parameters : list, *args):
    """
    Run the Module.

    :param parameters: The parameters that will be passed to the module
    :type parameters: list
    """

    # simplify the parameters

    argc = len(parameters)
    argv = parameters

    if argc < 1:
        aopm.error("Too few arguments :(", True)

    package_to_search = argv[0]

def help():
    print("""
Install Module:
----------------
    Install packages to the system.
    
Usage:
-------
    aopm install grub-efi - Install the package 'grub-efi' to the system
    aopm install firefox - Install the package 'firefox' to the system
""")