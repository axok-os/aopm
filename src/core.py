"""

AOPM (Axok!_OS Package Manager) Core
Version: 1.0.0
Made by: GusDev

"""

# libs
# -----
#   All the libs that the AOPM will use

import sys
import subprocess as sub
from pathlib import Path as p
import importlib.util
from configparser import ConfigParser
import os

# try import the AOPM API
import aopmAPI

# global variables
# -----------------
#   All the variables that will be used
#   ex: config = /etc

# where the config folder are
# NOTE: this probably will be changed with the "configure" command
config_path = "/home/gustavo/Projetos/axok-os/aopm/configs"

# the config file
config_file = f"{config_path}/aopm.conf"

# the essential sections of the config file
essential_sections = [
    "Paths",
]

# read the configs file
conf = ConfigParser()
conf.read(config_file)

# check the sections
for section in essential_sections:
    if conf.has_section(section):
        pass
    else:
        aopmAPI.error(f"The config file dont have the section: '{section}' :(", True)

# get the variables from config file
modules_path = conf.get("Paths", "modules_path")

# check if the user is root
if os.geteuid() != 0:
    aopmAPI.error("To run AOPM you must be root :(", True)

# check the arguments
argc = len(sys.argv)
if argc < 2:
    aopmAPI.error("Too few arguments :(\nTry: aopm help", True)

# define the module and parameters

# the module that will be found
module_to_search = sys.argv[1]

# the parameter that will be passed to the module
parameters_to_module = sys.argv[2:]

# the path that the module probably will be
path_to_search = f"{modules_path}/{module_to_search}.py"

spec = importlib.util.spec_from_file_location(f"{module_to_search}", path_to_search)
module = importlib.util.module_from_spec(spec)
try:
    spec.loader.exec_module(module)
except FileNotFoundError:
    aopmAPI.error(f"No Module named: '{module_to_search}' found :(", True)

if hasattr(module, "get_header"):
    module_header = module.get_header()
else:
    aopmAPI.error(f"The module: '{module_to_search}' dont have the get_header function :(", True)

module_reader = aopmAPI.Api_header(module_header)
if module_reader.check():
    if hasattr(module, "run"):
        module.run(parameters_to_module, modules_path)
    else:
        aopmAPI.error(f"The module: '{module_to_search}' dont have the run function :(", True)
else:
    print("vish")