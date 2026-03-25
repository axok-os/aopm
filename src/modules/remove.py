"""

AOPM remove Module
Version: 1.0.0
Made by: GusDev

"""

# libs
import subprocess as sub
import os
import shutil
from pathlib import Path as p
import json
import aopmAPI as aopm

# API header
header = {
    "name": "remove",
    "version": "1.0.0",
    "description": "Remove packages.",
    "author": "GusDev",
    "author_email": "axok.os.team@gmail.com",
    "api_version": "1.0.0"
}

def get_header() -> dict:
    """
    
    Return the API Header.
    
    """
    return header

def run(parameters: list, *args) -> bool:
    argc = len(parameters)
    argv = parameters
    
    if argc < 1:
        aopm.error("Too few arguments :(", True)
    else:
        package_to_search = argv[0]
        packages_path = args[4]

        aopm.info("Searching for the package...")
        found = False
        for pkg_file in p(packages_path).iterdir():
            if pkg_file.is_dir():
                if pkg_file.name == package_to_search:
                    aopm.success("Package found!")
                    found = True
                else:
                    pass
            else:
                aopm.warn("File found in packages directory")
            
            if found:
                break
        
        if found:
            pass
        else:
            aopm.error(f"Cant found the package: '{package_to_search}' :(", True)
        
        aopm.info("Opening files...")
        file_list_content = None
        aopkg_content = None
        try:
            with open(f"{packages_path}/{package_to_search}/file-list", "r") as f:
                file_list_content = f.read()
        except FileNotFoundError:
            aopm.error("Cant found the file: 'file-list' :(", True)
        try:
            aopkg_content = json.load(open(f"{packages_path}/{package_to_search}/aopkg.json", "r"))
        except FileNotFoundError:
            aopm.error("Cant found file: 'aopkg.json' :(", True)
        
        if file_list_content:
            pass
        else:
            aopm.error("Cant open the file 'file-list' :(", True)
        
        if aopkg_content:
            pass
        else:
            aopm.error("Cant open the file: 'aopkg.json' :(", True)
        
        print("\n")
        print("Package Detected!")
        print("-" * 30)
        for key in aopkg_content:
            print(f"{str(key).title().replace("-", " ").replace("_", " ")}: {aopkg_content[key]}")
        print("-" * 30)

        # get confirm
        user_confirm = None
        if "--force" in argv:
            user_confirm = True
        else:
            while user_confirm == None:
                user_input = input("Want remove this package?[y/N]: ").strip().lower()
                if user_input == "":
                    aopm.warn("No option found. Using preset: 'False'...")
                else:
                    match user_input:
                        case "y"|"yes":
                            user_confirm = True
                        case "n"|"no":
                            user_confirm = False
                        case _:
                            aopm.error("Invalid option :(. Try again.")
                            continue
            match user_confirm:
                case True:
                    user_confirm_warn = None
                    if "--no-warn" in argv:
                        user_confirm_warn = True
                    else:
                        while user_confirm_warn == None:
                            print("This package may remove dependencies required by other packages. Proceed at your own risk.")
                            user_input = input(f"Want remove the package '{package_to_search}'?[y/N]: ").strip().lower()
                            if user_input == "":
                                aopm.warn("No option found. Using preset: 'False'...")
                                user_confirm_warn = False
                            else:
                                match user_input:
                                    case "y"|"yes":
                                        user_confirm_warn = True
                                    case "n"|"no":
                                        user_confirm_warn = False
                                    case _:
                                        aopm.error("Invalid option :(. Try again.")
                                        continue
                        match user_confirm_warn:
                            case True:
                                pass
                            case False:
                                aopm.info("User canceled. Aborting...")
                                return 1
                case False:
                    aopm.info("User canceled. Aborting...")
                    return 1
        
        aopm.info("Removing package...")
        for file_or_dir in reversed(file_list_content.splitlines()):
            if p(file_or_dir).is_dir():
                try:
                    os.rmdir(file_or_dir)
                except OSError:
                    pass
            else:
                os.remove(file_or_dir)
        aopm.info("Removing from: 'installed packages'...")
        shutil.rmtree(f"{packages_path}/{package_to_search}")
        aopm.success("Package removed!")
        aopm.success("Everythig looks done!")
        return 0

def help():
    print("""
remove Module:
---------------
    Remove an package.
Examples:
----------
    aopm remove aopkg - Remove the package 'aopkg'
    aopm remove fakeroot --force - Remove the package 'fakeroot' with no questions
""")