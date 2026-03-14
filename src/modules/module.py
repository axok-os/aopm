"""

AOPM module Module
Version: 1.0.0
Made by: GusDev

"""

# libs
# -----
#   All the libs that the module will use

import aopmAPI as aopm
import importlib.util
import os
from pathlib import Path as p

# the API Header

header = {
    "name": "module",
    "version": "1.0.0",
    "description": "show infos about modules.",
    "author": "GusDev",
    "author_email" : "axok.os.team@gmail.com",
    "api_version": "1.0.0"
}

def get_header() -> dict:
    """
    Return the API Module Header.

    :return dict:
    """

    return header

def run(parameters: list, *args) -> int:
    """
    Run the module.

    :param parameters: The parameters that will be passed to the module
    :type parameters: dict
    """
    
    # simplify the parameters
    
    argc = len(parameters)
    argv = parameters

    if argc < 1:
        aopm.error("Too few arguments :(", True)

    match argv[0]:
        case "info":
            if argc < 2:
                aopm.error("No module to found specified :(", True)
            else:
                module_to_get_info = argv[1]

            path_to_search = f"{args[0]}/{module_to_get_info}.py"
            spec = importlib.util.spec_from_file_location(module_to_get_info, path_to_search)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)

            if hasattr(module, "get_header"):
                module_header = module.get_header()
            else:
                aopm.error(f"The module: '{module_to_get_info}' dont have the function get_header :(", True)
            
            print("Module Info:")
            print("-------------")
            for key, value in module_header.items():
                print(f"{str(key).replace("_", " ").title()}: {str(value).replace("_", " ")}")
        
        case "show":
            print("Modules Found:")
            print("---------------")
            for module in p(args[0]).iterdir():
                if module.is_file():
                    print(module.stem)
        
        case "create":
            if argc < 2:
                aopm.error("No module to create specified :(", True)
            else:
                module_to_create = argv[1]

            module_preset = """# libs:
# ------
#   All the libs that the module will use

import json
import aopmAPI as aopm
import os
from pathlib import Path as p


# The API Header
header = {
    "name": "module",
    "version": "1.0.0",
    "description": "Your module description.",
    "author": "Your Name",
    "author_email": "your.email@here.com",
    "api_version": "1.0.0"
}

# return the API Header
def get_header() -> dict:
    return header

# the core will run this
def run(parameters: list, *args) -> int:
    pass

# display your custom help message
def help():
    pass
"""
            with open(f"{args[0]}/{module_to_create}.py", "w", encoding="utf-8") as f:
                f.write(module_preset)
            
            print("Module created!")


def help():
    print("""
Module module:
---------------
    Create modules, view all modules, get info about modules

Usage:
-------
    aopm module show - Display all found modules
    aopm module info [MODULE] - Display the API header from the specified module

""")