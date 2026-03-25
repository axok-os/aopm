"""

AOPM installer script
Version: 1.0.0
Made by: GusDev

"""

#libs
import os
import subprocess as sub
from pathlib import Path as p
import sys
from time import sleep as s
import shutil

# print defs
def info(msg: str = "message"):
    s(0.1)
    print(f"\033[36m[INFO]\033[0m: {msg}")

def success(msg: str = "mesasge"):
    s(0.1)
    print(f"\033[32m[SUCCESS]\033[0m: {msg}")

def warn(msg: str = "message"):
    s(0.1)
    print(f"\033[33m[WARNING]\033[0m: {msg}")

def error(msg: str = "message", exit_: bool = False):
    s(0.1)
    print(f"\033[31m[ERROR]\033[0m: {msg}")
    if exit_:
        sys.exit(1)

# simplify arguments
argc = len(sys.argv)
argv = sys.argv

if os.geteuid() != 0:
    error("To install AOPM you must be root!", True)


if argc < 2:
    error("Too few arguments :(", True)

config_path = argv[1]
if p(config_path).is_file():
    pass
else:
    error("The specified .config file is a directory or does not exist :(", True)

info("Opening: 'install.config'...")
install_config_content = None
with open(config_path, "r") as f:
    install_config_content = f.read()

if install_config_content:
    success("'install.config' opened!")
else:
    error("Cant open 'install.config' file :(", True)

# install variables
repos_path = None
modules_path = None
repos_index_path = None
keys_path = None
packages_path = None

# .config variables
prefix = None
config_dir = None
var_dir = None

for line in install_config_content.strip().lower().splitlines():
    if line.startswith("repos_path"):
        repos_path = line.split("=")[1].strip()
    elif line.startswith("modules_path"):
        modules_path = line.split("=")[1].strip()
    elif line.startswith("repos_index_path"):
        repos_index_path = line.split("=")[1].strip()
    elif line.startswith("keys_path"):
        keys_path = line.split("=")[1].strip()
    elif line.startswith("packages_path"):
        packages_path = line.split("=")[1].strip()

variables = [repos_path, modules_path, repos_index_path, keys_path, packages_path]

if None in variables:
    error("Some variable is not set in 'install.config' :(", True)

info("Importing '.config' file...")
config_content = None
with open(".config", "r") as f:
    config_content = f.read()

if config_content:
    success("'.config' opened!")
else:
    error("Cant open '.config' file :(", True)

for line in config_content.strip().lower().splitlines():
    if line.startswith("with-aopkg"):
        aopkg_line = line.split("=")
        aopkg = aopkg_line[1].lower().strip()
    elif line.startswith("config-dir"):
        config_dir = line.split("=")[1].strip()
    elif line.startswith("var-dir"):
        var_dir = line.split("=")[1].strip()
    elif line.startswith("prefix"):
        prefix = line.split("=")[1].strip()

config_variables = [aopkg, config_dir, var_dir, prefix]

if None in config_variables:
    error("Some variable is not set in '.config' :(", True)

if aopkg not in ["true", "false"]:
    error(f"Invalid option for: 'with-aopkg': {aopkg} :(", True)

sub.run(["clear"])
print("Package Detected:")
print("-" * 30)
print(f"""Name: AOPM (Axok!_OS Package Manager)
Version: 1.0.0
Description: AOPM (Axok!_OS Package Manager) is a simple and direct package manager made for Axok!_OS
With AOPKG: {aopkg}
Author: Axok!_OS Team
Author Email: axok.os.team@gmail.com
License: GPL-2.0""")
print("-" * 30)

print(prefix)

# confirm
user_confirm = None
while user_confirm == None:
    user = input("Want install this package?[y/N]: ").lower().strip()
    if user == "":
        warn("No option found. Using preset: 'False'...")
        user_confirm = False
    else:
        match user:
            case "y" | "yes":
                user_confirm = True
            case "n" | "no":
                user_confirm = False
            case _:
                error("Invalid option :(")
                continue

base_dir = p(__file__).resolve().parent

match user_confirm:
    case True:
        info("Installing AOPM...")
        info("Creating main directories...")
        main_dirs = [
            f"{prefix}/share/aopm",
            f"{prefix}/share/aopm/repos",
            f"{prefix}/share/aopm/modules",
            f"{prefix}/share/aopm/keys",
            f"{prefix}/lib/aopm",
            f"{prefix}/lib/aopm/repos",
            var_dir,
            f"{var_dir}/aopm/packages",
            config_dir
        ]

        for directory in main_dirs:
            if p(directory).exists():
                warn(f"Directory: '{directory}' already exists.\nThis may cause fails.")
            else:
                os.makedirs(directory, exist_ok=True)
                success(f"Directory: '{directory}' created!")
        
        success("All main directories created!")
        info("Copying files...")
        # cory core
        info("Copying core...")
        shutil.copy(f"{base_dir}/compile/aopm", f"{prefix}/bin/aopm")
        success("Core copied!")
        # check and install aopkg
        if aopkg == "true":
            info("Copying AOPKG...")
            shutil.copy(f"{base_dir}/compile/aopkg", f"{prefix}/bin/aopkg")
            success("AOPKG copied!")
        # install modules
        info("Copying modules...")
        for module in p(f"{base_dir}/src/modules").iterdir():
            if module.is_file() and module.suffix == ".py":
                shutil.copy(module, f"{prefix}/share/aopm/modules/{module.name}{module.suffix}")
                success(f"Module: '{module.name}' copied!")
        
        success("All modules copied!")

        info("Copying config file...")
        shutil.copy(f"{base_dir}/configs/aopm.conf", f"{config_dir}/aopm.conf")
        success("Config file copied!")

        info("Copying repositories...")
        for repo in p(f"{base_dir}/repos").iterdir():
            if repo.is_dir():
                shutil.copytree(repo, f"{prefix}/share/aopm/repos/{repo.name}")
                success(f"Repository: '{repo.name}' copied!")
        success("All repositories copied!")

        info("Copying repositories indexes...")
        for repo_index in p(f"{base_dir}/lib/repos").iterdir():
            if repo_index.is_dir():
                shutil.copytree(repo_index, f"{prefix}/lib/aopm/repos/{repo_index.name}")
                success(f"Repository index: '{repo_index.name}' copied!")
        success("All repositories indexes copied!")

        info("Copyting keys...")
        for key in p(f"{base_dir}/keys").iterdir():
            if key.is_dir():
                shutil.copytree(key, f"{prefix}/share/aopm/keys/{key.name}")
                success(f"Key: '{key.name}' copied!")
        success("All keys copied!")

        info("Installing AOPM API...")
        if shutil.which("pip"):
            install_try = sub.run(["pip", "install", f"{base_dir}/compile/aopm_api-1.0.0-py3-none-any.whl"], capture_output=True)
            if install_try.returncode == 0:
                success("AOPM API installed!")
            else:
                error(f"Failed to install AOPM API :(. Exit code: {install_try.returncode}", True)
        else:
            error("Pip is not installed! Cant install AOPM API :(", True)
        
        success("AOPM installed successfully!")
    case False:
        info("User canceled. Aborting...")
        sys.exit(1)