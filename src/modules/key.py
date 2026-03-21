"""

AOPM key Module
Version: 1.0.0
Made by: GusDev

"""

#libs
import os
from pathlib import Path as p
import subprocess as sub
import aopmAPI as aopm
import gnupg
import tempfile
import json

# API header
header = {
    "name": "key",
    "version": "1.0.0",
    "description": "install, remove and see infos about your GPG keys",
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

    if argc < 2:
        aopm.error("Too few arguments :(", True)
    else:
        method = argv[0]
        key_to_check = argv[1]
        keys_path = args[3]
    
    aopm.info("Creating Temporary GPG home...")
    with tempfile.TemporaryDirectory() as tmp:
        aopm.success("Temporary GPG home created!")
        gpg = gnupg.GPG(homedir=tmp)
        match method:
            case "info":
                aopm.info("Searching for the specified key...")
                found = False
                for key_file in p(keys_path).iterdir():
                    if key_file.is_dir():
                        if key_file.name == key_to_check:
                            if (key_file / "key.asc").is_file():
                                aopm.success("Key found! Opening...")
                                found = True
                                key_content = None
                                with open(f"{key_file}/key.asc", "r") as f:
                                    key_content = f.read()
                                
                                if key_content:
                                    aopm.info("Importing key...")
                                    gpg.import_keys(key_content)
                                    aopm.success("Key imported!")
                                else:
                                    aopm.error("Cant open key file :(", True)
                            else:
                                aopm.warn("Empty directory found in keys directory.")
                        else:
                            continue
                    else:
                        aopm.warn("File found in keys directory.")
                    
                    if found:
                        break
                
                if found:
                    if "--full" in argv:
                        sub.run(["clear"])
                        print("Key Info:")
                        print("-" * 30)
                        for k in gpg.list_keys():
                            for key,value in k.items():
                                print(f"{key}: {value}")
                        print("-" * 30)
                        return 0
                    else:
                        sub.run(["clear"])
                        key_manifest_content = json.load(open(f"{keys_path}/{key_to_check}/aopkey.json", "r"))
                        print("Key Info:")
                        print("-" * 30)
                        for key in key_manifest_content:
                            print(f"{str(key).title().replace("-", " ").replace("_", " ")}: {key_manifest_content[key]}")
                        print("-" * 30)
                        return 0
                else:
                    aopm.error(f"Cant found key: '{key_to_check}' :(", True)

            case "remove":
                aopm.info("Searching for the specified key...")
                found = False
                for key_file in p(keys_path).iterdir():
                    if key_file.is_dir():
                        if key_file.name == key_to_check:
                            if (key_file / "key.asc").is_file():
                                aopm.success("Key found!")
                                if "--full" in argv:
                                    key_content = None
                                    with open(f"{key_file}/key.asc", "r") as f:
                                        key_content = f.read()
                                    
                                    if key_content:
                                        aopm.success("Importing key...")
                                        gpg.import_keys(key_content)
                                    else:
                                        aopm.error("Cant open the key file :(", True)
                                found = True
                            else:
                                aopm.warn("Empty directory found in keys directory.")
                        else:
                            continue
                    else:
                        aopm.warn("File found in keys directory.")

                    if found:
                        break
                
                if found:
                    if "--full" in argv:
                        sub.run(["clear"])
                        print("Key Info:")
                        print("-" * 30)
                        for k in gpg.list_keys():
                            for key, value in k.items():
                                print(f"{key}: {value}")
                        
                        print("-" * 30)
                    else:
                        key_manifest_content = json.load(open(f"{keys_path}/{key_to_check}/aopkey.json", "r"))
                        sub.run(["clear"])
                        for key in key_manifest_content:
                            print(f"{str(key).title().replace("-", " ").replace("_", " ")}: {key_manifest_content[key]}")
                        print("-" * 30)
                        print("after removal, this key will NOT be automatically reinstalled.")
                    
                    # get confirm
                    user_confirm = None
                    while user_confirm == None:
                        user_input = input(f"Want remove key: '{key_to_check}'[y/N]: ").strip()
                        if user_input.lower() == "":
                            aopm.warn("No option found. Using preset: 'False'...")
                            user_confirm = False
                        else:
                            match user_input.lower():
                                case "y"|"yes":
                                    user_confirm = True
                                case"n"|"no":
                                    user_confirm = False
                                case _:
                                    aopm.error("Invalid option :(. Try again.")
                                    continue
                    
                    match user_confirm:
                        case True:
                            aopm.info("Removing key...")
                            os.remove(f"{keys_path}/{key_to_check}")
                            aopm.success("Key removed!")
                            return 0
                        case False:
                            aopm.info("User canceled. Aborting...")
                            return 1

            case _:
                aopm.error("Invalid operation :(. Try use 'aopm help module key'.", True)



def help():
    print("""
key Module:
------------
    Remove and see infos about an specified key.
Examples:
----------
    aopm key info aopm - Display infos about the key 'aopm'
    aopm key remove aopm - Remove the key 'aopm'
        Note: After removal, this key will NOT be automatically installed.
""")