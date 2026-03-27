"""

AOPM help Module
Version: 1.0.0
Made by: GusDev

"""

# libs
# -----
#   All the libs that the module will use

import importlib.util
from configparser import ConfigParser
import sys
from pathlib import Path as p
import aopmAPI

# the API Header
header = {
    "name": "help",
    "version": "1.0.0",
    "description": "print a help message.",
    "author": "GusDev",
    "author_email": "axok.os.team@gmail.com",
    "api_version": "1.0.0"
}

def get_header() -> dict:
    """
    Returns the API Header.

    :return dict:
    """
    return header

def run(parameters : list, modules_home: str, *args) -> int:
    """
    Run the module

    :param parameters: The parameter that will be passed to the module
    :type parameters: dict
    :param modules_home: The paths that all the modules are
    :type modules_home: str
    """

    # simplify the parameters
    argc = len(parameters)
    argv = parameters
    if argc < 1:
        aopmAPI.error("Too few arguments :(", True)
    # match the first parameter
    match argv[0]:
        case "me":
            print("""
AOPM Usage:
----------------------------------
aopm [Method/Nodule] [Parameters]
----------------------------------
Examples:
    aopm help me - Display this message
    aopm help module (module name) - Display help for the specified module
""")
            return 0
        case "module":
            if argc < 2:
                aopmAPI.error("You need to specify the module to get help :(", True)
            else:
                module_to_get_help = argv[1]
            path_to_search = f"{modules_home}/{module_to_get_help}.py"
            spec = importlib.util.spec_from_file_location(module_to_get_help, path_to_search)
            module = importlib.util.module_from_spec(spec)
            try:
                spec.loader.exec_module(module)
            except FileNotFoundError:
                aopmAPI.error(f"The module: '{module_to_get_help}' dont exist :(", True)

            if hasattr(module, "help"):
                module.help()
            else:
                aopmAPI.error(f"The module: '{module_to_get_help}' dont have the help function :(", True)

def help():
    print("""
Help Module:
-------------
    The help module display help messages of how to use modules or how to use AOPM.

Usage:
-------
    aopm help module help - Display this message
    aopm help me - Display a message of how to use AOPM
""")